import os
import json
import cv2
import numpy as np
import albumentations as A
from matplotlib import pyplot as plt

# --------------------------------------------------------------------------------
# STEP 1: DEFINE YOUR LABEL MAPPING (CUSTOMIZE THIS!)
# --------------------------------------------------------------------------------
# Example: Suppose these are your unique tooth labels found in the JSON files.
# You need to list all 32 unique labels your annotators have used.
ALL_POSSIBLE_LABELS = ['11', '12', '13', '14', '15', '16', '17', '18',
        '21', '22', '23', '24', '25', '26', '27', '28',
        '31', '32', '33', '34', '35', '36', '37', '38',
        '41', '42', '43', '44', '45', '46', '47', '48']
# This is an example for 32 teeth using FDI notation. Adjust to your actual labels.

LABEL_TO_ID_MAP = {label: i for i, label in enumerate(ALL_POSSIBLE_LABELS)}
# ID 0 will be background implicitly by initializing mask with zeros.

# For visualization (optional, but helpful)
COLORS = [[0, 0, 0]] + [list(np.random.randint(50, 250, size=3)) for _ in ALL_POSSIBLE_LABELS]  # Brighter random colors
COLOR_MAP_FOR_VISUALIZATION = np.array(COLORS, dtype=np.uint8)


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
        points = shape.get('points')

        if label is None or points is None:
            print(f"Warning: Skipping shape with missing label or points in {json_path}")
            continue

        if not points or len(points) < 3:  # A polygon needs at least 3 points
            print(f"Warning: Skipping shape with insufficient points for label '{label}' in {json_path}")
            continue

        if label not in label_to_id_map:
            print(f"Warning: Label '{label}' in {json_path} not in LABEL_TO_ID_MAP. Skipping.")
            continue

        class_id = label_to_id_map[label]
        try:
            polygon_points = np.array(points, dtype=np.int32)
        except ValueError as e:
            print(
                f"Warning: Could not convert points to numpy array for label '{label}' in {json_path}. Error: {e}. Skipping.")
            continue

        cv2.fillPoly(mask, [polygon_points.reshape((-1, 1, 2))], class_id)  # Reshape for fillPoly

    return image, mask


# --------------------------------------------------------------------------------
# STEP 3: DISCOVERING YOUR DATA
# --------------------------------------------------------------------------------
def find_data_pairs(data_dir):
    data_pairs = []
    base_data_dir = os.path.abspath(data_dir)  # Get absolute path

    if not os.path.isdir(base_data_dir):
        print(f"Error: Data directory '{base_data_dir}' not found.")
        return data_pairs

    # Iterate over items in the base_data_dir
    for item_name in os.listdir(base_data_dir):
        item_path = os.path.join(base_data_dir, item_name)
        if os.path.isdir(item_path):  # This is a subfolder for an image/annotation pair
            subfolder_path = item_path
            image_file = None
            json_file = None
            for f_name in os.listdir(subfolder_path):
                f_path = os.path.join(subfolder_path, f_name)
                if f_name.lower().endswith(('.jpg', '.jpeg')):
                    if image_file is None:
                        image_file = f_path
                    else:
                        print(f"Warning: Multiple images found in {subfolder_path}. Using first one: {image_file}")
                elif f_name.lower().endswith('.json'):
                    if json_file is None:
                        json_file = f_path
                    else:
                        print(f"Warning: Multiple JSON files found in {subfolder_path}. Using first one: {json_file}")

            if image_file and json_file:
                data_pairs.append((image_file, json_file))
            elif image_file or json_file:
                print(f"Warning: Missing image or JSON in {subfolder_path}. Image: {image_file}, JSON: {json_file}")
    return data_pairs


# --------------------------------------------------------------------------------
# STEP 4: DEFINING AN AUGMENTATION PIPELINE
# --------------------------------------------------------------------------------
transform = A.Compose([
    A.HorizontalFlip(p=0.5),
    A.Rotate(limit=15, p=0.7, border_mode=cv2.BORDER_CONSTANT, value=0, mask_value=0),
    A.RandomScale(scale_limit=0.15, p=0.6, interpolation=cv2.INTER_NEAREST),  # Use INTER_NEAREST for masks
    A.RandomBrightnessContrast(brightness_limit=0.25, contrast_limit=0.25, p=0.75),
    A.GaussianBlur(blur_limit=(3, 7), p=0.3),
    A.ElasticTransform(p=0.4, alpha=100, sigma=100 * 0.07, alpha_affine=100 * 0.04,
                       border_mode=cv2.BORDER_CONSTANT, value=0, mask_value=0),
    # A.ShiftScaleRotate(shift_limit=0.0625, scale_limit=0.1, rotate_limit=10, p=0.5,
    #                    border_mode=cv2.BORDER_CONSTANT, value=0, mask_value=0), # Alternative to separate scale/rotate
    A.GaussNoise(var_limit=(10.0, 50.0), p=0.2),
    # Consider adding GridDistortion or OpticalDistortion if they make sense for panoramic X-rays
    # A.GridDistortion(p=0.2, border_mode=cv2.BORDER_CONSTANT, value=0, mask_value=0),
])


# --------------------------------------------------------------------------------
# STEP 5: APPLYING AUGMENTATIONS AND VISUALIZING
# --------------------------------------------------------------------------------
def visualize(image, mask_ids, augmented_image, augmented_mask_ids, color_map):
    original_mask_rgb = get_color_mask(mask_ids, color_map)
    augmented_mask_rgb = get_color_mask(augmented_mask_ids, color_map)

    fig, axes = plt.subplots(2, 2, figsize=(12, 12))
    fig.suptitle("Data Augmentation with Albumentations", fontsize=16)

    axes[0, 0].imshow(image, cmap='gray')
    axes[0, 0].set_title("Original Image")
    axes[0, 0].axis('off')

    axes[0, 1].imshow(original_mask_rgb)
    axes[0, 1].set_title("Original Mask")
    axes[0, 1].axis('off')

    axes[1, 0].imshow(augmented_image, cmap='gray')
    axes[1, 0].set_title("Augmented Image")
    axes[1, 0].axis('off')

    axes[1, 1].imshow(augmented_mask_rgb)
    axes[1, 1].set_title("Augmented Mask")
    axes[1, 1].axis('off')

    plt.tight_layout(rect=[0, 0, 1, 0.96])  # Adjust layout to make space for suptitle
    plt.show()


# --- Main Execution Example ---
if __name__ == "__main__":
    # IMPORTANT: Set your data directory correctly
    # Assuming your script is NOT in the AI folder, but one level above, or provide absolute path.
    # If script is in the same folder as the AI folder:
    data_directory = os.path.join("AI", "data")
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

    # 3. Load one sample and process
    image_path, json_path = data_pairs[0]  # Take the first sample for demonstration
    print(f"\nProcessing sample image: {image_path}")
    print(f"Processing sample JSON:  {json_path}")

    try:
        original_image, original_mask = load_image_and_mask(image_path, json_path, LABEL_TO_ID_MAP)
    except Exception as e:
        print(f"Error loading sample {image_path}: {e}")
        # Consider how to handle errors: skip file, log, or exit
        # For a robust pipeline, you might want to 'continue' in a loop
        exit()

    print(f"Original image shape: {original_image.shape}, Original mask shape: {original_mask.shape}")
    print(f"Unique IDs in original mask: {np.unique(original_mask)}")

    # 4. Apply augmentations
    try:
        augmented_data = transform(image=original_image, mask=original_mask)
        augmented_image = augmented_data['image']
        augmented_mask = augmented_data['mask']
    except Exception as e:
        print(f"Error during augmentation for {image_path}: {e}")
        # This can happen if a transform fails, e.g. due to image size or type issues
        exit()

    print(f"Augmented image shape: {augmented_image.shape}, Augmented mask shape: {augmented_mask.shape}")
    print(f"Unique IDs in augmented mask: {np.unique(augmented_mask)}")

    # 5. Visualize
    print("\nDisplaying original and augmented sample...")
    visualize(original_image, original_mask,
              augmented_image, augmented_mask,
              COLOR_MAP_FOR_VISUALIZATION)

    # --- Further Steps ---
    # In a real training pipeline, you would loop through all data_pairs:
    # for image_path, json_path in data_pairs:
    #     try:
    #         image, mask = load_image_and_mask(image_path, json_path, LABEL_TO_ID_MAP)
    #         for _ in range(num_augmentations_per_image): # Generate multiple augmented versions
    #             augmented = transform(image=image, mask=mask)
    #             aug_img = augmented['image']
    #             aug_mask = augmented['mask']
    #             # TODO: Save aug_img and aug_mask or feed to your YOLO model's dataloader
    #             # For YOLO, you might need to convert aug_mask back to polygon format
    #             # or use the mask directly if your YOLO version supports raster masks.
    #     except Exception as e:
    #         print(f"Skipping {image_path} due to error: {e}")
    #         continue