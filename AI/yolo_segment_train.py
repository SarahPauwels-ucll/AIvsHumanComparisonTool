from multiprocessing import freeze_support
from ultralytics import YOLO
import torch

if __name__ == "__main__":
    freeze_support()
    model = YOLO("runs/segment/train7/weights/last.pt")
    if torch.cuda.is_available():
        model.to("cuda")
        gpu_name = torch.cuda.get_device_name(0)
        print(f"Using GPU {gpu_name} for training")
    else:
        print("CUDA not detected, using CPU for training")
    #model.train(data="AI/yolo_segments.yaml",
    model.train(data="AI/yolo_segments_aug.yaml",
                epochs=300,
                imgsz=1024,
                batch=6,
                nbs=32,
                cache="disk",
                copy_paste=0.5,
                mask_ratio=1 # determines the downscaling factor during training. Set to 1 (default 4) to (hopefully) reduce blockiness.
                )
