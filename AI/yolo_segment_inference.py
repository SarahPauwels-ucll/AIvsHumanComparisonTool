import os
import random

import cv2
import torch
from ultralytics import YOLO
import numpy as np

from AI.draw_mask_on_input_data import apply_json_mask_to_image

# --- Configuration ---
MODEL_PATH = 'runs/segment/train9/weights/best.pt'

# Path to your YOLO dataset (used to find test images)
# Assumes this script is run from a directory where '../yolo_dataset_segmentation' is valid
# e.g., if script is in 'AIvsHumanComparisonTool/scripts/', dataset is in 'AIvsHumanComparisonTool/yolo_dataset_segmentation/'
DATASET_BASE_DIR = "yolo_dataset_segmentation"
TEST_IMAGE_DIR = os.path.join(DATASET_BASE_DIR, "images", "test")
JSON_DIR = os.path.join("AI", "data")

# Output directory for images with drawn segmentations
# This will be created relative to where the script is run.
OUTPUT_VISUALIZATION_DIR = "AI/output/segmentation"

CONF_THRESHOLD = 0.50  # Confidence threshold for displaying detections

# Class names for labeling (should match your YAML)
CLASS_NAMES = [
    '11', '12', '13', '14', '15', '16', '17', '18',
    '21', '22', '23', '24', '25', '26', '27', '28',
    '31', '32', '33', '34', '35', '36', '37', '38',
    '41', '42', '43', '44', '45', '46', '47', '48'
]

USE_BLUR = False


def run_inference_on_test_set(model: YOLO, image_dir, output_dir, conf_threshold):
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
        base_filename = os.path.splitext(image_name)[0]
        json_path = os.path.join(JSON_DIR, base_filename, base_filename + ".json")
        print(f"\nProcessing image: {image_path}")

        try:
            image_cv = cv2.imread(image_path)
            if image_cv is None:
                print(f"Warning: Could not read image {image_path}. Skipping.")
                continue

            H, W, _ = image_cv.shape

            # Run inference over the image
            results = model.predict(source=image_path, verbose=False, retina_masks=True, imgsz=1024)[0]

            # Prepare class info & deterministic colors per class
            random.seed(42)  # reproducible colors
            yolo_classes = list(model.names.values())
            colors = {cls_id: random.sample(range(256), 3) for cls_id, _ in enumerate(yolo_classes)}

            # Load image (BGR for OpenCV drawing)
            image_cv = cv2.imread(image_path)
            h, w = image_cv.shape[:2]

            # Drawing parameters
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            font_thickness = 2

            for result in results:
                # Get image dimensions once per result
                H, W = image_cv.shape[:2]

                for i, (poly, box) in enumerate(zip(result.masks.xy, result.boxes)):
                    confidence = box.conf[0].item()
                    if confidence < conf_threshold:
                        continue  # Skip low-confidence detections

                    cls_id = int(box.cls[0])
                    class_name = yolo_classes[cls_id]
                    mask_color = colors[cls_id]

                    # ----- Use the per-pixel mask directly (result.masks.data) -----
                    # mask_tensor has shape (h0, w0); we need to resize it to (H, W)
                    mask_tensor = result.masks.data[i]  # torch tensor of shape (h0, w0), values 0 or 1
                    mask_np = (mask_tensor.cpu().numpy().astype(np.uint8)) * 255  # now uint8, shape (h0, w0)

                    # Resize mask to match original image size (W, H)
                    binary_mask = cv2.resize(mask_np, (W, H), interpolation=cv2.INTER_LINEAR)

                    # ----- Smooth the binary mask with Gaussian blur -----
                    # You can adjust kernel size for more or less smoothing. Here, (21, 21) is an example.
                    if USE_BLUR:
                        blurred_mask = cv2.GaussianBlur(binary_mask, (21, 21), 0)
                    else:
                        # If blur is disabled, use the raw binary mask directly
                        blurred_mask = binary_mask

                    # ----- Build an alpha map in [0.0 .. 1.0] from the blurred mask -----
                    alpha = (blurred_mask.astype(np.float32) / 255.0)[..., None]  # shape (H, W, 1)

                    # ----- Create a flat color layer of the mask color -----
                    colored_layer = np.zeros_like(image_cv, dtype=np.uint8)
                    colored_layer[:] = mask_color  # fill with (B, G, R)

                    # ----- Composite the colored layer onto image_cv using the alpha map -----
                    max_interior_opacity = 0.6
                    alpha = alpha * max_interior_opacity
                    image_cv = (
                            alpha * colored_layer.astype(np.float32) +
                            (1.0 - alpha) * image_cv.astype(np.float32)
                    ).astype(np.uint8)

                    # ----- Bounding-box coords & center -----
                    x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                    cx = (x1 + x2) // 2
                    cy = (y1 + y2) // 2

                    # ----- Compute label placement (centered) -----
                    (text_w, text_h), baseline = cv2.getTextSize(
                        class_name, font, font_scale, font_thickness
                    )
                    top_left_x = cx - text_w // 2
                    top_left_y = cy - text_h // 2

                    # Ensure the text is fully inside the image bounds
                    top_left_x = max(0, min(top_left_x, w - text_w - 1))
                    top_left_y = max(0, min(top_left_y, h - text_h - 1))
                    label_origin = (top_left_x, top_left_y + text_h)

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

            # Save the result with smoothed, non-blocky masks
            image_base_filename, image_ext = os.path.splitext(image_name)
            os.makedirs(os.path.join(output_dir, image_base_filename), exist_ok=True)
            output_image_path = os.path.join(output_dir, image_base_filename, f"contoured_{image_name}")
            original_data_comparison_path = os.path.join(output_dir, image_base_filename)
            cv2.imwrite(output_image_path, image_cv)

            apply_json_mask_to_image(
                image_path=image_path,
                json_path=json_path,
                output_path=original_data_comparison_path,
                mask_color=(0, 255, 0),
                overlay_alpha=0.5  # 50% tint
            )

        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            import traceback
            traceback.print_exc()

        break


if __name__ == "__main__":
    try:
        yolo_model: YOLO = YOLO(MODEL_PATH)
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
