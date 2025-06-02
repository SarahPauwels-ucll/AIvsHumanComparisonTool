import json
import os

import cv2
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

# --- STEP 1: Load Ground Truth from JSON ---
def load_ground_truth_labels(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    present_teeth = set(shape['label'] for shape in data['shapes'])
    return present_teeth

# --- STEP 2: Run YOLO Inference ---
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
    ground_truth = load_ground_truth_labels(json_path)
    detected_teeth = detect_teeth(image_path)
    print(detected_teeth)
    for tooth in range(11, 19):
        status = "Present" if str(tooth) in ground_truth else "Missing"
        print(f"Tooth {tooth}: {status}")
    for tooth in range(21, 29):
        status = "Present" if str(tooth) in ground_truth else "Missing"
        print(f"Tooth {tooth}: {status}")

    for tooth in range(31, 39):
        status = "Present" if str(tooth) in ground_truth else "Missing"
        print(f"Tooth {tooth}: {status}")

    for tooth in range(41, 49):
            status = "Present" if str(tooth) in ground_truth else "Missing"
            print(f"Tooth {tooth}: {status}")

# Example Usage
image_path = 'AI/data/450416V340/450416V340.jpeg'
json_path = 'AI/data/450416V340/450416V340.json'

evaluate(image_path, json_path)
