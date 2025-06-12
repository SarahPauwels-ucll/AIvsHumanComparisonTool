# apply_yolo_masks_batch.py
# -------------------------
"""
Batch-runner that consumes YOLO-txt annotations and produces mask & overlay
images for an entire dataset split.  All configuration is done in-file.

Directory layout expected
=========================
<DATA_ROOT>/
  images/
    <SPLIT>/   ── *.jpg / *.png …
  labels/
    <SPLIT>/   ── *.txt          (YOLO format)

Outputs are written to:
<DATA_ROOT>/<OUT_REL>/<SPLIT>/   (created automatically)
"""
import os
import glob
import cv2
import numpy as np
from typing import Tuple

# ----------------------------------------------------------------------------- #
# CONFIGURATION ––– change these 3 variables and run the script as-is           #
# ----------------------------------------------------------------------------- #
DATA_ROOT = "yolo_dataset_segmentation_extra_data_splits" # ← absolute or relative path
SPLIT     = "test" # e.g. "train", "val", "test"
OUT_REL   = "output/segmentation_large" # sub-folder for results
# ----------------------------------------------------------------------------- #


# ———————————————————————————————————— 1. Per-image routine ——————————————————————————————————— #
def _relative_bbox_to_polygon(
    rel_xc: float, rel_yc: float, rel_w: float, rel_h: float, W: int, H: int
) -> np.ndarray:
    """Convert a relative YOLO bbox to a 4-point polygon in absolute pixels."""
    abs_w, abs_h = rel_w * W, rel_h * H
    x1, y1 = rel_xc * W - abs_w / 2, rel_yc * H - abs_h / 2
    x2, y2 = x1 + abs_w, y1 + abs_h
    return np.array([[x1, y1], [x2, y1], [x2, y2], [x1, y2]], dtype=np.float32)


def apply_yolo_mask_to_image(
    image_path: str,
    txt_path: str,
    output_path: str,
    mask_color: Tuple[int, int, int] = (0, 255, 0),
    overlay_alpha: float = 0.5,
):
    """Creates *masked-only* and *overlay* outputs for one image/label pair."""
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Could not read image at {image_path}")
    H, W = image.shape[:2]

    if not os.path.isfile(txt_path):
        print(f"[WARN] Missing label: {txt_path}")
        return

    binary_mask = np.zeros((H, W), dtype=np.uint8)

    with open(txt_path, "r") as f:
        for line in map(str.strip, f):
            if not line:
                continue
            parts = line.split()
            if len(parts) < 5:
                continue  # malformed

            nums = list(map(float, parts[1:]))

            if len(nums) == 4:
                # -------- Bounding box --------
                rel_xc, rel_yc, rel_w, rel_h = nums
                poly = _relative_bbox_to_polygon(rel_xc, rel_yc, rel_w, rel_h, W, H)
                pts = np.round(poly).astype(np.int32).reshape((-1, 1, 2))
                cv2.fillPoly(binary_mask, [pts], 255)
            else:
                # -------- Polygon --------
                if len(nums) % 2:
                    continue
                coords = np.array(nums, dtype=np.float32).reshape(-1, 2)
                coords[:, 0] *= W
                coords[:, 1] *= H
                pts = np.round(coords).astype(np.int32).reshape((-1, 1, 2))
                cv2.fillPoly(binary_mask, [pts], 255)

    # --- outputs -------------------------------------------------------- #
    base, ext = os.path.splitext(os.path.basename(image_path))
    os.makedirs(output_path, exist_ok=True)

    masked_only = cv2.bitwise_and(image, image, mask=binary_mask)
    cv2.imwrite(os.path.join(output_path, f"{base}_masked_only{ext}"), masked_only)

    color_layer = np.zeros_like(image)
    color_layer[:] = mask_color
    alpha = (binary_mask[..., None] / 255.0) * overlay_alpha
    overlay = (alpha * color_layer + (1 - alpha) * image).astype(np.uint8)
    cv2.imwrite(os.path.join(output_path, f"{base}_with_overlay{ext}"), overlay)


# ———————————————————————————————— 2. Batch driver ————————————————————————————————— #
def process_split(
    root: str,
    subset: str = "test",
    out_rel: str = "output/segmentation",
    exts: Tuple[str, ...] = ("*.jpg", "*.jpeg", "*.png", "*.bmp"),
):
    """Walk `root/images/<subset>` and process every image with a matching label."""
    img_dir = os.path.join(root, "images", subset)
    lbl_dir = os.path.join(root, "labels", subset)
    out_dir = os.path.join(root, out_rel, subset)

    if not os.path.isdir(img_dir):
        raise FileNotFoundError(f"No such image directory: {img_dir}")
    if not os.path.isdir(lbl_dir):
        raise FileNotFoundError(f"No such label directory: {lbl_dir}")

    # Gather image paths
    img_paths = []
    for ext in exts:
        img_paths.extend(glob.glob(os.path.join(img_dir, ext)))
    img_paths.sort()

    if not img_paths:
        print(f"[INFO] No images found in {img_dir}")
        return

    print(f"[INFO] Processing {len(img_paths)} images in '{subset}' split …")

    for idx, img_path in enumerate(img_paths, 1):
        base = os.path.splitext(os.path.basename(img_path))[0]
        txt_path = os.path.join(lbl_dir, base + ".txt")
        apply_yolo_mask_to_image(img_path, txt_path, out_dir)

        if idx % 50 == 0 or idx == len(img_paths):
            print(f"  {idx:>6}/{len(img_paths)} done")


# ———————————————————————————————— 3. Main ————————————————————————————————————— #
if __name__ == "__main__":
    process_split(DATA_ROOT, SPLIT, OUT_REL)
