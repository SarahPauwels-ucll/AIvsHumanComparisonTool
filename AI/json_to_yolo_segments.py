import json
import os
import glob
import random
import shutil
import math

# --- Configuration ---
CLASS_NAMES = [
    '11', '12', '13', '14', '15', '16', '17', '18',
    '21', '22', '23', '24', '25', '26', '27', '28',
    '31', '32', '33', '34', '35', '36', '37', '38',
    '41', '42', '43', '44', '45', '46', '47', '48'
]
CLASS_TO_INDEX = {name: i for i, name in enumerate(CLASS_NAMES)}

BASE_INPUT_DIR = "data"  # Root directory for your raw data
OUTPUT_DATASET_DIR = "../yolo_dataset_segmentation"  # Relative path for the output YOLO dataset

SPLIT_RATIOS = {"train": 0.7, "val": 0.2, "test": 0.1}


# --- Helper Functions ---

def create_yolo_directories():
    """Creates the YOLO dataset directory structure."""
    for split in ["train", "val", "test"]:
        os.makedirs(os.path.join(OUTPUT_DATASET_DIR, "images", split), exist_ok=True)
        os.makedirs(os.path.join(OUTPUT_DATASET_DIR, "labels", split), exist_ok=True)
    print(f"Created directory structure under {os.path.abspath(OUTPUT_DATASET_DIR)}")


def collect_json_files(base_input_dir):
    """
    Collects all <id>.json files from data/<id>/<id>.json structure.
    """
    json_files = []
    # Iterate over subdirectories in the base_input_dir (these are the <id> folders)
    for id_folder in os.listdir(base_input_dir):
        id_folder_path = os.path.join(base_input_dir, id_folder)
        if os.path.isdir(id_folder_path):
            # Construct the expected json file path, e.g., data/ABC/ABC.json
            json_file_name = f"{id_folder}.json"
            json_file_path = os.path.join(id_folder_path, json_file_name)
            if os.path.isfile(json_file_path):
                json_files.append(json_file_path)
            else:
                print(f"Warning: Expected JSON file not found: {json_file_path}")
    return json_files


def convert_and_save_yolo_segmentation(json_data, output_label_path):
    """
    Converts JSON data to YOLO segmentation lines and saves to a file.
    Returns True if successful, False otherwise.
    """
    image_path_in_json = json_data.get("imagePath")
    image_width = json_data.get("imageWidth")
    image_height = json_data.get("imageHeight")
    shapes = json_data.get("shapes", [])

    if not all([image_path_in_json, image_width, image_height]):
        print(f"Error: Missing imagePath, imageWidth, or imageHeight in JSON for {output_label_path}")
        return False

    yolo_lines = []
    for shape in shapes:
        if shape.get("shape_type") != "polygon":
            # print(f"Warning: Skipping non-polygon shape: {shape.get('label')} for {image_path_in_json}")
            continue

        label = shape.get("label")
        points = shape.get("points", [])

        if label not in CLASS_TO_INDEX:
            print(f"Warning: Label '{label}' not in CLASS_NAMES. Skipping for {image_path_in_json}.")
            continue

        class_index = CLASS_TO_INDEX[label]

        normalized_points = []
        for point in points:
            if len(point) == 2:
                x, y = point
                norm_x = x / image_width
                norm_y = y / image_height
                norm_x = max(0.0, min(1.0, norm_x))  # Clamp to [0.0, 1.0]
                norm_y = max(0.0, min(1.0, norm_y))  # Clamp to [0.0, 1.0]
                normalized_points.extend([norm_x, norm_y])
            else:
                # print(f"Warning: Invalid point format {point} for label '{label}' in {image_path_in_json}")
                continue

        if normalized_points:
            yolo_line_parts = [str(class_index)] + [f"{coord:.6f}" for coord in normalized_points]
            yolo_line = " ".join(yolo_line_parts)
            yolo_lines.append(yolo_line)

    if not yolo_lines:
        # print(f"Warning: No valid polygons found for {image_path_in_json}. Creating empty label file.")
        # Create an empty file if no valid annotations, YOLO might expect this.
        pass

    with open(output_label_path, 'w') as f:
        f.write("\n".join(yolo_lines))
    return True


# --- Main Processing Logic ---
if __name__ == "__main__":
    create_yolo_directories()

    all_json_files = collect_json_files(BASE_INPUT_DIR)
    if not all_json_files:
        print(
            f"No JSON files found in the structure {BASE_INPUT_DIR}/<id>/<id>.json. Please check your input directory.")
        exit()

    random.shuffle(all_json_files)  # Shuffle for random split

    total_files = len(all_json_files)
    num_train = math.floor(total_files * SPLIT_RATIOS["train"])
    num_val = math.floor(total_files * SPLIT_RATIOS["val"])
    # The rest go to test
    # num_test = total_files - num_train - num_val

    files_splits = {
        "train": all_json_files[:num_train],
        "val": all_json_files[num_train: num_train + num_val],
        "test": all_json_files[num_train + num_val:]
    }

    print(f"Total files found: {total_files}")
    print(f"Training files: {len(files_splits['train'])}")
    print(f"Validation files: {len(files_splits['val'])}")
    print(f"Test files: {len(files_splits['test'])}")

    processed_count = 0
    for split_name, json_file_list in files_splits.items():
        print(f"\nProcessing '{split_name}' split...")
        for json_file_path in json_file_list:
            try:
                with open(json_file_path, 'r') as f:
                    data = json.load(f)
            except Exception as e:
                print(f"Error reading or parsing JSON {json_file_path}: {e}")
                continue

            image_filename_from_json = data.get("imagePath")
            if not image_filename_from_json:
                print(f"Warning: 'imagePath' not found in {json_file_path}. Skipping.")
                continue

            # Construct source image path: data/<id>/<image_filename_from_json>
            # Assumes imagePath is just the filename, not a relative path from JSON location
            source_image_path = os.path.join(os.path.dirname(json_file_path), image_filename_from_json)

            if not os.path.exists(source_image_path):
                print(
                    f"Warning: Image file not found at {source_image_path} (referenced in {json_file_path}). Skipping.")
                continue

            # Determine destination paths
            image_base_name = os.path.basename(image_filename_from_json)
            label_base_name = os.path.splitext(image_base_name)[0]

            dest_image_path = os.path.join(OUTPUT_DATASET_DIR, "images", split_name, image_base_name)
            dest_label_path = os.path.join(OUTPUT_DATASET_DIR, "labels", split_name, f"{label_base_name}.txt")

            # Convert and save label file
            if convert_and_save_yolo_segmentation(data, dest_label_path):
                # Copy image file
                try:
                    shutil.copy2(source_image_path, dest_image_path)
                    processed_count += 1
                    if processed_count % 50 == 0:  # Print progress every 50 files
                        print(f"Processed {processed_count}/{total_files} files...")
                except Exception as e:
                    print(f"Error copying image {source_image_path} to {dest_image_path}: {e}")
            else:
                print(f"Failed to process annotations for {json_file_path}.")

    print(f"\nDataset creation complete. {processed_count} files processed.")
    print(f"Dataset stored in: {os.path.abspath(OUTPUT_DATASET_DIR)}")
    print(
        "Remember to update your yolo_segments.yaml 'path' to point to this directory if needed, e.g., path: ../yolo_dataset_segmentation")