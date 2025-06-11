import torch
from ultralytics import YOLO
from multiprocessing import freeze_support

if __name__ == "__main__":
    freeze_support()

    # Load model: choose a base YOLOv8 segmentation model or a checkpoint
    model = YOLO("runs/bone_segmentation/train2/weights/last.pt")  # You can switch to yolov8s-seg.pt, yolov8m-seg.pt, etc.

    # Use GPU if available
    if torch.cuda.is_available():
        model.to("cuda")
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("CUDA not detected, using CPU")

    # Train the model
    model.train(
        project="runs/bone_segmentation",
        data="AI/BoneSeg/bone_seg.yaml",  # Make sure this path and YAML content are correct
        epochs=200,
        resume=True,
        imgsz=1024,
        batch=4,
        cache="disk",
        copy_paste=0.5,
        mask_ratio=2
    )