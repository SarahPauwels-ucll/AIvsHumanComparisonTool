import os
import random

import cv2
import torch
from ultralytics import YOLO
import numpy as np

# --- Configuration ---
MODEL_PATH = 'AI/models/yolo11m_segmentation_finetuned.pt'

# Path to your YOLO dataset (used to find test images)
# Assumes this script is run from a directory where '../yolo_dataset_segmentation' is valid
# e.g., if script is in 'AIvsHumanComparisonTool/scripts/', dataset is in 'AIvsHumanComparisonTool/yolo_dataset_segmentation/'
DATASET_BASE_DIR = "yolo_dataset_segmentation"
TEST_IMAGE_DIR = os.path.join(DATASET_BASE_DIR, "images", "test")

# Output directory for images with drawn segmentations
# This will be created relative to where the script is run.
OUTPUT_VISUALIZATION_DIR = "AI/output/segmentation"

CONF_THRESHOLD = 0.35
# Confidence threshold for displaying detections

# Class names for labeling (should match your YAML)
CLASS_NAMES = [
    '11', '12', '13', '14', '15', '16', '17', '18',
    '21', '22', '23', '24', '25', '26', '27', '28',
    '31', '32', '33', '34', '35', '36', '37', '38',
    '41', '42', '43', '44', '45', '46', '47', '48'
]


def run_inference_on_test_set(model, image_dir, output_dir, conf_threshold):
    if not os.path.exists(image_dir):
        print(f"Error: Test image directory not found at '{os.path.abspath(image_dir)}'")
        return

    os.makedirs(output_dir, exist_ok=True)
    print(f"Output images will be saved to: {os.path.abspath(output_dir)}")

    image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]

    if not image_files:
        print(f"No images found in {image_dir}")
        return

    for image_name in image_files:
        image_path = os.path.join(image_dir, image_name)
        print(f"\nProcessing image: {image_path}")

        try:
            image_cv = cv2.imread(image_path)
            if image_cv is None:
                print(f"Warning: Could not read image {image_path}. Skipping.")
                continue

            H, W, _ = image_cv.shape

            # Run inference over the image
            results = model(image_path, verbose=False)[0]

            # Prepare class info & deterministic colors per class
            random.seed(42)  # reproducible colors
            yolo_classes = list(model.names.values())
            colors = {cls_id: random.sample(range(256), 3) for cls_id, _ in enumerate(yolo_classes)}

            # Load image (BGR for OpenCV drawing)
            image_cv = cv2.imread(image_path)
            overlay = image_cv.copy()
            h, w = image_cv.shape[:2]

            # Drawing parameters
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            font_thickness = 2

            for result in results:
                for mask, box in zip(result.masks.xy, result.boxes):
                    confidence = box.conf[0].item()
                    if confidence < conf_threshold:
                        continue  # Skip low-confidence detections

                    cls_id = int(box.cls[0])
                    class_name = yolo_classes[cls_id]
                    mask_color = colors[cls_id]

                    # ----- Draw mask -----
                    cv2.fillPoly(image_cv, [np.int32(mask)], mask_color)

                    # ----- Bounding-box coords & center -----
                    x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                    cx = (x1 + x2) // 2
                    cy = (y1 + y2) // 2

                    # ----- Compute label placement (centered) -----
                    (text_w, text_h), baseline = cv2.getTextSize(class_name, font, font_scale, font_thickness)
                    top_left_x = cx - text_w // 2
                    top_left_y = cy - text_h // 2

                    # Ensure the text is fully inside the image bounds
                    top_left_x = max(0, min(top_left_x, w - text_w - 1))
                    top_left_y = max(0, min(top_left_y, h - text_h - 1))
                    label_origin = (top_left_x, top_left_y + text_h)  # baseline-left for putText


                    # ----- Draw label text in black -----
                    cv2.putText(
                        image_cv,
                        class_name,
                        label_origin,
                        font,
                        font_scale,
                        (0, 0, 0),  # black text
                        font_thickness,
                        cv2.LINE_AA,
                    )

            # Make yolo polygons transparent
            imagecv_transparent = cv2.addWeighted(overlay, 0.5, image_cv, 0.5, 0)

            output_image_path = os.path.join(output_dir, f"contoured_{image_name}")
            cv2.imwrite(output_image_path, imagecv_transparent)

        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            import traceback
            traceback.print_exc()

        break


if __name__ == "__main__":
    try:
        yolo_model = YOLO(MODEL_PATH)
        # A more reliable check for segmentation task might be to see if 'seg' is in the model's head names or similar
        # For now, we'll rely on the presence of results.masks later.
        # The warning you saw with yolov8n-seg.pt suggests the simple check isn't always perfect.
        print(f"Successfully loaded model from {MODEL_PATH}")
        print(f"Model type as reported by Ultralytics: {yolo_model.type if hasattr(yolo_model, 'type') else 'N/A'}")
        if hasattr(yolo_model, 'overrides'):
            print(f"Model overrides: {yolo_model.overrides}")


    except Exception as e:
        print(f"Error loading model from {MODEL_PATH}: {e}")
        exit()

    if torch.cuda.is_available():
        yolo_model.to("cuda")
        gpu_name = torch.cuda.get_device_name(0)
        print(f"Using GPU {gpu_name} for inference")
    else:
        print("CUDA not detected, using CPU for inference")

    run_inference_on_test_set(yolo_model, TEST_IMAGE_DIR, OUTPUT_VISUALIZATION_DIR, CONF_THRESHOLD)

    print(f"\nInference on test set complete. Visualizations saved in {os.path.abspath(OUTPUT_VISUALIZATION_DIR)}")
