import os
import cv2
import numpy as np
def parse_yolo_polygon_txt(txt_path, img_width, img_height):
    """
    Parses YOLO polygon format:
    class_id x1 y1 x2 y2 x3 y3 ... (all normalized)
    Returns a list of polygons (list of points in pixel coords)
    """
    polygons = []
    with open(txt_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 3 or (len(parts) - 1) % 2 != 0:
                continue  # Not valid polygon line
            class_id = parts[0]
            coords = parts[1:]
            points = []
            for i in range(0, len(coords), 2):
                x_norm = float(coords[i])
                y_norm = float(coords[i+1])
                x_px = int(round(x_norm * img_width))
                y_px = int(round(y_norm * img_height))
                points.append([x_px, y_px])
            polygons.append(np.array(points, dtype=np.int32))
    return polygons


def apply_polygon_mask_from_yolo_txt(image_path, txt_path, output_path, mask_color=(0,255,0), overlay_alpha=0.5):
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Could not read image at {image_path}")
    H, W = image.shape[:2]
    print(f"Image loaded: {image_path} (W={W}, H={H})")

    polygons = parse_yolo_polygon_txt(txt_path, W, H)
    print(f"Found {len(polygons)} polygons")

    binary_mask = np.zeros((H, W), dtype=np.uint8)
    for i, poly in enumerate(polygons):
        print(f" Polygon {i} with {len(poly)} points")
        cv2.fillPoly(binary_mask, [poly], 255)

    print(f"Mask unique values after drawing: {np.unique(binary_mask)}")
    cv2.imwrite(os.path.join(output_path, "debug_binary_mask.png"), binary_mask)

    masked_only = cv2.bitwise_and(image, image, mask=binary_mask)
    base, ext = os.path.splitext(os.path.basename(image_path))
    save_masked = os.path.join(output_path, f"{base}_masked_only{ext}")
    cv2.imwrite(save_masked, masked_only)

    color_layer = np.zeros_like(image)
    color_layer[:] = mask_color
    alpha_map = (binary_mask.astype(np.float32) / 255.0)[..., None] * overlay_alpha
    overlayed = (
        alpha_map * color_layer.astype(np.float32) +
        (1.0 - alpha_map) * image.astype(np.float32)
    ).astype(np.uint8)
    save_overlay = os.path.join(output_path, f"{base}_with_overlay{ext}")
    cv2.imwrite(save_overlay, overlayed)

    print(f"Saved masked image: {save_masked}")
    print(f"Saved overlay image: {save_overlay}")
    print(f"Saved binary mask image: debug_binary_mask.png")




if __name__ == "__main__":
    base_folder = "yolo_dataset_augmented_extra_data_bone_seg"
    name = "1_1_aug_004"
    img_path = os.path.join(base_folder, "images", f"{name}.jpg")
    label_path = os.path.join(base_folder, "labels", f"{name}.txt")
    output_dir = os.path.join("output", "segmentation")
    os.makedirs(output_dir, exist_ok=True)

    apply_polygon_mask_from_yolo_txt(
        image_path=img_path,
        txt_path=label_path,
        output_path=output_dir,
        mask_color=(0, 255, 0),
        overlay_alpha=0.5
    )