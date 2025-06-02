import os
import json
import shutil
import random
from PIL import Image
from sklearn.model_selection import train_test_split
import re
TOOTH_LABELS = [
    '11', '12', '13', '14', '15', '16', '17', '18',
    '21', '22', '23', '24', '25', '26', '27', '28',
    '31', '32', '33', '34', '35', '36', '37', '38',
    '41', '42', '43', '44', '45', '46', '47', '48'
]

# Create mapping from tooth number to class index
TOOTH_MAP = {label: idx for idx, label in enumerate(TOOTH_LABELS)}

INPUT_DIR = "AI/data"
YOLO_DIR = "yolo_dataset"
LABELS_DIR = os.path.join(YOLO_DIR, "labels")
IMAGES_DIR = os.path.join(YOLO_DIR, "images")

# Create folders
for subfolder in ["train", "val"]:
    os.makedirs(os.path.join(LABELS_DIR, subfolder), exist_ok=True)
    os.makedirs(os.path.join(IMAGES_DIR, subfolder), exist_ok=True)

# Gather all image/json pairs
samples = []
for folder in os.listdir(INPUT_DIR):
    folder_path = os.path.join(INPUT_DIR, folder)
    if os.path.isdir(folder_path):
        for file in os.listdir(folder_path):
            if file.endswith(".json"):
                json_path = os.path.join(folder_path, file)
                img_name = file.replace(".json", ".jpeg")
                img_path = os.path.join(folder_path, img_name)
                if os.path.exists(img_path):
                    samples.append((img_path, json_path))

# 80/20 split
train_samples, val_samples = train_test_split(samples, test_size=0.2, random_state=42)


def convert_to_yolo_format(json_file, img_file, dest_txt):
    with open(json_file) as f:
        data = json.load(f)

    img = Image.open(img_file)
    width, height = img.size

    with open(dest_txt, 'w') as out_file:
        for shape in data['shapes']:
            label_str = shape['label'].strip().strip('.')

            # Extract leading number from label string
            match = re.match(r"(\d+)", label_str)
            if not match:
                print(f"Warning: No numeric label found in '{label_str}', skipping...")
                continue

            tooth_number = match.group(1)
            if tooth_number not in TOOTH_MAP:
                print(f"Skipping unknown tooth label '{tooth_number}' in {json_file}")
                continue

            label = TOOTH_MAP[tooth_number]
            label_num = int(match.group(1))

            points = shape['points']
            x_coords = [p[0] for p in points]
            y_coords = [p[1] for p in points]
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)
            x_center = (x_min + x_max) / 2 / width
            y_center = (y_min + y_max) / 2 / height
            bbox_width = (x_max - x_min) / width
            bbox_height = (y_max - y_min) / height
            out_file.write(f"{label} {x_center} {y_center} {bbox_width} {bbox_height}\n")

def process_split(samples, split_name):
    for img_path, json_path in samples:
        base = os.path.splitext(os.path.basename(img_path))[0]
        img_dest = os.path.join(IMAGES_DIR, split_name, f"{base}.jpg")
        label_dest = os.path.join(LABELS_DIR, split_name, f"{base}.txt")

        shutil.copy(img_path, img_dest)
        convert_to_yolo_format(json_path, img_path, label_dest)

process_split(train_samples, "train")
process_split(val_samples, "val")
