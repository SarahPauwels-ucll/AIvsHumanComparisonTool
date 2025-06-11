from ultralytics import YOLO


def main():
    model = YOLO('runs/segment/train10/weights/best.pt')
    metrics = model.val(
        data="AI/yolo_segments_aug.yaml",
        split='test',
        imgsz=1024,
        save=True,
    )
    print(metrics)


if __name__ == "__main__":
    main()