import os
import json
import shutil
import re
from PIL import Image
from sklearn.model_selection import train_test_split

TOOTH_LABELS = [
    '11', '12', '13', '14', '15', '16', '17', '18',
    '21', '22', '23', '24', '25', '26', '27', '28',
    '31', '32', '33', '34', '35', '36', '37', '38',
    '41', '42', '43', '44', '45', '46', '47', '48'
]
TOOTH_MAP = {label: idx for idx, label in enumerate(TOOTH_LABELS)}

INPUT_DIR   = "AI/data"
YOLO_DIR    = "yolo_dataset"
LABELS_DIR  = os.path.join(YOLO_DIR, "labels")
IMAGES_DIR  = os.path.join(YOLO_DIR, "images")

# Desired split ratios must add up to 1.0
SPLIT_RATIOS = {"train": 0.7, "val": 0.2, "test": 0.1}
assert abs(sum(SPLIT_RATIOS.values()) - 1.0) < 1e-6, "Split ratios must sum to 1"

def ensure_folders() -> None:
    for split in SPLIT_RATIOS:
        os.makedirs(os.path.join(LABELS_DIR, split), exist_ok=True)
        os.makedirs(os.path.join(IMAGES_DIR, split), exist_ok=True)


def collect_samples():
    samples = []
    for case in os.listdir(INPUT_DIR):
        case_dir = os.path.join(INPUT_DIR, case)
        if not os.path.isdir(case_dir):
            continue

        for filename in os.listdir(case_dir):
            if not filename.lower().endswith(".json"):
                continue

            json_path = os.path.join(case_dir, filename)
            stem = os.path.splitext(filename)[0]

            for ext in (".jpeg", ".jpg"):
                img_path = os.path.join(case_dir, stem + ext)
                if os.path.exists(img_path):
                    samples.append((img_path, json_path))
                    break

    return samples



def split_dataset(samples):
    train_samples, remainder = train_test_split(
        samples,
        test_size=SPLIT_RATIOS["val"] + SPLIT_RATIOS["test"],
        random_state=42,
        shuffle=True,
    )
    val_frac_within_remainder = SPLIT_RATIOS["val"] / (SPLIT_RATIOS["val"] + SPLIT_RATIOS["test"])
    val_samples, test_samples = train_test_split(
        remainder,
        test_size=1 - val_frac_within_remainder,
        random_state=42,
        shuffle=True,
    )
    return {"train": train_samples, "val": val_samples, "test": test_samples}


def convert_to_yolo_format(json_file, img_file, dest_txt):
    with open(json_file) as fh:
        data = json.load(fh)

    img = Image.open(img_file)
    w, h = img.size

    with open(dest_txt, "w") as out:
        for shape in data["shapes"]:
            label_raw = shape["label"].strip().strip(".")
            m = re.match(r"(\d+)", label_raw)
            if not m:
                print(f"[WARN] '{label_raw}' has no numeric label – skipped")
                continue

            tooth_num = m.group(1)
            if tooth_num not in TOOTH_MAP:
                print(f"[WARN] Unknown tooth '{tooth_num}' in {json_file} – skipped")
                continue
            class_id = TOOTH_MAP[tooth_num]

            xs = [p[0] for p in shape["points"]]
            ys = [p[1] for p in shape["points"]]
            x_min, x_max = min(xs), max(xs)
            y_min, y_max = min(ys), max(ys)

            x_c = (x_min + x_max) / 2 / w
            y_c = (y_min + y_max) / 2 / h
            bw  = (x_max - x_min) / w
            bh  = (y_max - y_min) / h
            out.write(f"{class_id} {x_c:.6f} {y_c:.6f} {bw:.6f} {bh:.6f}\n")


def process_split(split_name, sample_list):
    for img_path, json_path in sample_list:
        stem = os.path.splitext(os.path.basename(img_path))[0]
        img_dest   = os.path.join(IMAGES_DIR, split_name, f"{stem}.jpg")
        label_dest = os.path.join(LABELS_DIR,  split_name, f"{stem}.txt")

        shutil.copy2(img_path, img_dest)
        convert_to_yolo_format(json_path, img_path, label_dest)


def main():
    ensure_folders()
    samples = collect_samples()
    splits  = split_dataset(samples)

    for split_name, split_samples in splits.items():
        print(f"{split_name:>5}: {len(split_samples)} images")
        process_split(split_name, split_samples)


if __name__ == "__main__":
    main()
