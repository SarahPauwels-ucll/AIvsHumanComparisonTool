from PIL import Image
import os

def flipImages():
    # Folder containing the images
    folder = "yolo_dataset_segmentation/images/train"

    image_extensions = (".jpg", ".jpeg")

    # Process each image
    for filename in os.listdir(folder):
        if filename.lower().endswith(image_extensions) and not filename.startswith("flip_"):
            img_path = os.path.join(folder, filename)
            img = Image.open(img_path)
            flipped = img.transpose(Image.FLIP_LEFT_RIGHT)

            name, ext = os.path.splitext(filename)
            output_filename = f"flip_{name}{ext}"
            output_path = os.path.join(folder, output_filename)

            flipped.save(output_path)


def fliplabel():
     # Folder containing the images
    folder = "yolo_dataset_segmentation/labels/train"


    file_extensions = (".txt")

    # Process each file
    for filename in os.listdir(folder):
        if filename.lower().endswith(file_extensions) and not filename.startswith("flip_"):
            name, ext = os.path.splitext(filename)
            input_path = os.path.join(folder, filename)
            output_file = f"flip_{name}{ext}"
            output_path = os.path.join(folder, output_file)

            with open(input_path, "r") as infile, open(output_path, "w") as outfile:
                for line in infile:
                    parts = line.strip().split()
                    if len(parts) < 3:
                        continue  # skip lines that don't have at least label + one (x,y)
                    label = parts[0]
                    label=int(label)
                    if label in [0,1,2,3,4,5,6,7,16, 17, 18, 19, 20, 21, 22, 23]:
                        label=int(label)+8
                    else:
                        label=int(label)-8
                    coords = list(map(float, parts[1:]))
                    mirrored_coords = []

                    # Loop over x,y pairs
                    for i in range(0, len(coords), 2):
                        x = coords[i]
                        y = coords[i + 1]
                        mirrored_x = 1 - x
                        mirrored_coords.extend([mirrored_x, y])
                    
                    # Schrijf naar outputfile
                    mirrored_line = str(label) + " " + " ".join(f"{val:.6f}" for val in mirrored_coords)
                    outfile.write(mirrored_line + "\n")
fliplabel()
flipImages()



