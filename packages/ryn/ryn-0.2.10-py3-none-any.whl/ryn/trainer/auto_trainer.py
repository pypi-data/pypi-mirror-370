from dataclasses import replace
from copy import deepcopy

from .config import DEFAULT_CONFIG, TrainingConfig, DatasetConfig # Ensure DatasetConfig is imported
from .tasks.task_registry import task_factory_registry



class AutoTrainer:
    """
    AutoTrainer - Automated Machine Learning Training Pipeline

    This module provides an automated training pipeline that simplifies the process of
    setting up and running machine learning experiments. It uses a factory pattern to
    automatically create datasets, models, and trainers based on task configuration.

    Features:
        - Task-based automatic component creation (dataset, model, trainer)
        - Configuration management with default settings and custom overrides
        - Factory pattern integration for extensible task support
        - Flexible model injection for custom models
        - Deep configuration merging and validation

    Key methods:
        - **__init__**: Initializes the AutoTrainer with configuration, creates dataset, 
        model, and trainer instances using registered task factories.
        - run: Executes the complete training pipeline using the configured trainer.

    Usage:
        # Basic usage with task configuration
        config = {"task": "classification", "epochs": 50, "batch_size": 32}
        auto_trainer = AutoTrainer(config=config)
        auto_trainer.run()
        
        # With custom model
        my_model = MyCustomModel()
        auto_trainer = AutoTrainer(config=config, model=my_model)
        auto_trainer.run()
        
        # With kwargs override
        auto_trainer = AutoTrainer(config=config, learning_rate=0.01, epochs=100)
        auto_trainer.run()

    Architecture:
        AutoTrainer acts as a high-level orchestrator that:
        1. Merges configuration from defaults, config dict, and kwargs
        2. Validates the requested task against registered factories
        3. Uses task-specific factories to create components
        4. Coordinates the training process through the trainer instance


    Dependencies:
        - ml_trainer.tasks.task_registry: Task factory registry for component creation

    """

    def __init__(self, config: None, model=None, **kwargs): 
        self.config = deepcopy(DEFAULT_CONFIG)
        self.config.update(kwargs)

        if config:
            self.config.update(config)
        self.config.update(kwargs)

        self.task = self.config["task"]
        
        if self.task not in task_factory_registry:
            raise ValueError(
                f"Task: {self.task} is not registered\n"
                f"Available tasks: {list(task_factory_registry.keys())}"
            )
        
        factory = task_factory_registry[self.task]
        
        self.dataset = factory.create_dataset(self.config)
        self.model = model or factory.create_model(self.config)
        self.trainer = factory.create_trainer(self.model, self.dataset, self.config)

    def run(self):
        self.trainer.run()
