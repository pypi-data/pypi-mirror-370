# Standard library
import abc
from pathlib import Path

# Third-party
import requests
from torch.utils.data import DataLoader, random_split, Dataset


class BaseDataset(abc.ABC):
    """
    BaseDataset - Abstract Base Class for Dataset Management

    This module provides an abstract base class for managing datasets in machine learning
    workflows. It handles data loading, train/validation splitting, and DataLoader creation
    with configurable parameters for batch processing and multi-threading.

    Features:
        - Abstract dataset loading interface for extensible dataset types
        - Automatic train/validation splitting with configurable ratios
        - DataLoader creation with batch processing and multi-threading support
        - Flexible configuration management for dataset parameters
        - Shuffling control for training and validation sets
        - Support for custom batch sizes and worker processes

    Key methods:
        - **__init__**: Initializes the dataset with configuration parameters including
        batch size, split ratio, number of workers, and shuffle settings.
        - get_dataloaders: Creates and returns train and validation DataLoaders with
        automatic dataset splitting and appropriate configurations.
        - load_dataset: Abstract method to be implemented by subclasses for loading
        the actual dataset (must return a PyTorch Dataset instance).

    Usage:
        class MyDataset(BaseDataset):
            def load_dataset(self):
                # Load your specific dataset here
                return CustomDataset(self.config)
        
        # Create dataset instance
        config = {"data_path": "/path/to/data", "transform": True}
        dataset = MyDataset(config, batch_size=64, split_ratio=0.9)


    Architecture:
        BaseDataset follows the template method pattern where:
        1. Common functionality (splitting) is implemented in the base class
        2. Dataset-specific loading logic is delegated to subclasses via load_dataset()
        3. Configuration and parameters are managed centrally for consistency

    Dependencies:
        - torch.utils.data: PyTorch data utilities for DataLoader and Dataset handling
        - requests: HTTP library for potential data downloading functionality
        - pathlib: Modern path handling utilities

    License: [Your License]
    """

    def __init__(self, config, batch_size=32, split_ratio=0.8, num_workers=0, *, shuffle=True):
        self.config = config
        self.batch_size = batch_size
        self.split_ratio = split_ratio
        self.num_workers = num_workers
        self.shuffle = shuffle

    def get_dataloaders(self) -> tuple[DataLoader, DataLoader]:
        dataset = self.load_dataset()
        train_size = int(self.split_ratio * len(dataset))
        val_size = len(dataset) - train_size
        train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
        return (
            DataLoader(
                train_dataset,
                batch_size=self.batch_size,
                shuffle=self.shuffle,
                num_workers=self.num_workers,
            ),
            DataLoader(
                val_dataset,
                batch_size=self.batch_size,
                shuffle=False,
                num_workers=self.num_workers,
            ),
        )

    @abc.abstractmethod
    def load_dataset(self):
        """Must be implemented in the subclass."""
        msg = "Subclasses must implement load_dataset()"
        raise NotImplementedError(msg)
