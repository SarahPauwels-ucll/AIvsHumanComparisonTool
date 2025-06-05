import os
import json
import cv2
import numpy as np

def apply_json_mask_to_image(image_path, json_path, output_path, mask_color=(0, 255, 0), overlay_alpha=0.5):
    """
    1) Loads an image from `image_path`.
    2) Loads its annotation from `json_path`, expecting a top‐level "shapes" list where each shape has:
         - "label"    (ignored for masking, but available if you want per‐class masks)
         - "points":  a list of [x, y] float coordinates forming a polygon.
    3) Builds a binary mask that fills each polygon (255 inside, 0 outside).
    4) (Option A) Writes out a “masked only” image where only the polygon region remains.
    5) (Option B) Also writes out an “overlay” image where the polygon is tinted with `mask_color` at alpha=overlay_alpha.
    6) Saves both images under `output_path`.

    - mask_color:  BGR tuple for overlay (default green).
    - overlay_alpha: how strong the overlay is (0.0 = transparent, 1.0 = fully solid color).
    """
    # 1) Load image
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Could not read image at {image_path}")
    H, W = image.shape[:2]

    # 2) Load JSON annotation
    with open(json_path, "r") as f:
        data = json.load(f)

    # Create a blank single‐channel mask of the same size
    binary_mask = np.zeros((H, W), dtype=np.uint8)

    # 3) For each “shape” (polygon) in JSON, fill it into binary_mask
    for shape in data.get("shapes", []):
        pts = shape.get("points", None)
        if pts is None:
            continue

        # Convert list of [x, y] floats → int32 array of shape (n_points, 1, 2)
        pts_arr = np.array(pts, dtype=np.float32)
        pts_arr = np.round(pts_arr).astype(np.int32)
        pts_arr = pts_arr.reshape((-1, 1, 2))

        cv2.fillPoly(binary_mask, [pts_arr], 255)

    # 4) Option A: “Masked only” = keep only pixels under the polygon(s)
    #    (all other pixels become black)
    masked_only = cv2.bitwise_and(image, image, mask=binary_mask)
    #    Save it
    base, ext = os.path.splitext(os.path.basename(image_path))
    save_masked_only = os.path.join(output_path, f"{base}_masked_only{ext}")
    cv2.imwrite(save_masked_only, masked_only)
    print(f"Saved masked‐only image to: {save_masked_only}")

    # 5) Option B: “Overlay” = tint the original with mask_color at alpha
    #    First build a 3‐channel color fill where mask=255 → mask_color, mask=0 → ignored
    color_layer = np.zeros_like(image, dtype=np.uint8)
    color_layer[:] = mask_color  # broadcast to entire image

    # Convert binary_mask → float alpha in [0..1]
    alpha_map = (binary_mask.astype(np.float32) / 255.0)[..., None]  # shape (H, W, 1)
    alpha_map = alpha_map * overlay_alpha

    # Composite:   out = alpha_map * color_layer + (1 - alpha_map) * original
    overlayed = (
        alpha_map * color_layer.astype(np.float32)
        + (1.0 - alpha_map) * image.astype(np.float32)
    ).astype(np.uint8)

    save_overlay = os.path.join(output_path, f"{base}_with_overlay{ext}")
    cv2.imwrite(save_overlay, overlayed)
    print(f"Saved overlay image to: {save_overlay}")

    # 6) Return both results (in case you want to further process them)
    return masked_only, overlayed


if __name__ == "__main__":

    folder = "data/530425V033"
    fname = "530425V033"
    img_path = os.path.join(folder, fname + ".jpg")
    json_path = os.path.join(folder, fname + ".json")
    out_folder = os.path.join("output", "segmentation")
    os.makedirs(out_folder, exist_ok=True)

    apply_json_mask_to_image(
        image_path=img_path,
        json_path=json_path,
        output_path=out_folder,
        mask_color=(0, 255, 0),
        overlay_alpha=0.5
    )