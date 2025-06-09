import math
import random
import shutil
from pathlib import Path
from typing import List, Tuple

from tqdm import tqdm

INPUT_DIR: str = "../yolo_dataset_augmented_extra_data"
OUTPUT_DIR: str = "../yolo_dataset_segmentation_extra_data_splits"
SPLIT_RATIOS = {"train": 0.7, "val": 0.2, "test": 0.1}
SEED: int = 42

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg")


def verify_input_structure(root: Path) -> None:
    images_dir = root / "images"
    labels_dir = root / "labels"
    if not images_dir.is_dir() or not labels_dir.is_dir():
        raise Exception(
            f"Input directory must contain 'images/' and 'labels/' sub‑folders.\n"
            f"Found: images/ -> {images_dir.exists()}, labels/ -> {labels_dir.exists()}"
        )


def gather_pairs(root: Path) -> List[Tuple[Path, Path]]:
    images_dir = root / "images"
    labels_dir = root / "labels"

    pairs: List[Tuple[Path, Path]] = []
    for img_path in images_dir.iterdir():
        if img_path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        label_path = labels_dir / (img_path.stem + ".txt")
        if label_path.is_file():
            pairs.append((img_path, label_path))
        else:
            print(f"⚠ No label file for image {img_path.name} - skipped")

    for label_path in labels_dir.iterdir():
        if label_path.suffix.lower() != ".txt":
            continue
        img_path = images_dir / (label_path.stem + ".jpg")
        if not any((images_dir / f"{label_path.stem}{ext}").is_file() for ext in IMAGE_EXTENSIONS):
            print(f"Label {label_path.name} has no matching image – ignored")

    if not pairs:
        raise Exception("No matching image/label pairs found – aborting.")

    return pairs


def create_output_dirs(root: Path) -> None:
    for split in ("train", "val", "test"):
        (root / "images" / split).mkdir(parents=True, exist_ok=True)
        (root / "labels" / split).mkdir(parents=True, exist_ok=True)


def main() -> None:
    input_root = Path(INPUT_DIR).resolve()
    output_root = Path(OUTPUT_DIR).resolve()

    print(f"Input  : {input_root}")
    print(f"Output : {output_root}\n")

    verify_input_structure(input_root)

    pairs = gather_pairs(input_root)
    total_files = len(pairs)
    print(f"Found {total_files} valid image/label pairs.")

    random.seed(SEED)
    random.shuffle(pairs)

    train_end = math.floor(total_files * SPLIT_RATIOS["train"])
    val_end = train_end + math.floor(total_files * SPLIT_RATIOS["val"])

    split_map = {
        "train": pairs[:train_end],
        "val": pairs[train_end:val_end],
        "test": pairs[val_end:],
    }

    for split in ("train", "val", "test"):
        print(f"{split.capitalize()} set: {len(split_map[split])} files")

    create_output_dirs(output_root)

    for split_name, pair_list in split_map.items():
        print(f"\nCopying {split_name} files…")
        for img_path, lbl_path in tqdm(pair_list, unit="file"):
            dest_img = output_root / "images" / split_name / img_path.name
            dest_lbl = output_root / "labels" / split_name / lbl_path.name

            try:
                shutil.copy2(img_path, dest_img)
                shutil.copy2(lbl_path, dest_lbl)
            except Exception as exc:
                print(f"Error copying {img_path.name}: {exc}")

    print("\nDataset successfully split.")
    print(f"Location : {output_root}")
    print("Remember to reference each split directory in your YOLO config if needed.")


if __name__ == "__main__":
    main()
