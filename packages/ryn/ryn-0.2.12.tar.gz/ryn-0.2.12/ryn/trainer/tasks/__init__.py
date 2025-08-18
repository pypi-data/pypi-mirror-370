# """
# Task-specific implementations of datasets and models.
# """

# from .text_prediction import TextPredictionDataset, TextPredictionModel, TextPredictionTrainer
# from .tabular_classification import TabularDataset, TabularModel, TabularTrainer
# from .image_classification import ImageClassificationDataset, ImageClassificationModel, ImageClassificationTrainer
# from .timeseries import TimeseriesDataset, TimeseriesModel, TimeseriesTrainer

# __all__ = [
#     "TextPredictionDataset", "TextPredictionModel", "TextPredictionTrainer",
#     "TabularDataset", "TabularModel", "TabularTrainer",
#     "ImageClassificationDataset", "ImageClassificationModel", "ImageClassificationTrainer",
#     "TimeseriesDataset", "TimeseriesModel", "TimeseriesTrainer"
# ]

import importlib
import pkgutil

from .task_factory import AbstractTaskFactory
from .task_registry import register_task
__all__ = ["AbstractTaskFactory", "register_task"]

for _, module_name, _ in pkgutil.iter_modules(__path__):
    importlib.import_module(f"{__name__}.{module_name}")
