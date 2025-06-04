import json
import os
import numpy as np
import io
import cv2
import torch
from ultralytics import YOLO
from PIL import Image

# def is_package_installed(package_name):
#     return importlib.util.find_spec(package_name) is not None
#
# # Install ultralytics (YOLOv8) if not already installed
# if not is_package_installed("ultralytics"):
#     print("🔄 Installing YOLOv8 (ultralytics)...")
#     subprocess.check_call(["pip", "install", "ultralytics"])
# else:
#     print("✅ YOLOv8 (ultralytics) is already installed.")

# Load trained YOLO model
model = YOLO('runs/detect/train2/weights/best.pt')
if torch.cuda.is_available():
    model.to("cuda")
    gpu_name = torch.cuda.get_device_name(0)
    print(f"Using GPU {gpu_name} for inference")
else:
    print("CUDA not detected, using CPU for inference")

# --- STEP 1: Load Ground Truth from JSON ---
def load_ground_truth_labels(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    present_teeth = set(shape['label'] for shape in data['shapes'])
    return present_teeth

# --- STEP 2: Run YOLO Inference ---
def detect_teethAISlop(image_source, conf_threshold=0.40, save_path='filtered_output.jpg'):
    """
    image_source: can be a file path (str) or image bytes
    """
    if isinstance(image_source, bytes):
        # Convert bytes to OpenCV image
        pil_image = Image.open(io.BytesIO(image_source)).convert("RGB")
        image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        results = model(pil_image)[0]  # Run YOLO on PIL image directly
    elif isinstance(image_source, str):
        image = cv2.imread(image_source)
        results = model(image_source)[0]  # Run YOLO on file path
    else:
        raise ValueError("image_source must be a file path or image bytes")

    detected_teeth = []

    for box in results.boxes.data.tolist():
        x1, y1, x2, y2, conf, class_id = box
        if conf < conf_threshold:
            continue

        class_id = int(class_id)

        if class_id < 8:
            tooth_num = 11 + class_id
        elif class_id < 16:
            tooth_num = 21 + (class_id - 8)
        elif class_id < 24:
            tooth_num = 31 + (class_id - 16)
        else:
            tooth_num = 41 + (class_id - 24)

        detected_teeth.append({
            "tooth": str(tooth_num),
            "confidence": round(conf, 3)
        })

        p1, p2 = (int(x1), int(y1)), (int(x2), int(y2))
        cv2.rectangle(image, p1, p2, (0, 255, 0), 2)
        label = f"{tooth_num} {conf:.2f}"
        cv2.putText(image, label, (p1[0], p1[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.imwrite(save_path, image)

    return detected_teeth
# --- STEP 2: Run YOLO Inference and Show ---
def detect_teeth(image_path, conf_threshold=0.40, save_path='filtered_output.jpg'):
    results = model(image_path)[0]
    image = cv2.imread(image_path)

    detected_teeth = []

    for box in results.boxes.data.tolist():
        x1, y1, x2, y2, conf, class_id = box
        if conf < conf_threshold:
            continue

        class_id = int(class_id)

        # Map YOLO class index to FDI tooth number
        if class_id < 8:
            tooth_num = 11 + class_id      # 11–18
        elif class_id < 16:
            tooth_num = 21 + (class_id - 8)  # 21–28
        elif class_id < 24:
            tooth_num = 31 + (class_id - 16) # 31–38
        else:
            tooth_num = 41 + (class_id - 24) # 41–48

        detected_teeth.append({
            "tooth": str(tooth_num),
            "confidence": round(conf, 3)
        })

        # Draw box
        p1, p2 = (int(x1), int(y1)), (int(x2), int(y2))
        cv2.rectangle(image, p1, p2, (0, 255, 0), 2)
        label = f"{tooth_num} {conf:.2f}"
        cv2.putText(image, label, (p1[0], p1[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Save filtered result
    cv2.imwrite(save_path, image)

    return detected_teeth



# --- STEP 3: Compare and Output Results ---
def evaluate(image_path, json_path):
    ground_truth = load_ground_truth_labels(json_path)  # e.g., ['11', '12', '13', ...]
    detections = detect_teeth(image_path)  # [{'tooth': '21', 'confidence': 0.812}, ...]

    # Extract unique detected tooth numbers as strings
    detected_teeth = set([d['tooth'] for d in detections])

    print(f"\n📸 Evaluating image: {image_path}")
    print(f"✅ Detected Teeth: {detected_teeth}")
    print(f"📋 Ground Truth: {ground_truth}\n")

    all_teeth = list(range(11, 19)) + list(range(21, 29)) + list(range(31, 39)) + list(range(41, 49))

    for tooth in all_teeth:
        tooth_str = str(tooth)
        in_ground_truth = tooth_str in ground_truth
        is_detected = tooth_str in detected_teeth

        if in_ground_truth and is_detected:
            print(f"✅ Tooth {tooth}: correctly detected")
        elif in_ground_truth and not is_detected:
            print(f"❌ Tooth {tooth}: not detected")
        elif not in_ground_truth and is_detected:
            print(f"❌ Tooth {tooth}: falsely detected")
        else:
            print(f"Tooth {tooth}: missing (not expected and not detected)")

def get_teeth_presence(image_path, confidence_threshold=0.5):
    detections = detect_teeth(image_path)  # [{'tooth': '21', 'confidence': 0.812}, ...]

    # Filter and extract tooth numbers above confidence threshold
    detected_teeth = set(
        d['tooth'] for d in detections if d['confidence'] >= confidence_threshold
    )

    all_teeth = set(str(t) for t in (
        list(range(11, 19)) + list(range(21, 29)) +
        list(range(31, 39)) + list(range(41, 49))
    ))

    present_teeth = sorted(list(detected_teeth & all_teeth))
    missing_teeth = sorted(list(all_teeth - detected_teeth))

    return present_teeth, missing_teeth
def get_teeth_presenceAISlop(image_source, confidence_threshold=0.5):
    """
    Accepts either image path (str) or image bytes (bytes)
    """
    detections = detect_teethAISlop(image_source, conf_threshold=confidence_threshold)

    detected_teeth = set(
        d['tooth'] for d in detections if d['confidence'] >= confidence_threshold
    )

    all_teeth = set(str(t) for t in (
        list(range(11, 19)) + list(range(21, 29)) +
        list(range(31, 39)) + list(range(41, 49))
    ))

    present_teeth = sorted(list(detected_teeth & all_teeth))
    missing_teeth = sorted(list(all_teeth - detected_teeth))

    return present_teeth, missing_teeth

# Example Usage
# image_path = 'AI/data/650228V319/650228V319.jpeg'
# json_path = 'AI/data/650228V319/650228V319.json'
#
# evaluate(image_path, json_path)
# print(get_teeth_presence(image_path, confidence_threshold=0))