import os
from PIL import Image
from torch.utils.data import Dataset
import numpy as np
import rasterio


class DeterDataset(Dataset):
    def __init__(self, image_dir, mask_dir, transform=None):
        self.image_dir = image_dir
        self.mask_dir = mask_dir
        self.transform = transform
        self.images = os.listdir(image_dir)

    def __len__(self):
        return len(self.images)

    def __getitem__(self, index):
        img_path = os.path.join(self.image_dir, self.images[index])
        mask_path = os.path.join(self.mask_dir, self.images[index].replace('_bands.tif', '.tif'))

        with rasterio.open(img_path) as src:
            # Optional: Read and print data for each band
            band1 = src.read(1)  # Read the first band
            band2 = src.read(2)  # Read the second band
            band3 = src.read(3)  # Read the third band
            band4 = src.read(4)  # Read the third band

        image = np.stack((band1, band2, band3, band4), axis=-1)

        with rasterio.open(mask_path) as src:
            mask = src.read(1)

        if self.transform is not None:
            augmentations = self.transform(image=image, mask=mask)
            image = augmentations['image']
            mask = augmentations['mask']

        return image, mask
