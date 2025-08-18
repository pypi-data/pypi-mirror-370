# Standard library imports
import abc
import os
from pathlib import Path
from datetime import datetime

#Third-party 
import torch
from torch.utils.tensorboard import SummaryWriter

# Local application
from .utils.logger import get_logger


Path(__file__).resolve().parent.parent

class BaseTrainer(abc.ABC):
    """
    BaseTrainer - Abstract Base Class for Machine Learning Training

    This module provides an abstract base class for training machine learning models
    with PyTorch. It includes common functionality for training loops, validation,
    logging, checkpointing, and TensorBoard integration.

    Features:
        - Abstract training and validation step methods for customization
        - Automatic device detection (CUDA/CPU)
        - Integrated logging with configurable log directories
        - Model checkpointing with timestamp-based naming
        - TensorBoard integration for training visualization
        - Configurable model saving/loading functionality
        - Automatic data type handling for different loss functions

    Usage:
        Inherit from BaseTrainer and implement the abstract methods:
        - training_step(batch): Define how to process a training batch
        - validation_step(batch): Define how to process a validation batch

    Example:
        class MyTrainer(BaseTrainer):
            def training_step(self, batch):
                inputs, labels = self.prepare_batch(*batch)
                outputs = self.model(inputs)
                return self.loss_fn(outputs, labels)
            
            def validation_step(self, batch):
                inputs, labels = self.prepare_batch(*batch)
                outputs = self.model(inputs)
                return self.loss_fn(outputs, labels)

    Key methods:
    - __init__: Initializes the trainer with model, data loaders, optimizer, loss function, 
      and other configuration parameters.
    - save_model: Saves the trained model to the specified directory.
    - load_model: Loads a previously saved model.
    - prepare_batch: Prepares inputs and labels for training, adjusting them for the 
      specific loss function.
    - training_step: Abstract method to define the training step (to be implemented in subclasses).
    - validation_step: Abstract method to define the validation step (to be implemented in subclasses).
    - train_one_epoch: Handles one epoch of training, including loss calculation and optimization.
    - validate: Evaluates the model on the validation dataset.
    - run: Executes the full training process for the specified number of epochs.


    """
    def __init__(
        self,
        model,
        train_loader,
        val_loader,
        optimizer,
        loss_fn,
        epochs=10,
        device=None,
        log_dir=None,
        checkpoint_path=None,
        log_name="trainer", # could be removed and be replaced by task name
        config = None
    ):
        self.config = config or {}
        self.device = device or torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        self.model = model.to(self.device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.optimizer = optimizer
        self.loss_fn = loss_fn
        self.epochs = epochs
        self.logger, _ = get_logger(name=log_name, log_dir=log_dir or "logs")

        if checkpoint_path:
            self.checkpoint_path = checkpoint_path
        else:
            checkpoint_dir = Path.cwd() / "checkpoints"
            checkpoint_dir.mkdir(parents=True, exist_ok=True)
            filename = f"model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pt"
            self.checkpoint_path = str(checkpoint_dir / filename)

        self.writer = SummaryWriter(
            log_dir or f"runs/train_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        self.best_val_loss = float("inf")

        self.logger.info(f"Device: {self.device}")
        self.logger.info(f"Model: {model}")
        self.logger.info(f"Training set size: {len(train_loader.dataset)}")
        self.logger.info(f"Validation set size: {len(val_loader.dataset)}")

        self.save_model_flag = self.config.get("save_model", False)
        self.load_model_flag = self.config.get("load_model", False)
        self.model_dir = self.config.get("model_dir", "checkpoints")
        self.model_path = os.path.join(self.model_dir, "model.pt")

        if self.load_model_flag:
            self.load_model()

    
    def save_model(self):
        if hasattr(self.model, "save"):
            Path(self.model_dir).mkdir(parents=True, exist_ok=True)
            self.model.save(self.model_path)
            self.logger.info(f"Model saved via .save() to {self.model_path}")

        else:
            self.logger.warning("Model has no `.save()` method.")

    def load_model(self):
        if hasattr(self.model, "load"):
            self.model.load(self.model_path)
            self.logger.info(f"Model loaded via .load() from {self.model_path}")
        else:
            self.logger.warning("Model has no `.load()` method.")


    def prepare_batch(self, inputs, labels):
        inputs = inputs.to(self.device)
        labels = labels.to(self.device)

        if isinstance(self.loss_fn, torch.nn.CrossEntropyLoss):
            labels = labels.long()
        elif isinstance(
            self.loss_fn,
            (torch.nn.MSELoss, torch.nn.BCELoss, torch.nn.BCEWithLogitsLoss),
        ):
            labels = labels.float()

        return inputs, labels

    @abc.abstractmethod
    def training_step(self, batch):
        raise NotImplemented

    @abc.abstractmethod
    def validation_step(self, batch):
        raise NotImplemented

    def train_one_epoch(self, epoch_index):
        self.model.train()
        total_loss = 0.0    # full epoch loss
        running_loss = 0.0
        num_batches = 0

        for i, batch in enumerate(self.train_loader):
            loss = self.training_step(batch)  # self.model.training_step(batch)
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

            running_loss += loss.item()
            total_loss += loss.item()
            num_batches += 1

        return total_loss / num_batches

    def validate(self):
        self.model.eval()
        total_loss = 0.0
        num_batches = 0
        with torch.no_grad():
            for batch in self.val_loader:
                loss = self.validation_step(batch)
                total_loss += loss.item()
                num_batches += 1
        return total_loss / num_batches


    def run(self):
        for epoch in range(self.epochs):
            self.logger.info(f"--- Epoch {epoch + 1}/{self.epochs} ---")
            train_loss = self.train_one_epoch(epoch)
            val_loss = self.validate()
            self.writer.add_scalars(
                "Loss", {"Train": train_loss, "Validation": val_loss}, epoch + 1
            )
            self.logger.info(
                f"Epoch {epoch + 1}: Train Loss = {train_loss:.4f}, Val Loss = {val_loss:.4f}"
            )

        if self.save_model_flag:
            self.save_model()

        return self.model

            
