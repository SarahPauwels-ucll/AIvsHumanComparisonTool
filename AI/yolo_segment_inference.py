#!/usr/bin/env python3
"""
Run inference with a **YOLOv8‑seg** model on either

* the full **test split** (`images/test`) of a YOLO‑style dataset, **or**
* a **single sample** identified by its filename **stem** (image + matching `labels/test/<stem>.txt`).

Just tweak the variables in the **CONFIGURATION** block—no command‑line flags required.

Dataset layout expected::

    DATASET_ROOT/
        images/
            train/      *.jpg|png|…
            val/
            test/
        labels/
            train/      *.txt (YOLO format, not used for inference)
            val/
            test/

When `SPECIFIC_SAMPLE` is *None* (default) the script processes **all** images under
`images/test` (recursively).  If you set `SPECIFIC_SAMPLE = "my_image"`, it will look for:

    images/test/**/my_image.(jpg|jpeg|png|bmp|tif|tiff)
    labels/test/**/my_image.txt        # optional – just checked for existence

Only the image with that stem is sent through the model; the label file, if found,
can be used later for evaluation (this script merely reports its presence).
"""
import random
import sys
from pathlib import Path
from typing import Iterable, List

import cv2
import numpy as np
import torch
from ultralytics import YOLO

MODEL_PATH: str = "runs/segment/train10/weights/best.pt"
#DATASET_ROOT: str = "yolo_dataset_segmentation_extra_data_splits"
DATASET_ROOT: str = "C:/Users/Jarne/KU Leuven/Lola Gracea - UCLL_dataset_28/AI_training/Teeth/Test set"
CONF_THRESHOLD: float = 0.50
IMG_SIZE: int = 1024
OUTPUT_DIR: str | None = "AI/output/segmentation_v2_test_unlabeled"
USE_BLUR: bool = False
WRITE_TOOTH_NAMES: bool = False
DRAW_BOUNDING_BOXES: bool = False

MAX_MASK_OPACITY: float = 0.2
SPECIFIC_SAMPLE: str | None = None

DATASET_ROOT = Path(DATASET_ROOT)
#TEST_IMAGE_DIR = DATASET_ROOT / "images" / "test"
TEST_IMAGE_DIR = DATASET_ROOT
TEST_LABEL_DIR = DATASET_ROOT / "labels" / "test"
OUTPUT_DIR = Path(OUTPUT_DIR or (DATASET_ROOT / "output_test"))

TOOTH_LABELS = [
    '11', '12', '13', '14', '15', '16', '17', '18', #  0,  1,  2,  3,  4,  5,  6,  7
    '21', '22', '23', '24', '25', '26', '27', '28', #  8,  9, 10, 11, 12, 13, 14, 15
    '31', '32', '33', '34', '35', '36', '37', '38', # 16, 17, 18, 19, 20, 21, 22, 23
    '41', '42', '43', '44', '45', '46', '47', '48'  # 24, 25, 26, 27, 28, 29, 30, 31
]

def _gather_images(root: Path, stem: str | None = None) -> List[Path]:
    """Collect images under *root*.
    If *stem* is given, return every file whose name (without suffix) equals *stem*.
    Search is *recursive* to honour arbitrary sub‑folder structures inside *test*.
    """
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}
    if stem is None:
        return [p for p in root.rglob("*") if p.suffix.lower() in exts]

    matches: List[Path] = []
    for ext in exts:
        matches.extend(root.rglob(f"{stem}{ext}"))
    return matches


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


# ---------- Inference ----------

def run_inference(
    model: YOLO,
    image_paths: Iterable[Path],
    image_root: Path,
    output_root: Path,
    *,
    conf_threshold: float = 0.25,
    img_size: int = 1024,
):
    """Run inference on *i mage_paths* and save visualisations under *output_root*."""

    if not image_paths:
        print("[WARN] No images to process – exiting.")
        return

    output_root.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Saving visualisations to: {output_root.resolve()}")

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    font_thickness = 2

    second_digit_colors = {}

    yolo_id_colors = {}

    random.seed(42)  # For reproducible random colors

    for yolo_id, tooth_label in enumerate(TOOTH_LABELS):
        # Ensure the tooth_label is a string and has at least two digits
        if isinstance(tooth_label, int):
            tooth_label_str = str(tooth_label)
        else:
            tooth_label_str = tooth_label

        if len(tooth_label_str) == 2:
            second_digit = tooth_label_str[1]

            if second_digit not in second_digit_colors:
                second_digit_colors[second_digit] = random.sample(range(256), 3)
            yolo_id_colors[yolo_id] = second_digit_colors[second_digit]
        else:
            print(f"Warning: Tooth label '{tooth_label_str}' for YOLO ID {yolo_id} is not a two-digit number. Assigning black.")
            yolo_id_colors[yolo_id] = [0, 0, 0]  # Assign black as a default

    for img_path in image_paths:
        try:
            # Load and sanity‑check image first (so missing/corrupt files are skipped early)
            img = cv2.imread(str(img_path))
            if img is None:
                print(f"[WARN] Could not read {img_path}, skipping.")
                continue
            H, W = img.shape[:2]

            # Forward pass (retina masks give smoother edges)
            res = model.predict(
                source=str(img_path),
                verbose=False,
                retina_masks=True,
                imgsz=img_size,
            )[0]

            for i, box in enumerate(res.boxes):
                conf = float(box.conf[0])
                if conf < conf_threshold:
                    continue

                cls_id = int(box.cls[0])
                cls_name = model.names[cls_id]
                colour = yolo_id_colors[cls_id]

                # ----- Mask -----
                mask_tensor = res.masks.data[i]  # (h0, w0)
                mask_np = (mask_tensor.cpu().numpy().astype(np.uint8)) * 255
                mask_resized = cv2.resize(mask_np, (W, H), interpolation=cv2.INTER_LINEAR)
                if USE_BLUR:
                    mask_resized = cv2.GaussianBlur(mask_resized, (21, 21), 0)
                alpha = (mask_resized.astype(np.float32) / 255.0)[..., None] * MAX_MASK_OPACITY

                colour_layer = np.zeros_like(img, dtype=np.uint8)
                colour_layer[:] = colour  # (B, G, R)

                img = (
                    alpha * colour_layer.astype(np.float32)
                    + (1.0 - alpha) * img.astype(np.float32)
                ).astype(np.uint8)

                # ----- Box & label -----
                if DRAW_BOUNDING_BOXES:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                    cv2.rectangle(img, (x1, y1), (x2, y2), colour, 2)

                if WRITE_TOOTH_NAMES:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                    (tw, th), _ = cv2.getTextSize(cls_name, font, font_scale, font_thickness)
                    tlx = max(0, min(cx - tw // 2, W - tw - 1))
                    tly = max(th, min(cy + th // 2, H - 1))
                    cv2.putText(
                        img,
                        cls_name,
                        (tlx, tly),
                        font,
                        font_scale,
                        (0, 0, 0),
                        font_thickness,
                        cv2.LINE_AA,
                    )

            # ----- Save keeping relative structure -----
            rel_path = img_path.relative_to(image_root)
            out_path = output_root / rel_path.parent / f"pred_{rel_path.name}"
            _ensure_parent(out_path)
            cv2.imwrite(str(out_path), img)
            print(f"[DONE] {rel_path} → {out_path.relative_to(output_root)}")

        except Exception as exc:
            print(f"[ERROR] {img_path}: {exc}")
            import traceback

            traceback.print_exc()


def main() -> None:
    try:
        model = YOLO(MODEL_PATH)
        print(f"[INFO] Loaded model: {MODEL_PATH}")
    except Exception as exc:
        print(f"[FATAL] Could not load model '{MODEL_PATH}': {exc}")
        sys.exit(1)

    # Device
    if torch.cuda.is_available():
        model.to("cuda")
        print(f"[INFO] Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("[INFO] CUDA not available – falling back to CPU.")

    # Determine what to process
    if SPECIFIC_SAMPLE is None:
        imgs_to_process = _gather_images(TEST_IMAGE_DIR, None)
    else:
        imgs_to_process = _gather_images(TEST_IMAGE_DIR, SPECIFIC_SAMPLE)
        if not imgs_to_process:
            print(
                f"[FATAL] No image with stem '{SPECIFIC_SAMPLE}' found under {TEST_IMAGE_DIR}."
            )
            sys.exit(1)
        # Optionally check for matching label file
        label_matches = list(TEST_LABEL_DIR.rglob(f"{SPECIFIC_SAMPLE}.txt"))
        if label_matches:
            print(f"[INFO] Found label file: {label_matches[0].relative_to(DATASET_ROOT)}")
        else:
            print(
                f"[WARN] No matching label file found for '{SPECIFIC_SAMPLE}' under labels/test."
            )

    run_inference(
        model,
        image_paths=imgs_to_process,
        image_root=TEST_IMAGE_DIR,
        output_root=OUTPUT_DIR,
        conf_threshold=CONF_THRESHOLD,
        img_size=IMG_SIZE,
    )

    print(f"\n[FINISHED] Visualisations saved in: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
