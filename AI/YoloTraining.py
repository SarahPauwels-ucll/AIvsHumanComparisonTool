from multiprocessing import freeze_support
from ultralytics import YOLO

if __name__ == "__main__":
    freeze_support()
    model = YOLO("runs/detect/train/weights/best.pt")
    model.to("cuda")
    model.train(data="AI/yolo_teeth.yaml", epochs=500, imgsz=640, batch=8)
