import json
import math
import os
import random
import shutil
from pathlib import Path
from typing import Iterable, List, Optional

from tqdm import tqdm

CLASS_NAMES: List[str] = [
    "11", "12", "13", "14", "15", "16", "17", "18",
    "21", "22", "23", "24", "25", "26", "27", "28",
    "31", "32", "33", "34", "35", "36", "37", "38",
    "41", "42", "43", "44", "45", "46", "47", "48",
]
CLASS_TO_INDEX = {name: i for i, name in enumerate(CLASS_NAMES)}

BASE_INPUT_DIR = Path("yolo_dataset_augmented_extra_data")
OUTPUT_DATASET_DIR = Path("yolo_dataset_segmentation_extra_data")

IMAGES_DIR = BASE_INPUT_DIR / "images"
LABELS_DIR = BASE_INPUT_DIR / "labels"

SPLIT_RATIOS = {"train": 0.70, "val": 0.20, "test": 0.10}
COMMON_IMAGE_EXTENSIONS = [
    ".jpeg",
    ".jpg",
    ".png",
]

def create_yolo_directories() -> None:
    for split in ("train", "val", "test"):
        (OUTPUT_DATASET_DIR / "images" / split).mkdir(parents=True, exist_ok=True)
        (OUTPUT_DATASET_DIR / "labels" / split).mkdir(parents=True, exist_ok=True)
    print(f"Created directory structure under {OUTPUT_DATASET_DIR.resolve()}")


def collect_json_files(labels_dir: Path) -> List[Path]:
    return sorted(labels_dir.glob("*.json"))


def find_image_for_json(json_path: Path, images_dir: Path) -> Optional[Path]:
    base_name = json_path.stem
    for ext in COMMON_IMAGE_EXTENSIONS:
        candidate = images_dir / f"{base_name}{ext}"
        if candidate.is_file():
            return candidate
    return None


def convert_and_save_yolo_segmentation(json_data: dict, dst_label: Path) -> bool:
    w = json_data.get("imageWidth")
    h = json_data.get("imageHeight")
    if not w or not h:
        print(f"Error: imageWidth / imageHeight missing in {dst_label.name}")
        return False

    shapes = json_data.get("shapes", [])
    yolo_lines: List[str] = []

    for shape in shapes:
        if shape.get("shape_type") not in {"polygon", "polygon_box"}:
            print(
                f"Warning: Unsupported shape_type '{shape.get('shape_type')}' in {dst_label.name}",
            )
            return False

        label = shape.get("label")
        if "contour_points" in shape and shape["contour_points"]:
            points = shape["contour_points"]
        else:
            points = shape.get("points", [])
        if not points:
            print(f"Warning: No points for label '{label}' in {dst_label.name}")
            return False

        if label not in CLASS_TO_INDEX:
            print(f"Warning: Unknown label '{label}' in {dst_label.name}")
            return False
        class_idx = CLASS_TO_INDEX[label]

        norm_coords: List[float] = []
        for x, y in points:
            norm_coords.extend([max(0.0, min(1.0, x / w)), max(0.0, min(1.0, y / h))])

        yolo_lines.append(" ".join([str(class_idx)] + [f"{c:.6f}" for c in norm_coords]))

    dst_label.write_text("\n".join(yolo_lines))
    return True


def main() -> None:
    create_yolo_directories()

    all_json_files = collect_json_files(LABELS_DIR)
    if not all_json_files:
        print(f"No JSON files in {LABELS_DIR}. Is the path correct?")
        return

    random.seed(42)
    random.shuffle(all_json_files)

    n_total = len(all_json_files)
    n_train = math.floor(n_total * SPLIT_RATIOS["train"])
    n_val = math.floor(n_total * SPLIT_RATIOS["val"])

    splits = {
        "train": all_json_files[:n_train],
        "val": all_json_files[n_train : n_train + n_val],
        "test": all_json_files[n_train + n_val :],
    }

    print(f"Total annotations: {n_total}")
    for s, items in splits.items():
        print(f"  {s:<5}: {len(items)}")

    for split, json_paths in splits.items():
        print(f"\nProcessing '{split}' split…")
        for json_path in tqdm(json_paths, unit="file"):
            try:
                data = json.loads(json_path.read_text(encoding="utf‑8"))
            except Exception as exc:
                print(f"Error reading {json_path}: {exc}")
                continue

            img_path = find_image_for_json(json_path, IMAGES_DIR)
            if img_path is None:
                print(f"Warning: No image for {json_path.name} – skipping.")
                continue

            destination_image = OUTPUT_DATASET_DIR / "images" / split / img_path.name
            destination_label = OUTPUT_DATASET_DIR / "labels" / split / f"{img_path.stem}.txt"

            if convert_and_save_yolo_segmentation(data, destination_label):
                try:
                    shutil.copy2(img_path, destination_image)
                except Exception as exc:
                    print(f"Error copying {img_path} → {destination_image}: {exc}")
            else:
                if destination_label.exists():
                    destination_label.unlink(missing_ok=True)

    print(f"YOLO dataset stored in {OUTPUT_DATASET_DIR.resolve()}")


if __name__ == "__main__":
    main()
