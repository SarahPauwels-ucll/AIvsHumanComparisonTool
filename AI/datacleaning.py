import numpy as np
import cv2
import torch
from torch.utils.data import Dataset
from torchvision import transforms
from PIL import Image

def generate_heatmap(img_size, points, sigma=2):
    num_points = len(points) // 2
    h, w = img_size
    heatmaps = np.zeros((num_points * 2, h, w), dtype=np.float32)

    for i in range(num_points * 2):
        x, y = points[i*2], points[i*2+1]
        if x < 0 or y < 0:
            continue
        heatmap = np.zeros((h, w), dtype=np.float32)
        cv2.circle(heatmap, (int(x), int(y)), sigma, 1, -1)
        heatmap = cv2.GaussianBlur(heatmap, (0, 0), sigma)
        heatmap = np.clip(heatmap, 0, 1)
        heatmaps[i] = heatmap
    return heatmaps


class TeethLineDataset(Dataset):
    def __init__(self, image_paths, keypoints, img_size=(256, 256)):
        self.image_paths = image_paths
        self.keypoints = keypoints
        self.img_size = img_size
        self.transform = transforms.Compose([
            transforms.Resize(img_size),
            transforms.ToTensor()
        ])

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img = Image.open(self.image_paths[idx]).convert('L')  
        img = self.transform(img)

        pts = self.keypoints[idx]  # 64 values
        heatmap = generate_heatmap(self.img_size, pts)
        heatmap = torch.tensor(heatmap, dtype=torch.float32)

        return img, heatmap
    
def extract_keypoints_from_heatmap(heatmaps):
    B, C, H, W = heatmaps.shape
    coords = []
    for i in range(B):
        image_coords = []
        for j in range(C):
            heatmap = heatmaps[i, j]
            y, x = torch.argmax(heatmap.view(-1), dim=0) // W, torch.argmax(heatmap.view(-1), dim=0) % W
            image_coords.extend([x.item(), y.item()])
        coords.append(image_coords)
    return coords   