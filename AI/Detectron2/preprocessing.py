import json
import os
import numpy as np
from PIL import Image

# the labelme json does include imageHeight, imageWidth, imagePath and imageData. imagePath should NOT be used however, as it is sometimes incorrect. the image is in a folder with its casename, next to the json. both image and json have the same name.


all_tooth_labels = [
    "11", "12", "13", "14", "15", "16", "17", "18",
    "21", "22", "23", "24", "25", "26", "27", "28",
    "31", "32", "33", "34", "35", "36", "37", "38",
    "41", "42", "43", "44", "45", "46", "47", "48"
]

coco_categories = []
label_to_category_id = {}
for i, label_name in enumerate(all_tooth_labels):
    coco_categories.append({"id": i, "name": label_name, "supercategory": "tooth"})
    label_to_category_id[label_name] = i


