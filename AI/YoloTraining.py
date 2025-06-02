from ultralytics import YOLO

model = YOLO("runs/detect/train/weights/best.pt")  # Start from pretrained nano model
model.train(data="AI/yolo_teeth.yaml", epochs=50, imgsz=640, batch=8)