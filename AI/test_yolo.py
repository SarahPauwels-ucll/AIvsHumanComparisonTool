from ultralytics import YOLO


def main():
    model = YOLO('runs/segment/train10/weights/best.pt')
    results = model.val(
        data="AI/yolo_segments_aug.yaml",
        split='test',
        imgsz=1024,
        save=True,
    )

    print("all mask metrics:")
    print(results.seg)

if __name__ == "__main__":
    main()