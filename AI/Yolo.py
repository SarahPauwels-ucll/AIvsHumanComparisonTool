import json
import os
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
model = YOLO('runs/detect/train/weights/best.pt')

# --- STEP 1: Load Ground Truth from JSON ---
def load_ground_truth_labels(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    present_teeth = set(shape['label'] for shape in data['shapes'])
    return present_teeth

# --- STEP 2: Run YOLO Inference ---
# --- STEP 2: Run YOLO Inference and Show ---
def detect_teeth(image_path):
    results = model(image_path)[0]

    # Show image with YOLO bounding boxes
    results.show()

    # Optionally save it
    results.save(filename='annotated_output.jpg')

    predicted_teeth = set()

    # Mapping YOLO class ID to tooth number
    for box in results.boxes.data.tolist():
        class_id = int(box[5])
        tooth_num = 11 + (class_id // 2) if class_id // 2 < 18 else 31 + (class_id // 2 - 18)
        predicted_teeth.add(str(tooth_num))

    return predicted_teeth


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
