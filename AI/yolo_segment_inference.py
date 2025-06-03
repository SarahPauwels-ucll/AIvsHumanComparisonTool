import json
import os
import cv2
import torch
from ultralytics import YOLO
from PIL import Image
import numpy as np  # Added for polygon conversion

# Load your trained YOLO SEGMENTATION model
# Replace 'runs/segment/YOUR_TRAIN_RUN/weights/best.pt' with the actual path to your trained segmentation model
MODEL_PATH = 'runs/segment/train/weights/best.pt'  # <--- IMPORTANT: UPDATE THIS PATH

try:
    model = YOLO(MODEL_PATH)
except Exception as e:
    print(f"Error loading model from {MODEL_PATH}: {e}")
    print("Please ensure the MODEL_PATH is correct and points to your trained segmentation model's .pt file.")
    exit()

if torch.cuda.is_available():
    model.to("cuda")
    gpu_name = torch.cuda.get_device_name(0)
    print(f"Using GPU {gpu_name} for inference")
else:
    print("CUDA not detected, using CPU for inference")


# --- STEP 1: Load Ground Truth from JSON (remains the same) ---
def load_ground_truth_labels(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    present_teeth = set(shape['label'] for shape in data['shapes'])
    return present_teeth


# --- STEP 2: Run YOLO Segmentation, Process Masks, and Draw ---
def segment_and_visualize_teeth(image_path, conf_threshold=0.40, save_path='segmented_output.jpg'):
    # It's good practice to read the image with OpenCV to get its dimensions for denormalization
    image_cv = cv2.imread(image_path)
    if image_cv is None:
        print(f"Error: Could not read image at {image_path}")
        return []

    H, W, _ = image_cv.shape

    results = model(image_path)[0]  # Perform inference

    detected_teeth_info = []

    # Check if masks and boxes are present in the results
    if results.masks is not None and results.boxes is not None:
        for i in range(len(results.masks.xy)):  # Iterate through detected masks
            confidence = results.boxes.conf[i].item()

            if confidence < conf_threshold:
                continue

            class_id = int(results.boxes.cls[i].item())

            # Map YOLO class index to FDI tooth number (same as your original script)
            if class_id < 8:
                tooth_num = 11 + class_id  # 11–18
            elif class_id < 16:
                tooth_num = 21 + (class_id - 8)  # 21–28
            elif class_id < 24:
                tooth_num = 31 + (class_id - 16)  # 31–38
            else:
                tooth_num = 41 + (class_id - 24)  # 41–48

            detected_teeth_info.append({
                "tooth": str(tooth_num),
                "confidence": round(confidence, 3)
            })

            # Get polygon points (these are normalized)
            polygon_normalized = results.masks.xy[i]
            # Denormalize polygon points
            polygon_pixel = (polygon_normalized * np.array([W, H])).astype(int)

            # Draw polygon on the image_cv
            cv2.polylines(image_cv, [polygon_pixel], isClosed=True, color=(0, 255, 0), thickness=2)

            # For the label, we can use the bounding box associated with the mask
            # or calculate a position from the polygon (e.g., its top-most point or centroid)
            # Using bounding box for simplicity here if available
            if len(results.boxes.xyxy) > i:
                x1_box, y1_box, _, _ = results.boxes.xyxy[i].tolist()
                label_origin = (int(x1_box), int(y1_box) - 10)  # Adjust offset as needed
            else:  # Fallback if no bounding box, use first point of polygon
                label_origin = (polygon_pixel[0, 0], polygon_pixel[0, 1] - 10)

            label_text = f"{tooth_num} {confidence:.2f}"
            cv2.putText(image_cv, label_text, label_origin, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # Save filtered result
    cv2.imwrite(save_path, image_cv)
    print(f"Saved segmented image to: {save_path}")

    return detected_teeth_info


# --- STEP 3: Compare and Output Results (modified to call the new segmentation function) ---
def evaluate(image_path, json_path):
    ground_truth = load_ground_truth_labels(json_path)
    # Call the new segmentation function
    detected_teeth_with_conf = segment_and_visualize_teeth(image_path,
                                                           save_path=f"segmented_{os.path.basename(image_path)}")

    detected_teeth_types = set([d['tooth'] for d in detected_teeth_with_conf])

    print(f"\n📸 Evaluating image: {image_path}")
    print(f"✅ Detected Teeth (Segmentation): {detected_teeth_types}")
    print(f"📋 Ground Truth: {ground_truth}\n")

    all_teeth_FDI = list(range(11, 19)) + list(range(21, 29)) + list(range(31, 39)) + list(range(41, 49))

    for tooth in all_teeth_FDI:
        tooth_str = str(tooth)
        in_ground_truth = tooth_str in ground_truth
        is_detected = tooth_str in detected_teeth_types

        if in_ground_truth and is_detected:
            print(f"🦷 Tooth {tooth_str}: Correctly detected (Present)")
        elif in_ground_truth and not is_detected:
            print(f"⚠️ Tooth {tooth_str}: Not detected (False Negative)")
        elif not in_ground_truth and is_detected:
            print(f"🚫 Tooth {tooth_str}: Falsely detected (False Positive)")
        # else:
        # print(f"Tooth {tooth_str}: Correctly not detected (Absent)") # Optional: for true negatives


def get_teeth_presence(image_path, confidence_threshold=0.5):
    # Call the new segmentation function
    detected_teeth_with_conf = segment_and_visualize_teeth(image_path, conf_threshold=confidence_threshold,
                                                           save_path=f"presence_check_{os.path.basename(image_path)}")

    detected_teeth = set(
        d['tooth'] for d in detected_teeth_with_conf
        # Already filtered by conf_threshold in segment_and_visualize_teeth
    )

    all_teeth_options = set(str(t) for t in (
            list(range(11, 19)) + list(range(21, 29)) +
            list(range(31, 39)) + list(range(41, 49))
    ))

    present_teeth = sorted(list(detected_teeth & all_teeth_options))
    missing_teeth = sorted(list(all_teeth_options - detected_teeth))

    return present_teeth, missing_teeth


# Example Usage
# Ensure these paths are correct and the images/JSONs exist
# Assuming your 'AI' folder is at the root of where your script is, or adjust paths.
# If your dataset structure created by the previous script is '../yolo_dataset_segmentation',
# you might want to pick an image from its 'val' or 'test' set.
# For this example, I'll use the path structure you provided in the problem description.
# You might need to adjust this if the 'AI' folder is not in the script's directory.

# Create a dummy image and json for testing if they don't exist
# This is just for the script to run without FileNotFoundError if you don't have the exact files
# In a real scenario, replace these with your actual image and json paths from your test/val set.

example_image_dir = "example_data"  # Create this directory
example_image_name = "sample_image.jpg"  # Use a real image name
example_json_name = "sample_image.json"  # Use a real json name

os.makedirs(example_image_dir, exist_ok=True)
example_image_path = os.path.join(example_image_dir, example_image_name)
example_json_path = os.path.join(example_image_dir, example_json_name)

# Create a dummy image file (replace with your actual image)
if not os.path.exists(example_image_path):
    try:
        from PIL import Image as PILImage

        dummy_img = PILImage.new('RGB', (640, 480), color='red')
        dummy_img.save(example_image_path)
        print(f"Created dummy image: {example_image_path}")
    except ImportError:
        print("Pillow not installed, can't create dummy image. Please use a real image.")
    except Exception as e:
        print(f"Error creating dummy image: {e}")

# Create a dummy JSON file (replace with your actual JSON content)
if not os.path.exists(example_json_path):
    dummy_json_content = {
        "imagePath": example_image_name,  # Or the actual name of the image
        "imageHeight": 480,
        "imageWidth": 640,
        "shapes": [
            {"label": "11", "points": [[10, 10], [50, 10], [50, 50], [10, 50]], "shape_type": "polygon"},
            {"label": "12", "points": [[60, 60], [100, 60], [100, 100], [60, 100]], "shape_type": "polygon"}
        ]
    }
    with open(example_json_path, 'w') as f:
        json.dump(dummy_json_content, f)
    print(f"Created dummy JSON: {example_json_path}")

if os.path.exists(example_image_path) and os.path.exists(example_json_path):
    print(f"\n--- Running evaluate function for segmentation model ---")
    evaluate(example_image_path, example_json_path)

    print(f"\n--- Running get_teeth_presence function for segmentation model ---")
    present, missing = get_teeth_presence(example_image_path, confidence_threshold=0.25)  # Use a suitable threshold
    print(f"Teeth detected as present: {present}")
    print(f"Teeth detected as missing: {missing}")
else:
    print(f"Skipping example usage as dummy files could not be created or real files are missing.")
    print(f"Please ensure '{example_image_path}' and '{example_json_path}' exist or replace them with your test files.")