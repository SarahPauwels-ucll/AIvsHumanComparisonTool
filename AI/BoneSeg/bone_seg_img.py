import io
import os
import numpy as np
import cv2
from PIL import Image
from shapely.geometry import Polygon
from shapely.geometry.multipolygon import MultiPolygon
from shapely.validation import explain_validity
from ultralytics import YOLO

from AI.augmented_data_to_splits import OUTPUT_DIR


# -------- 1.  LOAD YOLO .TXT GROUND-TRUTH  -----------------------------------
def load_ground_truth_yolo(txt_path: str, image_path: str):
    """
    Reads a YOLO-format .txt annotation file and returns polygons in ABSOLUTE
    pixel coordinates along with their class IDs.

    Returns
    -------
    polygons : list[Polygon]
    classes  : list[int]     # added: list of class IDs corresponding to polygons
    width    : int
    height   : int
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")
    h, w = img.shape[:2]

    polygons = []
    classes = []
    with open(txt_path, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 5:  # need ≥ class + 2 coords
                continue

            class_id = int(parts[0])  # get class id
            coords = list(map(float, parts[1:]))

            # bbox line: xc yc w h
            if len(coords) == 4:
                xc, yc, bw, bh = coords
                x_min = (xc - bw / 2) * w
                y_min = (yc - bh / 2) * h
                x_max = (xc + bw / 2) * w
                y_max = (yc + bh / 2) * h
                pts = [(x_min, y_min), (x_max, y_min),
                       (x_max, y_max), (x_min, y_max)]

            # segmentation line: x1 y1 x2 y2 ...
            else:
                if len(coords) % 2:
                    continue
                pts = [(coords[i] * w, coords[i + 1] * h) for i in range(0, len(coords), 2)]

            if len(pts) == 4:
                xs, ys = {p[0] for p in pts}, {p[1] for p in pts}
                if len(xs) <= 2 and len(ys) <= 2:
                    continue

            poly = Polygon(pts).buffer(0)
            if not poly.is_valid:
                poly = poly.buffer(0)
            polygons.append(poly)
            classes.append(class_id)

    return polygons, classes, w, h


# -------- 2.  REMAINING UTILITY FUNCTIONS  ----------------------------------
def compute_iou(poly1, poly2):

    if not poly1.is_valid:
        print("GT polygon invalid:", explain_validity(poly1))
    if not poly2.is_valid:
        print("Pred polygon invalid:", explain_validity(poly2))

    if not poly1.is_valid or not poly2.is_valid:
        print("SnoopyPoopy")
        return 0.0

    poly1 = poly1.buffer(0)
    poly2 = poly2.buffer(0)

    # ------------------------------------------

    inter = poly1.intersection(poly2).area
    union = poly1.union(poly2).area
    return inter / union if union else 0.0


MODEL_PATH: str = "AI/models/yolo11m_bone_segmentation_finetuned.pt"


def get_bone_level(image_bytes):
    model = YOLO(MODEL_PATH)

    if isinstance(image_bytes, bytes):
        pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img = np.array(pil_image)
    else:
        raise TypeError("image_bytes must be a bytes object")

    result = model.predict(
        source=img,
        verbose=False,
        retina_masks=True,
        imgsz=1024,
    )[0]

    predicted_polys = []
    for mask in result.masks.xy:
        if len(mask) == 4:  # skip box-shaped masks
            xs, ys = {p[0] for p in mask}, {p[1] for p in mask}
            if len(xs) <= 2 and len(ys) <= 2:
                continue
        poly = Polygon(mask)
        poly = poly.buffer(0)
        if not poly.is_valid:
            poly = poly.buffer(0)
        predicted_polys.append(poly)

    #pil_image = Image.open(io.BytesIO(image_bytes))
    image_with_bone = draw_polygons(img, [], predicted_polys)
    img_bgr = cv2.cvtColor(image_with_bone, cv2.COLOR_RGB2BGR)
    success, buf = cv2.imencode(".png", img_bgr)
    if not success:
        raise RuntimeError("Failed to encode result image")

    img_bytes: bytes = buf.tobytes()
    return img_bytes


def run_inference(model_path, image_path):
    model = YOLO(model_path)
    result = model(image_path)[0]
    h, w = result.orig_shape[:2]

    predicted_polys = []
    for mask in result.masks.xy:
        if len(mask) == 4:  # skip box-shaped masks
            xs, ys = {p[0] for p in mask}, {p[1] for p in mask}
            if len(xs) <= 2 and len(ys) <= 2:
                continue
        poly = Polygon(mask)
        poly = poly.buffer(0)
        if not poly.is_valid:
            poly = poly.buffer(0)
        predicted_polys.append(poly)

    return predicted_polys, w, h, result.orig_img


def draw_polygons(img, gt_polys, pred_polys):
    out = img.copy()
    overlay = img.copy()
    opacity = 0.4

    def draw(poly, color):
        if isinstance(poly, Polygon):
            contours = [np.int32(poly.exterior.coords).reshape((-1, 1, 2))]
        elif isinstance(poly, MultiPolygon):
            contours = [np.int32(p.exterior.coords).reshape((-1, 1, 2)) for p in poly.geoms]
        else:
            return  # unsupported geometry

        for cnt in contours:
            cv2.fillPoly(overlay, [cnt], color)

    # Don't draw ground truth polygons
    # for p in gt_polys:
    #     draw(p, (0, 255, 0))  # previously green for ground truth

    # Draw predicted polygons in green
    for p in pred_polys:
        draw(p, (0, 255, 0))  # green = prediction

    out = cv2.addWeighted(overlay, opacity, out, 1 - opacity, 0)
    return out
def predict_and_save(image_path, model_path, output_path=OUTPUT_DIR):
    """
    Runs prediction on a single image, draws predicted polygons, saves and optionally shows the result.

    Parameters
    ----------
    image_path : str
        Path to the input image.
    model_path : str
        Path to the YOLO model.
    output_path : str or None
        Path to save the output image. If None, saves in same directory as input with '_pred' suffix.
    show : bool
        Whether to display the image using matplotlib.
    """
    # Run inference
    pred_polys, w, h, img = run_inference(model_path, image_path)

    # Draw only predicted polygons
    vis = draw_polygons(img, gt_polys=[], pred_polys=pred_polys)

    # Prepare output path
    if output_path is None:
        dir_name, file_name = os.path.split(image_path)
        name, ext = os.path.splitext(file_name)
        output_path = os.path.join(dir_name, name + "_pred" + ext)

    # Save the image
    cv2.imwrite(output_path, vis)
    print(f"[INFO] Saved prediction image to: {output_path}")
def average_iou_for_folder(image_folder, label_folder, model_path):
    max_iou_scores_mandible = []
    max_iou_scores_maxilla = []

    image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]

    for img_file in image_files:
        base_name = os.path.splitext(img_file)[0]
        img_path = os.path.join(image_folder, img_file)
        label_path = os.path.join(label_folder, base_name + ".txt")

        if not os.path.isfile(label_path):
            print(f"[WARNING] Label file missing for image {img_file}, skipping.")
            continue

        pred_polys, w_pred, h_pred, img = run_inference(model_path, img_path)
        gt_polys, gt_classes, w_gt, h_gt = load_ground_truth_yolo(label_path, img_path)

        if (w_pred, h_pred) != (w_gt, h_gt):
            print(f"[ERROR] Dimension mismatch for {img_file}, skipping.")
            continue

        if len(gt_polys) == 0 or len(pred_polys) == 0:
            print(f"[WARNING] No polygons found in GT or predictions for {img_file}, skipping.")
            continue

        max_iou_mandible_img = 0.0
        max_iou_maxilla_img = 0.0
        has_mandible = False
        has_maxilla = False

        # If exactly two GT and two predicted polygons, try both assignments and pick best
        if len(gt_polys) == 2 and len(pred_polys) == 2:
            # Compute IoU for original assignments
            iou_00 = compute_iou(gt_polys[0], pred_polys[0])
            iou_11 = compute_iou(gt_polys[1], pred_polys[1])
            sum_orig = iou_00 + iou_11

            # Compute IoU for swapped assignments
            iou_01 = compute_iou(gt_polys[0], pred_polys[1])
            iou_10 = compute_iou(gt_polys[1], pred_polys[0])
            sum_swapped = iou_01 + iou_10

            if sum_swapped > sum_orig:
                assigned = [(gt_polys[0], pred_polys[1], gt_classes[0]),
                            (gt_polys[1], pred_polys[0], gt_classes[1])]
                print(f"{img_file}: Using swapped predicted polygons for better matching.")
            else:
                assigned = [(gt_polys[0], pred_polys[0], gt_classes[0]),
                            (gt_polys[1], pred_polys[1], gt_classes[1])]
                print(f"{img_file}: Using original predicted polygon assignments.")

            # For each pair, update max IoU per class
            for gt_poly, pred_poly, gt_cls in assigned:
                iou = compute_iou(gt_poly, pred_poly)
                if gt_cls == 0:
                    has_mandible = True
                    if iou > max_iou_mandible_img:
                        max_iou_mandible_img = iou
                else:
                    has_maxilla = True
                    if iou > max_iou_maxilla_img:
                        max_iou_maxilla_img = iou

        else:
            # For other cases, match polygons by index (fallback)
            for i, gt_poly in enumerate(gt_polys):
                if i >= len(pred_polys):
                    continue
                pred_poly = pred_polys[i]
                iou = compute_iou(gt_poly, pred_poly)
                if gt_classes[i] == 0:
                    has_mandible = True
                    if iou > max_iou_mandible_img:
                        max_iou_mandible_img = iou
                else:
                    has_maxilla = True
                    if iou > max_iou_maxilla_img:
                        max_iou_maxilla_img = iou

        if has_mandible:
            max_iou_scores_mandible.append(max_iou_mandible_img)
        if has_maxilla:
            max_iou_scores_maxilla.append(max_iou_maxilla_img)

        print(f"{img_file}: Max Mandible IoU = {max_iou_mandible_img:.4f}, Max Maxilla IoU = {max_iou_maxilla_img:.4f}")

    avg_iou_mandible = sum(max_iou_scores_mandible) / len(max_iou_scores_mandible) if max_iou_scores_mandible else 0
    avg_iou_maxilla = sum(max_iou_scores_maxilla) / len(max_iou_scores_maxilla) if max_iou_scores_maxilla else 0

    print(f"\nFinal Average IoU for Mandible (class 0): {avg_iou_mandible:.4f}")
    print(f"Final Average IoU for Maxilla (others): {avg_iou_maxilla:.4f}")

    return avg_iou_mandible, avg_iou_maxilla


# -------- 3.  MAIN -----------------------------------------------------------
if __name__ == "__main__":
    # === CONFIG ===
    base_path = ""
    image_end_path = "AI/output/segmentation_v2_test_unlabeled/pred_case_1.jpeg"
    txt_end_path   = "yolo_dataset_segmentation_extra_data_bone_seg_splits/labels/test/104_1_aug_001.txt"      # <-- YOLO label file
    model_path = "AI/models/yolo11m_bone_segmentation_finetuned.pt"
    output_path = "comparison_output.jpg"

    # === RUN ===
    image_path = base_path + image_end_path
    txt_path   = base_path + txt_end_path

    pred_polys, w_pred, h_pred, img = run_inference(model_path, image_path)
    gt_polys, classes,  w_gt,   h_gt        = load_ground_truth_yolo(txt_path, image_path)

    if (w_pred, h_pred) != (w_gt, h_gt):
        raise ValueError("[ERROR] Image dimensions mismatch.")

    print(f"GT polygons: {len(gt_polys)}, Predictions: {len(pred_polys)}")

    if len(gt_polys) == 2 and len(pred_polys) == 2:
        # Compute IoU for (GT0, Pred0) and (GT1, Pred1)
        iou_00 = compute_iou(gt_polys[0], pred_polys[0])
        iou_11 = compute_iou(gt_polys[1], pred_polys[1])

        # Compute IoU for swapped pairs (GT0, Pred1) and (GT1, Pred0)
        iou_01 = compute_iou(gt_polys[0], pred_polys[1])
        iou_10 = compute_iou(gt_polys[1], pred_polys[0])

        # Sum IoUs for both assignments
        sum_orig = iou_00 + iou_11
        sum_swapped = iou_01 + iou_10

        if sum_swapped > sum_orig:
            print(f"Swapping predicted polygons for better matching.")
            print(f"GT Polygon 1 matched with Pred Polygon 2 (IoU: {iou_01:.4f})")
            print(f"GT Polygon 2 matched with Pred Polygon 1 (IoU: {iou_10:.4f})")
        else:
            print(f"GT Polygon 1 matched with Pred Polygon 1 (IoU: {iou_00:.4f})")
            print(f"GT Polygon 2 matched with Pred Polygon 2 (IoU: {iou_11:.4f})")

    else:
        # For more polygons, do your existing matching or fallback logic
        for i, gt_poly in enumerate(gt_polys, 1):
            pred_poly = pred_polys[i - 1] if i - 1 < len(pred_polys) else None
            if pred_poly is not None:
                iou = compute_iou(gt_poly, pred_poly)
                print(f"GT Polygon {i} matched with Pred Polygon {i} (IoU: {iou:.4f})")

    # === DRAW & SAVE ===
    vis = draw_polygons(img, gt_polys, pred_polys)
    cv2.imwrite(output_path, vis)
    predict_and_save(image_path, model_path, output_path)


# if __name__ == "__main__":
#     base_path = "yolo_dataset_segmentation_extra_data_bone_seg_splits/"
#     image_folder = os.path.join(base_path, "images/test/")
#     label_folder = os.path.join(base_path, "labels/test/")
#     model_path = "AI/models/yolo11m_bone_segmentation_finetuned.pt"
#
#     print(f"Starting IoU evaluation on folder:\n Images: {image_folder}\n Labels: {label_folder}")
#     avg_iou_mandible, avg_iou_maxilla = average_iou_for_folder(image_folder, label_folder, model_path)
#     print(f"Final average IoU - Mandible: {avg_iou_mandible:.4f}")
#     print(f"Final average IoU - Maxilla: {avg_iou_maxilla:.4f}")