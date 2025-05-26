from torch.utils.data import DataLoader
import torch.optim as optim
from datacleaning import TeethLineDataset 

# Assuming image_paths and keypoints are lists
train_dataset = TeethLineDataset(image_paths, keypoints)
train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True)

model = UNetKeypoint()
model = model.cuda() if torch.cuda.is_available() else model
optimizer = optim.Adam(model.parameters(), lr=1e-4)
criterion = nn.MSELoss()

# Training loop
num_epochs = 5
for epoch in range(num_epochs):
    model.train()
    running_loss = 0.0
    for imgs, heatmaps in train_loader:
        imgs, heatmaps = imgs.to(model.device), heatmaps.to(model.device)

        optimizer.zero_grad()
        outputs = model(imgs)
        loss = criterion(outputs, heatmaps)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()

    print(f"Epoch {epoch+1}/{num_epochs}, Loss: {running_loss:.4f}")
