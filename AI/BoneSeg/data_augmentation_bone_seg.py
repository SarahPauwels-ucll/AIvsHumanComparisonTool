import os
import json
import time
from multiprocessing import freeze_support

import cv2
import numpy as np
import albumentations as A
from matplotlib import pyplot as plt
from tqdm import tqdm
from tqdm.contrib.concurrent import thread_map

# --------------------------------------------------------------------------------
# STEP 1: DEFINE YOUR LABEL MAPPING (CUSTOMIZE THIS!)
# --------------------------------------------------------------------------------
# Example: Suppose these are your unique tooth labels found in the JSON files.
# You need to list all 32 unique labels your annotators have used.
ALL_POSSIBLE_LABELS = ['mandibular bone lvl', 'maxillary bone lvl']
# This is an example for 32 teeth using FDI notation. Adjust to your actual labels.

LABEL_TO_ID_MAP = {label: i + 1 for i, label in enumerate(ALL_POSSIBLE_LABELS)}
# ID 0 will be background implicitly by initializing mask with zeros.

# For visualization (optional, but helpful)
COLORS = [[0, 0, 0]] + [list(np.random.randint(50, 250, size=3)) for _ in ALL_POSSIBLE_LABELS]  # Brighter random colors
COLOR_MAP_FOR_VISUALIZATION = np.array(COLORS, dtype=np.uint8)

NUM_AUGMENTATIONS_PER_IMAGE = 5

def get_color_mask(mask_ids, color_map):
    rgb_mask = np.zeros((*mask_ids.shape, 3), dtype=np.uint8)
    # Ensure color_map has enough colors for max_id in mask_ids
    max_id = np.max(mask_ids)
    if max_id >= len(color_map):  # Resize color_map if necessary (should not happen if LABEL_TO_ID_MAP is correct)
        print(
            f"Warning: Max ID in mask ({max_id}) exceeds color map size ({len(color_map)}). Some classes may share colors.")
        # Add dummy colors if needed, though this indicates an issue with LABEL_TO_ID_MAP or mask generation
        additional_colors = [list(np.random.randint(50, 250, size=3)) for _ in range(max_id - len(color_map) + 1)]
        color_map = np.vstack([color_map, np.array(additional_colors, dtype=np.uint8)])

    for class_id in np.unique(mask_ids):  # Iterate only over present class IDs
        if class_id == 0 and class_id >= len(
                color_map):  # Handle case where only background (0) is present and color_map is empty
            rgb_mask[mask_ids == class_id] = [0, 0, 0]  # Default background color
        elif class_id < len(color_map):
            rgb_mask[mask_ids == class_id] = color_map[class_id]
        else:  # Should not happen with the check above, but as a fallback
            rgb_mask[mask_ids == class_id] = [255, 255, 255]  # White for unknown classes
    return rgb_mask


# --------------------------------------------------------------------------------
# STEP 2: HELPER FUNCTION TO LOAD IMAGE AND CREATE MASK
# --------------------------------------------------------------------------------
def load_image_and_mask(image_path, json_path, label_to_id_map):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(f"Image not found or unreadable: {image_path}")

    height, width = image.shape[:2]
    mask = np.zeros((height, width), dtype=np.uint8)

    try:
        with open(json_path, 'r') as f:
            annotations = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Annotation JSON not found: {json_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Error decoding JSON: {json_path}")

    for shape in annotations.get('shapes', []):
        label = shape.get('label')
        if shape.get("contour_points", []):
            points = shape["contour_points"]
        elif shape.get("points", []) and len(shape["points"]) > 0:
            points = shape.get("points", [])
        else:
            points = None

        if label is None or points is None:
            raise Exception(f"Warning: Skipping shape with missing label or points in {json_path}")

        if not points or len(points) < 4:  # A polygon needs at least 3 points
            raise Exception(f"Warning: Skipping shape with insufficient points for label '{label}' in {json_path}")

        if label not in label_to_id_map:
            raise Exception(f"Warning: Label '{label}' in {json_path} not in LABEL_TO_ID_MAP. Skipping.")

        class_id = label_to_id_map[label]
        try:
            polygon_points = np.array(points, dtype=np.int32)
        except ValueError as e:
            raise Exception(
                f"Warning: Could not convert points to numpy array for label '{label}' in {json_path}. Error: {e}. Skipping.")

        cv2.fillPoly(mask, [polygon_points.reshape((-1, 1, 2))], class_id)  # Reshape for fillPoly

    return image, mask


# --------------------------------------------------------------------------------
# STEP 3: DISCOVERING YOUR DATA
# --------------------------------------------------------------------------------
def find_data_pairs(data_dir):
    data_pairs = []
    base_data_dir = os.path.abspath(data_dir)

    for root, _, files in os.walk(base_data_dir):
        file_map = {}
        for file in files:
            name, ext = os.path.splitext(file)
            if ext.lower() in ['.jpg', '.jpeg', '.png', '.json']:
                if name not in file_map:
                    file_map[name] = {}
                file_map[name][ext.lower()] = os.path.join(root, file)

        for base_name, paths in file_map.items():
            if '.json' in paths and any(img_ext in paths for img_ext in ['.jpg', '.jpeg', '.png']):
                for img_ext in ['.jpg', '.jpeg', '.png']:
                    if img_ext in paths:
                        data_pairs.append((paths[img_ext], paths['.json']))
                        break
            elif '.json' in paths or any(img_ext in paths for img_ext in ['.jpg', '.jpeg', '.png']):
                print(f"Warning: Incomplete pair for base name '{base_name}' in {root}. Skipping.")

    return data_pairs



# --------------------------------------------------------------------------------
# STEP 4: DEFINING AN AUGMENTATION PIPELINE
# --------------------------------------------------------------------------------
transform = A.Compose([
    A.HorizontalFlip(p=0.5),
    #A.Rotate(limit=15, p=0.7, border_mode=cv2.BORDER_CONSTANT),
    A.RandomScale(scale_limit=0.05, p=0.6, interpolation=cv2.INTER_NEAREST),
    A.RandomBrightnessContrast(brightness_limit=0.1, contrast_limit=0.1, p=0.75),
    #A.GaussianBlur(blur_limit=(3, 7), p=0.3),
    A.ElasticTransform(p=0.4, alpha=100, sigma=100 * 0.07,
                       border_mode=cv2.BORDER_CONSTANT),
    #A.GaussNoise(p=0.2),
    # Consider adding GridDistortion or OpticalDistortion if they make sense for panoramic X-rays
    # A.GridDistortion(p=0.2, border_mode=cv2.BORDER_CONSTANT, value=0, mask_value=0),
])


def convert_mask_to_yolo_format(mask, image_shape, min_contour_area=10):
    """
    Converts a segmentation mask to YOLO polygon format.

    Args:
        mask (np.array): The segmentation mask where pixel values are class IDs.
                         Assumes class IDs are 1-indexed for objects, and 0 is background.
        image_shape (tuple): The shape of the corresponding image (height, width)
                             for normalizing coordinates.
        min_contour_area (int): Minimum area for a contour to be considered.

    Returns:
        list: A list of strings, each formatted for a YOLO label file.
              (e.g., "class_id norm_x1 norm_y1 norm_x2 norm_y2 ...")
    """
    yolo_lines = []
    image_height, image_width = image_shape[:2]

    unique_class_ids = np.unique(mask)
    for class_id_from_mask in unique_class_ids:
        if class_id_from_mask == 0:  # Skip background
            continue

        # Create binary mask for the current class
        binary_mask_for_class = (mask == class_id_from_mask).astype(np.uint8)

        # Find contours for the current class
        # cv2.RETR_EXTERNAL retrieves only the extreme outer contours.
        # cv2.CHAIN_APPROX_SIMPLE compresses horizontal, vertical, and diagonal segments
        # and leaves only their end points.
        contours, _ = cv2.findContours(binary_mask_for_class, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if cv2.contourArea(contour) < min_contour_area:
                continue

            # YOLO class IDs are typically 0-indexed.
            # If your LABEL_TO_ID_MAP creates 1-indexed IDs (1 to N),
            # subtract 1 here.
            yolo_class_id = class_id_from_mask - 1  # Adjust if your map is already 0-indexed for objects

            # Normalize polygon points
            polygon_points_normalized = []
            # Contour is a list of points, e.g., [[[x1,y1]], [[x2,y2]], ...]
            # We need to flatten it to [x1,y1, x2,y2, ...]
            for point in contour.reshape(-1, 2):  # Reshape to list of (x,y)
                norm_x = point[0] / image_width
                norm_y = point[1] / image_height
                polygon_points_normalized.extend([norm_x, norm_y])

            if len(polygon_points_normalized) > 0:
                # Format: class_id x1 y1 x2 y2 ...
                yolo_line = f"{yolo_class_id} " + " ".join(map(str, polygon_points_normalized))
                yolo_lines.append(yolo_line)

    return yolo_lines


if __name__ == "__main__":
    freeze_support()
    # IMPORTANT: Set your data directory correctly
    # Assuming your script is NOT in the AI folder, but one level above, or provide absolute path.
    # If script is in the same folder as the AI folder:
    data_directory = os.path.join("AI/Normal bone")
    # Or if your script is inside the AI folder:
    # data_directory = "data"  # If script is in AI folder and data is AI/data
    # Or an absolute path:
    # data_directory = "/path/to/your/AI/data"

    # 1. Check Label Mapping
    if not ALL_POSSIBLE_LABELS or not LABEL_TO_ID_MAP:
        print("Error: ALL_POSSIBLE_LABELS or LABEL_TO_ID_MAP is not defined correctly. Please customize it.")
        exit()
    print(f"Using {len(ALL_POSSIBLE_LABELS)} labels mapped to IDs 0 through {len(ALL_POSSIBLE_LABELS) - 1}.")

    # 2. Find data
    data_pairs = find_data_pairs(data_directory)
    if not data_pairs:
        print(
            f"No data pairs found in '{os.path.abspath(data_directory)}'. Check the path and your directory structure.")
        print("Expected structure: data_directory -> subfolder_per_image -> image.jpg/jpeg and annotation.json")
        exit()

    print(f"Found {len(data_pairs)} image-annotation pairs.")

    data_directory = "AI/Normal Bone"  # Or your actual path "AI/data"
    output_base_dir = "yolo_dataset_augmented_extra_data_bone_seg"  # Choose your output directory

    # Create output directories if they don't exist
    output_images_dir = os.path.join(output_base_dir, "images")
    output_labels_dir = os.path.join(output_base_dir, "labels")
    os.makedirs(output_images_dir, exist_ok=True)
    os.makedirs(output_labels_dir, exist_ok=True)

    def augment_one_pair(pair):
        img_idx, (image_path, json_path) = pair
        try:
            original_image, original_mask = load_image_and_mask(image_path, json_path, LABEL_TO_ID_MAP)
        except Exception as e:
            print(f"Error loading {image_path}: {e}. Skipping.")
            return # replaced from continue

        original_basename = os.path.splitext(os.path.basename(image_path))[0]

        for aug_idx in range(NUM_AUGMENTATIONS_PER_IMAGE):
            try:
                augmented_data = transform(image=original_image, mask=original_mask)
                aug_img = augmented_data['image']
                aug_mask = augmented_data['mask']

                # Create a unique filename for the augmented data
                # Using original image index, original name, and augmentation index for clarity
                aug_filename_base = f"{original_basename}_aug_{aug_idx:03d}"

                aug_image_save_path = os.path.join(output_images_dir, f"{aug_filename_base}.jpg")
                aug_label_save_path = os.path.join(output_labels_dir, f"{aug_filename_base}.txt")

                # 1. Save the augmented image
                # Ensure image is in BGR if it's color, or save grayscale directly
                # cv2.imwrite expects BGR or Grayscale. If aug_img is RGB, convert it.
                # Your images are grayscale, so this should be fine.
                cv2.imwrite(aug_image_save_path, aug_img)

                # 2. Convert augmented mask to YOLO format and save labels
                yolo_label_strings = convert_mask_to_yolo_format(aug_mask, aug_img.shape)

                with open(aug_label_save_path, 'w') as f:
                    for line in yolo_label_strings:
                        f.write(line + "\n")

            except Exception as e:
                print(f"Error during augmentation or saving for {original_basename}, aug_idx {aug_idx}: {e}")
                continue

        # Finally, also move the original image to the target directory
        original_image_save_path = os.path.join(output_images_dir, f"{original_basename}_orig.jpg")
        original_label_save_path = os.path.join(output_labels_dir, f"{original_basename}_orig.txt")
        cv2.imwrite(original_image_save_path, original_image)
        yolo_label_strings = convert_mask_to_yolo_format(original_mask, original_image.shape)
        with open(original_label_save_path, 'w') as f:
            for line in yolo_label_strings:
                f.write(line + "\n")


    thread_map(
        augment_one_pair,
        enumerate(data_pairs),
        max_workers=16,
        total=len(data_pairs)
    )
    #for img_idx, (image_path, json_path) in tqdm(enumerate(data_pairs), desc="Creating augmented images", total=len(data_pairs * NUM_AUGMENTATIONS_PER_IMAGE)):


