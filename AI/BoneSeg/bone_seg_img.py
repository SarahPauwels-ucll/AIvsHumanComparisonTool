import json
import os
import numpy as np
import cv2
from shapely.geometry import Polygon
from ultralytics import YOLO


def load_ground_truth(json_path):
    with open(json_path, "r") as f:
        data = json.load(f)
    h, w = data["imageHeight"], data["imageWidth"]
    polygons = []
    for shape in data["shapes"]:
        if shape["shape_type"] == "polygon":
            pts = shape["points"]
            if len(pts) == 4:
                x_coords = [p[0] for p in pts]
                y_coords = [p[1] for p in pts]
                if len(set(x_coords)) <= 2 and len(set(y_coords)) <= 2:
                    continue
            polygons.append(Polygon(pts))
    return polygons, w, h


def compute_iou(poly1, poly2):
    if not poly1.is_valid or not poly2.is_valid:
        return 0.0
    intersection = poly1.intersection(poly2).area
    union = poly1.union(poly2).area
    return intersection / union if union != 0 else 0.0


def run_inference(model_path, image_path):
    model = YOLO(model_path)
    results = model(image_path)[0]
    h, w = results.orig_shape[:2]
    predicted_polygons = []

    for mask in results.masks.xy:
        if len(mask) == 4:
            x_coords = [pt[0] for pt in mask]
            y_coords = [pt[1] for pt in mask]
            if len(set(x_coords)) <= 2 and len(set(y_coords)) <= 2:
                continue  # skip boxy predictions
        predicted_polygons.append(Polygon(mask))
    return predicted_polygons, w, h, results.orig_img


def draw_polygons(image, gt_polys, pred_polys):
    image_copy = image.copy()

    # Draw GT in green
    for poly in gt_polys:
        pts = np.array(poly.exterior.coords, np.int32)
        cv2.polylines(image_copy, [pts], isClosed=True, color=(0, 255, 0), thickness=2)

    # Draw predictions in red
    for poly in pred_polys:
        pts = np.array(poly.exterior.coords, np.int32)
        cv2.polylines(image_copy, [pts], isClosed=True, color=(0, 0, 255), thickness=2)

    return image_copy


# === CONFIG ===
image_path = "AI/Normal bone/1_1.jpg"
json_path = "AI/Normal bone/1_1.json"
model_path = "runs/segment/train6/weights/best.pt"  # replace with actual path
output_path = "comparison_output.jpg"

# === RUN ===
pred_polygons, w_pred, h_pred, orig_img = run_inference(model_path, image_path)
gt_polygons, w_gt, h_gt = load_ground_truth(json_path)

assert w_pred == w_gt and h_pred == h_gt, "[ERROR] Image dimensions mismatch."

print(f"GT polygons: {len(gt_polygons)}, Predictions: {len(pred_polygons)}")
for i, gt_poly in enumerate(gt_polygons):
    best_iou = 0.0
    for pred_poly in pred_polygons:
        iou = compute_iou(gt_poly, pred_poly)
        best_iou = max(best_iou, iou)
    print(f"GT Polygon {i + 1}: Best IoU = {best_iou:.4f}")

# === DRAW AND SAVE ===
result_img = draw_polygons(orig_img, gt_polygons, pred_polygons)
cv2.imwrite(output_path, result_img)
cv2.imshow("Comparison", result_img)
cv2.waitKey(0)
cv2.destroyAllWindows()
