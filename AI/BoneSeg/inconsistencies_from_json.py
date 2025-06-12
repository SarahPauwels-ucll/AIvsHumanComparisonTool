import os
import json

# Root directory of your dataset
root_dir = r"AI/Normal bone"

# Label normalization mapping
LABEL_NORMALIZATION_MAP = {
    "maxillary": "maxillary bone lvl",
    "maxillary lvl": "maxillary bone lvl",
    "maxillary-bone-lvl": "maxillary bone lvl",
    "mandible": "mandibular bone lvl",
    "mandible lvl": "mandibular bone lvl",
    "mandibular-bone-lvl": "mandibular bone lvl"
}

# Supported image file extensions
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".bmp"]

def normalize_labels_in_json(json_path):
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        changed = False
        for shape in data.get("shapes", []):
            original_label = shape.get("label", "").strip().lower()
            normalized_label = LABEL_NORMALIZATION_MAP.get(original_label)
            if normalized_label:
                shape["label"] = normalized_label
                changed = True

        if changed:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print(f"✅ Normalized: {json_path}")
    except Exception as e:
        print(f"⚠️ Error processing {json_path}: {e}")

def process_directory(root):
    for dirpath, _, filenames in os.walk(root):
        json_files = {os.path.splitext(f)[0] for f in filenames if f.endswith(".json")}

        for file in filenames:
            file_path = os.path.join(dirpath, file)
            base_name, ext = os.path.splitext(file)

            if ext.lower() in IMAGE_EXTENSIONS:
                # Check if there's a corresponding JSON file
                if base_name not in json_files:
                    try:
                        os.remove(file_path)
                        print(f"🗑️ Removed image without JSON: {file_path}")
                    except Exception as e:
                        print(f"⚠️ Error deleting {file_path}: {e}")

            elif ext.lower() == ".json":
                normalize_labels_in_json(file_path)

# Run the processing
process_directory(root_dir)
print("🎉 All done: label normalization + cleanup complete.")
