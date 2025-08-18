from dataclasses import dataclass, field
import os



@dataclass
class DatasetConfig:
    """Base configuration for datasets."""
    dataset_type: str = "clearml" # e.g., "clearml", "local", "download"
    name: str = "MNIST"
    project: str = "datasets"
    path: str = os.path.join(os.getcwd(), "data") # Default path for local/download
    download: bool = False
    
    # You can add more specific fields for transforms here,
    # or keep them as a dictionary for flexibility
    transform_config: dict = field(default_factory=lambda: {
        "resize": (28, 28),
        "grayscale": True,
        "normalize_mean": (0.5,),
        "normalize_std": (0.5,)
    })
    # Add any other dataset-specific parameters (e.g., credentials, URL)

@dataclass
class TrainingConfig:
    task: str = "no_task"
    batch_size: int = 32
    epochs: int = 10
    lr: float = 1e-3
    split_ratio: float = 0.8
    device: str = "cuda"  # or "cpu"
    checkpoint_path: str = None
    log_dir: str = os.path.join(os.getcwd(), "logs")
    dataset_config: DatasetConfig = field(default_factory=DatasetConfig)


# DEFAULT_CONFIG = TrainingConfig()
DEFAULT_CONFIG = {
    "task": None,
    "batch_size": 32,
    "epochs": 10,
    "lr": 1e-3,
    "split_ratio": 0.8,
    "device": "cuda",
    "log_dir": "logs",
    "checkpoint_path": None,
    "dataset_config": {},  # Still a plain dict
}

