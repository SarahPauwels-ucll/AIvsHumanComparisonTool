from multiprocessing import freeze_support
from ultralytics import YOLO
import torch

if __name__ == "__main__":
    freeze_support()
    model = YOLO("yolo12m.pt")
    if torch.cuda.is_available():
        model.to("cuda")
        gpu_name = torch.cuda.get_device_name(0)
        print(f"Using GPU {gpu_name} for training")
    else:
        print("CUDA not detected, using CPU for training")
    model.train(data="AI/yolo_teeth.yaml", epochs=500, imgsz=640, batch=8)
