import os
import glob
from PIL import Image
import torch
from torchvision import transforms
from torch.utils.data import Dataset
import numpy as np

import timm

from ..base import BaseDataset
from ..tasks.task_registry import register_task
from ..tasks.task_factory import AbstractTaskFactory
from ..base import AbstractModelArchitecture
from ..trainer import BaseTrainer

import torch.nn as nn
import torch.nn.functional as F

import os
import urllib.request
import zipfile
import tarfile
from pathlib import Path

from albumentations.pytorch import ToTensorV2
import albumentations as A
from torchvision import transforms as T
from PIL import Image
import os
from pathlib import Path
from torch.utils.data import Dataset

class ImageSegmentationDataset(BaseDataset):
    def __init__(self, image_size=(128, 128), **kwargs):
        super().__init__(**kwargs)
        self.cfg = self.config
        self.image_size = image_size
        self.root_dir = Path(self.cfg.get("root_dir", "."))
        self.label_offset = self.cfg.get("label_offset", 0)
        self.ignore_label = self.cfg.get("ignore_label", None)
        self.split_ratio = self.cfg.get("split_ratio", 0.8)


        self.image_size = self.config.get("image_size", image_size)
        # Transforms
        tf_cfg = self.cfg.get("transforms", {})
        tf_lib = self.cfg.get("transform_lib", "albumentations")
        self.train_transform = self.build_transform_from_config(tf_cfg.get("train", []), lib=tf_lib)
        self.val_transform = self.build_transform_from_config(tf_cfg.get("val", []), lib=tf_lib)
        self.using_albumentations = (tf_lib == "albumentations")

    def build_transform_from_config(self, config_list, lib="albumentations"):
        if lib == "albumentations":
            available = {
                "Resize": A.Resize,
                "HorizontalFlip": A.HorizontalFlip,
                "VerticalFlip": A.VerticalFlip,
                "RandomBrightnessContrast": A.RandomBrightnessContrast,
                "Normalize": A.Normalize,
                "ToTensorV2": ToTensorV2,
            }
        else:
            available = {
                "Resize": T.Resize,
                "RandomHorizontalFlip": T.RandomHorizontalFlip,
                "RandomVerticalFlip": T.RandomVerticalFlip,
                "Normalize": T.Normalize,
                "ToTensor": T.ToTensor,
            }

        tfms = []
        for t in config_list:
            name = t["name"]
            params = t.get("params", {})
            tfms.append(available[name](**params) if params else available[name]())
        return A.Compose(tfms) if lib == "albumentations" else T.Compose(tfms)

    def load_dataset(self):
        image_dir = Path(self.cfg.get("image_dir"))
        mask_dir = Path(self.cfg.get("mask_dir"))

        if not image_dir.exists() or not mask_dir.exists():
            raise ValueError(f"Directories not found: {image_dir}, {mask_dir}")

        image_files = sorted(image_dir.glob("*"))
        mask_files = sorted(mask_dir.glob("*"))
        mask_dict = {f.stem: f for f in mask_files}
        matched = [(img, mask_dict[img.stem]) for img in image_files if img.stem in mask_dict]

        if len(matched) == 0:
            raise ValueError("No matching image-mask pairs found (pattern-based).")

        split_idx = int(len(matched) * self.split_ratio)
        train_pairs, val_pairs = matched[:split_idx], matched[split_idx:]

        class SegDataset(Dataset):
            def __init__(self, pairs, transform, use_albu, label_offset=0, ignore_label=None, image_size=(128, 128)):
                self.pairs = pairs
                self.transform = transform
                self.use_albu = use_albu
                self.label_offset = label_offset
                self.ignore_label = ignore_label
                self.image_size = image_size  # ✅ Add this line

            def __len__(self):
                return len(self.pairs)

            def __getitem__(self, idx):
                img_path, mask_path = self.pairs[idx]
                image = Image.open(img_path).convert("RGB")
                mask = Image.open(mask_path)

                image = image.resize(self.image_size)
                mask = mask.resize(self.image_size, Image.NEAREST)

                image_np = np.array(image)
                mask_np = np.array(mask)

                if self.use_albu:
                    augmented = self.transform(image=image_np, mask=mask_np)
                    image = augmented["image"]
                    mask = augmented["mask"].long()
                else:
                    image = self.transform(image)
                    mask = T.PILToTensor()(mask).squeeze(0).long()

                if self.label_offset:
                    mask = mask - self.label_offset
                if self.ignore_label is not None:
                    mask[mask < 0] = self.ignore_label

                return image, mask

        self.train_dataset = SegDataset(train_pairs, self.train_transform, self.using_albumentations,
            self.label_offset, self.ignore_label, self.image_size)
        self.val_dataset = SegDataset(val_pairs, self.val_transform, self.using_albumentations,
        self.label_offset, self.ignore_label, self.image_size)

        # return self.train_dataset, self.val_dataset
    def get_dataloaders(self):
        if not hasattr(self, "train_dataset") or not hasattr(self, "val_dataset"):
            self.load_dataset()

        train_loader = torch.utils.data.DataLoader(
            self.train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=4,
        )
        val_loader = torch.utils.data.DataLoader(
            self.val_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=4,
        )
        return train_loader, val_loader



class ImageSegmentationModel(AbstractModelArchitecture, nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Conv2d(3, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        )
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(32, 16, 2, stride=2), nn.ReLU(),
            nn.ConvTranspose2d(16, num_classes, 2, stride=2)
        )

    def forward(self, x):
        x = self.encoder(x)
        x = self.decoder(x)
        return x  # [B, num_classes, H, W]

    def save(self, path):
        torch.save(self.state_dict(), path)

    def load(self, path):
        self.load_state_dict(torch.load(path))
# class TimmSegmentationModel(nn.Module):
#     def __init__(self, model_name: str, num_classes: int, pretrained=True):
#         super().__init__()
#         self.encoder = timm.create_model(model_name, features_only=True, pretrained=pretrained)
#         encoder_channels = self.encoder.feature_info.channels()[-1]

#         self.decoder = nn.Sequential(
#             nn.Conv2d(encoder_channels, 256, 3, padding=1),
#             nn.ReLU(),
#             nn.Upsample(scale_factor=2, mode='bilinear', align_corners=False),
#             nn.Conv2d(256, 128, 3, padding=1),
#             nn.ReLU(),
#             nn.Upsample(scale_factor=2, mode='bilinear', align_corners=False),
#             nn.Conv2d(128, num_classes, 1)
#         )

#     def forward(self, x):
#         features = self.encoder(x)[-1]  # Use last feature map
#         return self.decoder(features)



class ImageSegmentationTrainer(BaseTrainer):
    def training_step(self, batch):
        x, y = self.prepare_batch(*batch)
        y_hat = self.model(x)
        return self.loss_fn(y_hat, y)

    def validation_step(self, batch):
        x, y = self.prepare_batch(*batch)
        y_hat = self.model(x)
        return self.loss_fn(y_hat, y)

@register_task("image_segmentation")
class ImageSegmentationFactory(AbstractTaskFactory):
    def create_dataset(self, config):
        dataset_cfg = config.get("dataset_config", {})
        return ImageSegmentationDataset(
            image_size=dataset_cfg.get("image_size", (128, 128)),
            batch_size=config.get("batch_size", 8),
            split_ratio=config.get("split_ratio", 0.8),
            config=dataset_cfg,
        )

    def create_model(self, config):
        # model_cfg = config.get("model_config", {})
        # if model_cfg.get("type") == "timm":
        #     model_name = model_cfg.get("name", "resnet34")
        #     pretrained = model_cfg.get("pretrained", True)
        #     return TimmSegmentationModel(
        #         model_name=model_name,
        #         num_classes=config.get("num_classes", 2),
        #         pretrained=pretrained
        #     )
        return ImageSegmentationModel(num_classes=config.get("num_classes", 2))
    

    def create_trainer(self, model, dataset, config):
        train_loader, val_loader = dataset.get_dataloaders()
        optimizer = torch.optim.Adam(model.parameters(), lr=config.get("lr", 1e-3))
        # loss_fn = torch.nn.CrossEntropyLoss()
        loss_fn = torch.nn.CrossEntropyLoss(ignore_index=255)
        return ImageSegmentationTrainer(
            model=model,
            train_loader=train_loader,
            val_loader=val_loader,
            optimizer=optimizer,
            loss_fn=loss_fn,
            epochs=config.get("epochs", 10),
            device=config.get("device", "cuda"),
            log_dir=config.get("log_dir", "logs"),
            checkpoint_path=config.get("checkpoint_path", None),
        )
