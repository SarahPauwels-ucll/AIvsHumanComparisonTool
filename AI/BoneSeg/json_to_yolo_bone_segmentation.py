import os
import json
import shutil
import random
from glob import glob

# Set paths
base_dir = "AI/Normal bone"
output_base = "YOLO_dataset_bone_seg"
splits = ['train', 'val', 'test']
split_ratio = [0.7, 0.2, 0.1]

# Step 1: Find all JSON files
json_files = glob(os.path.join(base_dir, "**", "*.json"), recursive=True)

# Step 2: Map image files by base filename
image_extensions = [".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"]
image_dict = {}
for ext in image_extensions:
    for img_path in glob(os.path.join(base_dir, "**", f"*{ext}"), recursive=True):
        base = os.path.splitext(os.path.basename(img_path))[0]
        image_dict[base] = img_path

# Step 3: Match JSONs to their images
data = []
for json_path in json_files:
    base = os.path.splitext(os.path.basename(json_path))[0]
    if base in image_dict:
        data.append((image_dict[base], json_path))
    else:
        print(f"[WARNING] No image found for JSON: {json_path}")

# Step 4: Shuffle and split
random.shuffle(data)
n = len(data)
train_end = int(n * split_ratio[0])
val_end = int(n * split_ratio[0] + n * split_ratio[1])
split_data = {
    'train': data[:train_end],
    'val': data[train_end:val_end],
    'test': data[val_end:]
}

# Step 5: Label mapping
label_map = {
    "mandibular bone lvl": 0,
    "maxillary bone lvl": 1
}

# Step 6: Convert polygon to YOLO bbox
def polygon_to_bbox(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    x_center = (x_min + x_max) / 2
    y_center = (y_min + y_max) / 2
    width = x_max - x_min
    height = y_max - y_min
    return x_center, y_center, width, height

# Step 7: Create folders and process data
for split in splits:
    os.makedirs(f"{output_base}/images/{split}", exist_ok=True)
    os.makedirs(f"{output_base}/labels/{split}", exist_ok=True)

    for img_path, json_path in split_data[split]:
        with open(json_path, "r") as f:
            data_json = json.load(f)

        h, w = data_json.get("imageHeight"), data_json.get("imageWidth")
        if not h or not w:
            print(f"[WARNING] Missing image dimensions in {json_path}")
            continue

        label_lines = []
        for shape in data_json["shapes"]:
            label = shape["label"]
            if label not in label_map:
                continue
            points = shape["points"]
            class_id = label_map[label]

            normalized_points = []
            for x, y in points:
                normalized_points.append(x / w)
                normalized_points.append(y / h)

            line = f"{class_id} " + " ".join(f"{pt:.6f}" for pt in normalized_points)
            label_lines.append(line)

        # Save labels
        base_name = os.path.splitext(os.path.basename(img_path))[0]
        label_path = os.path.join(output_base, f"labels/{split}/{base_name}.txt")
        with open(label_path, "w") as f:
            f.write("\n".join(label_lines))

        # Copy images
        if os.path.exists(img_path):
            shutil.copy(img_path, os.path.join(output_base, f"images/{split}/{base_name}{os.path.splitext(img_path)[1]}"))
        else:
            print(f"[WARNING] Image not found: {img_path}")
