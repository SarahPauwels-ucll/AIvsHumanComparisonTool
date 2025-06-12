import os
import numpy as np
import cv2
from shapely.geometry import Polygon
from ultralytics import YOLO


# -------- 1.  LOAD YOLO .TXT GROUND-TRUTH  -----------------------------------
def load_ground_truth_yolo(txt_path: str, image_path: str):
    """
    Reads a YOLO-format .txt annotation file and returns polygons in ABSOLUTE
    pixel coordinates.

    • Segmentation rows ........ class  x1 y1 x2 y2 ...  (all normalised 0-1)
    • Bounding-box rows ........ class  xc yc w h        (normalised 0-1)

    Returns
    -------
    polygons : list[Polygon]
    width    : int
    height   : int
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")
    h,  w  = img.shape[:2]

    polygons = []
    with open(txt_path, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 5:                 # need ≥ class + 2 coords
                continue

            coords = list(map(float, parts[1:]))  # drop class id

            # --- bbox line: xc yc w h -------------
            if len(coords) == 4:
                xc, yc, bw, bh = coords
                x_min = (xc - bw / 2) * w
                y_min = (yc - bh / 2) * h
                x_max = (xc + bw / 2) * w
                y_max = (yc + bh / 2) * h
                pts   = [(x_min, y_min), (x_max, y_min),
                         (x_max, y_max), (x_min, y_max)]

            # --- segmentation line: x1 y1 x2 y2 ... -------------
            else:
                if len(coords) % 2:             # odd number → malformed
                    continue
                pts = [(coords[i] * w, coords[i + 1] * h)
                       for i in range(0, len(coords), 2)]

            # optional: filter out perfectly axis-aligned rectangles
            if len(pts) == 4:
                xs, ys = {p[0] for p in pts}, {p[1] for p in pts}
                if len(xs) <= 2 and len(ys) <= 2:
                    continue

            polygons.append(Polygon(pts))

    return polygons, w, h


# -------- 2.  REMAINING UTILITY FUNCTIONS  ----------------------------------
def compute_iou(poly1, poly2):
    if not poly1.is_valid or not poly2.is_valid:
        return 0.0
    inter = poly1.intersection(poly2).area
    union = poly1.union(poly2).area
    return inter / union if union else 0.0


def run_inference(model_path, image_path):
    model   = YOLO(model_path)
    result  = model(image_path)[0]
    h, w    = result.orig_shape[:2]

    predicted_polys = []
    for mask in result.masks.xy:
        if len(mask) == 4:                      # skip box-shaped masks
            xs, ys = {p[0] for p in mask}, {p[1] for p in mask}
            if len(xs) <= 2 and len(ys) <= 2:
                continue
        predicted_polys.append(Polygon(mask))

    return predicted_polys, w, h, result.orig_img


def draw_polygons(img, gt_polys, pred_polys):
    out = img.copy()
    overlay = img.copy()
    opacity = 0.4

    if gt_polys:
        for p in gt_polys:
            cv2.polylines(out, [np.int32(p.exterior.coords)], True, (0, 255, 0), 2)

    if pred_polys:
        for p in pred_polys:
            pts = np.int32([p.exterior.coords])
            cv2.fillPoly(overlay, pts, (255, 0, 255))

    out = cv2.addWeighted(overlay, opacity, out, 1 - opacity, 0)
    return out


# -------- 3.  MAIN -----------------------------------------------------------
if __name__ == "__main__":
    # === CONFIG ===
    base_path = "C:/Users/Jarne/Documents/yolo_dataset_segmentation_extra_data_bone_seg_splits/"
    image_end_path = "images/test/32_1_aug_000.jpg"
    txt_end_path   = "labels/test/32_1_aug_000.txt"      # <-- YOLO label file
    model_path = "runs/bone_segmentation/train/weights/best.pt"
    output_path = "comparison_output.jpg"

    # === RUN ===
    image_path = base_path + image_end_path
    txt_path   = base_path + txt_end_path

    pred_polys, w_pred, h_pred, img = run_inference(model_path, image_path)
    gt_polys,   w_gt,   h_gt        = load_ground_truth_yolo(txt_path, image_path)

    if (w_pred, h_pred) != (w_gt, h_gt):
        raise ValueError("[ERROR] Image dimensions mismatch.")

    # print(f"GT polygons: {len(gt_polys)}, Predictions: {len(pred_polys)}")
    # for i, gt in enumerate(gt_polys, 1):
    #     best_iou = max((compute_iou(gt, p) for p in pred_polys), default=0.0)
    #     print(f"GT Polygon {i}: Best IoU = {best_iou:.4f}")

    # === DRAW & SAVE ===
    vis = draw_polygons(img, gt_polys=None, pred_polys=pred_polys)
    cv2.imwrite(output_path, vis)