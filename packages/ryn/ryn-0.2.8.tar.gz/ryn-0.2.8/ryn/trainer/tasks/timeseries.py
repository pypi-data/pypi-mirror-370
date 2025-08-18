"""
Time Series Task - Complete Pipeline Implementation

This module provides a comprehensive time series analysis pipeline supporting multiple
tasks including forecasting, classification, imputation, and anomaly detection. It
integrates with the TSLib library for advanced time series models while providing
simple GRU-based models as fallbacks.

Features:
    - Multi-task support (forecasting, classification, imputation, anomaly detection)
    - Automatic sequence generation from time series data
    - Data normalization with MinMaxScaler
    - TSLib integration for state-of-the-art time series models
    - Custom GRU-based model for simple forecasting tasks
    - Flexible input/output handling for different task types
    - Configurable sequence and prediction lengths

Components:
    - TimeseriesDataset: Handles time series data loading and sequence generation
    - TimeseriesModel: Simple GRU-based model for basic forecasting
    - TsaiModelWrapper: Wrapper for TSLib models with task-specific routing
    - TimeseriesTrainer: Training logic adapted for time series tasks
    - TimeSeriesFactory: Factory for creating time series pipeline components

Key methods:
    Dataset:
        - **__init__**: Initializes dataset with sequence and prediction lengths
        - load_dataset: Loads CSV data, creates sequences, and applies normalization
    
    Models:
        - TimeseriesModel.__init__: Initializes GRU-based architecture
        - TsaiModelWrapper.__init__: Wraps TSLib models with task-specific logic
        - forward: Task-aware forward pass handling different input requirements
        - save/load: Model persistence methods
    
    Trainer:
        - prepare_batch: Task-specific batch preparation for different model inputs
        - training_step/validation_step: Forward pass with task-aware input handling
    
    Factory:
        - create_dataset: Creates dataset with sequence configuration
        - create_model: Selects between simple GRU or TSLib models
        - create_trainer: Assembles training pipeline with MSE loss

Usage:
    # Simple forecasting with GRU model
    config = {
        "task": "timeseries",
        "dataset_config": {
            "source": "path/to/timeseries.csv",
            "seq_len": 24,
            "pred_len": 6
        },
        "model_config": {
            "type": "simple"  # Uses TimeseriesModel
        },
        "batch_size": 32,
        "epochs": 100,
        "lr": 0.001
    }
    
    # Advanced forecasting with TSLib
    config = {
        "task": "timeseries",
        "dataset_config": {
            "source": "path/to/timeseries.csv",
            "seq_len": 96,
            "pred_len": 24
        },
        "model_config": {
            "type": "tslib",
            "name": "Transformer",
            "task_name": "long_term_forecast",
            "params": {
                "d_model": 128,
                "n_heads": 8,
                "e_layers": 3
            }
        }
    }
    
    trainer = AutoTrainer(config=config)
    trainer.run()

Supported Tasks:
    - long_term_forecast: Multi-step ahead forecasting
    - short_term_forecast: Single/few-step ahead forecasting
    - classification: Time series classification
    - imputation: Missing value imputation
    - anomaly_detection: Outlier detection in time series

TSLib Integration:
    The module integrates with TSLib (Time Series Library) to provide access to
    state-of-the-art models including:
    - Transformer variants for forecasting
    - Specialized models for each task type
    - Automatic experiment management and configuration

Architecture:
    The pipeline follows a flexible design:
    1. Dataset layer handles sequence generation and normalization
    2. Model layer provides both simple and advanced architectures
    3. Trainer layer adapts to different task input/output requirements
    4. Factory layer manages model selection and configuration


Dependencies:
    - torch: PyTorch deep learning framework
    - pandas: Data manipulation and CSV loading
    - numpy: Numerical computations
    - sklearn: Data preprocessing (MinMaxScaler)
    - tslib: Time Series Library for advanced models

"""

# third part imports
import torch
import pandas as pd
import numpy as np
from torch.utils.data import TensorDataset
from sklearn.preprocessing import MinMaxScaler

from types import SimpleNamespace

from .tslib.exp.exp_basic import Exp_Basic
from .tslib.exp.exp_long_term_forecasting import Exp_Long_Term_Forecast
from .tslib.exp.exp_short_term_forecasting import Exp_Short_Term_Forecast
from .tslib.exp.exp_imputation import Exp_Imputation
from .tslib.exp.exp_anomaly_detection import Exp_Anomaly_Detection
from .tslib.exp.exp_classification import Exp_Classification

# imports from the package
from ..base import BaseDataset, AbstractModelArchitecture
from ..trainer import BaseTrainer
from ..tasks.task_factory import AbstractTaskFactory
from ..tasks.task_registry import register_task


# -------------------------- Dataset ------------------------
class TimeseriesDataset(BaseDataset):
    def __init__(self, seq_len=12, pred_len=1, **kwargs):
        super().__init__(**kwargs)
        self.seq_len = seq_len
        self.pred_len = pred_len
        self.scaler = None  # To be used externally if needed
    
    

    
    def load_dataset(self):
        url = self.config["source"]
        df = pd.read_csv(url)
        values = df["Passengers"].values.astype("float32").reshape(-1, 1)

        # Normalize
        self.scaler = MinMaxScaler()
        values_scaled = self.scaler.fit_transform(values)

        # Create sequences
        X, Y = [], []
        for i in range(len(values_scaled) - self.seq_len - self.pred_len):
            X.append(values_scaled[i : i + self.seq_len])
            Y.append(values_scaled[i + self.seq_len : i + self.seq_len + self.pred_len])

        X = np.array(X)  # [samples, seq_len, 1]
        Y = np.array(Y)  # [samples, pred_len]

        X = torch.tensor(X, dtype=torch.float32)
        Y = torch.tensor(Y, dtype=torch.float32)

        batch_size = X.shape[0]
        X_mark = np.tile(np.array([[1, 1, 1, 0]]), (batch_size, self.seq_len, 1))  # [B, T, 4]
        X_mark = torch.tensor(X_mark, dtype=torch.float32)


        # return all three
        return TensorDataset(X, Y, X_mark)


        # return TensorDataset(X, Y)


# -------------------------- Model ------------------------
class TimeseriesModel(AbstractModelArchitecture, torch.nn.Module):
    def __init__(self, input_size=1, hidden_size=64, output_size=1):
        super().__init__()
        self.rnn = torch.nn.GRU(
            input_size=input_size, hidden_size=hidden_size, batch_first=True
        )
        self.fc = torch.nn.Linear(hidden_size, output_size)

    def forward(self, x):
        out, _ = self.rnn(x)  # out: [batch, seq_len, hidden]
        last_hidden = out[:, -1, :]  # take last timestep
        prediction = self.fc(last_hidden)
        return prediction
    
    def save(self, path):
        torch.save(self.state_dict(), path)

    def load(self, path):
        self.load_state_dict(torch.load(path))



def build_tsai_args(name: str, user_cfg: dict, config: dict) -> SimpleNamespace:
    defaults = {
        # core
        "model": name,
        "task_name": config.get("task_name", "classification"),
        "model_id": config.get("model_id", "default_model"),
        "data": config.get("data", "UEA"),
        "root_path": config.get("root_path", "./dataset/"),
        "checkpoints": config.get("checkpoints", "./checkpoints/"),

        # input/output
        "seq_len": config.get("seq_len", 12),
        "label_len": config.get("label_len", 12),
        "pred_len": config.get("pred_len", 1),
        "enc_in": config.get("input_channels", 1),
        "dec_in": config.get("input_channels", 1),
        "c_out": config.get("output_size", 1),
        "batch_size": config.get("batch_size", 32),
        "freq": config.get("freq", "h"),

        # model params
        "num_class": config.get("output_size", 1),
        "num_kernels": 6,
        "top_k": 5,
        "moving_avg": 25,
        "factor": 1, 
        "d_model": 64,
        "n_heads": 4,
        "e_layers": 2,
        "d_layers": 1,
        "d_ff": 128,
        "dropout": 0.1,
        "use_gpu": True,
        "gpu": 0,
        "gpu_type": "cuda",
        "use_multi_gpu": False,
        "devices": "0",
        "distil": True,
        "embed": "timeF",
        "des": "tslib_model",
        "activation": "gelu",

        # training
        "train_epochs": 10,
        "patience": 3,
        "learning_rate": 0.001,
        "itr": 1,
    }

    # Merge config overrides
    combined = {**defaults, **user_cfg}
    return SimpleNamespace(**combined)




class TsaiModelWrapper(torch.nn.Module):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.exp = self._select_exp_class(args)(args)  # instantiate the proper Exp class
        self.model = self.exp.model  # delegate the model

    def _select_exp_class(self, args):
        task_map = {
            'long_term_forecast': Exp_Long_Term_Forecast,
            'short_term_forecast': Exp_Short_Term_Forecast,
            'imputation': Exp_Imputation,
            'anomaly_detection': Exp_Anomaly_Detection,
            'classification': Exp_Classification,
        }
        return task_map.get(args.task_name, Exp_Long_Term_Forecast)

    def forward(self, *inputs, **kwargs):
        task = self.args.task_name

        if task in ['long_term_forecast', 'short_term_forecast']:
            # Expecting: (x_enc, x_mark_enc, x_dec, x_mark_dec)
            if len(inputs) != 4:
                raise ValueError(f"{task} expects 4 inputs: x_enc, x_mark_enc, x_dec, x_mark_dec")
            x_enc, x_mark_enc, x_dec, x_mark_dec = inputs
            return self.model(x_enc, x_mark_enc, x_dec, x_mark_dec)

        elif task == 'imputation':
            # Expecting: (x_enc, x_mark_enc, x_dec, x_mark_dec, mask)
            if len(inputs) != 5:
                raise ValueError(f"{task} expects 5 inputs: x_enc, x_mark_enc, x_dec, x_mark_dec, mask")
            x_enc, x_mark_enc, x_dec, x_mark_dec, mask = inputs
            return self.model(x_enc, x_mark_enc, x_dec, x_mark_dec, mask)

        elif task == 'anomaly_detection':
            # Expecting: (x_enc,)
            if len(inputs) != 1:
                raise ValueError(f"{task} expects 1 input: x_enc")
            x_enc = inputs[0]
            return self.model(x_enc)

        elif task == 'classification':
            # Expecting: (x_enc, x_mark_enc)
            if len(inputs) != 2:
                raise ValueError(f"{task} expects 2 inputs: x_enc, x_mark_enc")
            x_enc, x_mark_enc = inputs
            return self.model(x_enc, x_mark_enc)

        else:
            raise NotImplementedError(f"Task '{task}' not supported in TsaiModelWrapper")


    def save(self, path):
        torch.save(self.model.state_dict(), path)

    def load(self, path):
        self.model.load_state_dict(torch.load(path))


# -------------------------- Trainer ------------------------
class TimeseriesTrainer(BaseTrainer):
    def prepare_batch(self, *batch):
        task = getattr(self.model, "args", None)
        task_name = getattr(task, "task_name", None)

        if task_name == "classification":
            x, y, x_mark = batch
            return (x.to(self.device), x_mark.to(self.device)), y.to(self.device)
        
        elif task_name in ["long_term_forecast", "short_term_forecast"]:
            # If needed, synthesize decoder inputs from x
            x, y, x_mark = batch

            # Make decoder input same shape as label
            x_dec = torch.zeros_like(y)
            x_mark_dec = torch.zeros_like(x_mark[:, :y.shape[1], :])  # adjust to match pred_len

            return (x.to(self.device),
                    x_mark.to(self.device),
                    x_dec.to(self.device),
                    x_mark_dec.to(self.device)), y.to(self.device)

        else:
            x, y = batch[:2]
            return x.to(self.device), y.to(self.device)

        
    def training_step(self, batch):
        inputs, y = self.prepare_batch(*batch)
        y_hat = self.model(*inputs) if isinstance(inputs, tuple) else self.model(inputs)
        return self.loss_fn(y_hat, y)

    def validation_step(self, batch):
        inputs, y = self.prepare_batch(*batch)
        y_hat = self.model(*inputs) if isinstance(inputs, tuple) else self.model(inputs)
        return self.loss_fn(y_hat, y)


# -------------------------- Factory ------------------------
@register_task("timeseries")
class TimeSeriesFactory(AbstractTaskFactory):
    def create_dataset(self, config):
        dataset_cfg = config.get("dataset_config", {})
        
        return TimeseriesDataset(
            seq_len=dataset_cfg.get("seq_len", 12),
            pred_len=dataset_cfg.get("pred_len", 1),
            batch_size=config.get("batch_size", 32),
            split_ratio=config.get("split_ratio", 0.8),
            config=dataset_cfg,
        )
    
    def create_model(self, config):
        model_cfg = config.get("model_config", {})

        if model_cfg.get("type") == "tslib":
            tsai_args = build_tsai_args(
                name=model_cfg["name"],
                user_cfg=model_cfg.get("params", {}),
                config=config
            )
            tsai_args.task_name = model_cfg["task_name"]
            return TsaiModelWrapper(tsai_args)

        return TimeseriesModel(
            input_size=1,
            hidden_size=config.get("hidden_size", 64),
            output_size=1,
        )

    
    def create_trainer(self, model , dataset, config):
        train_loader , val_loader = dataset.get_dataloaders()
        optimizer = torch.optim.Adam(model.parameters(), lr=config.get('lr'))
        loss_fn = torch.nn.MSELoss()
        return TimeseriesTrainer(
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