# third party
import torch
import pandas as pd
from sklearn.preprocessing import StandardScaler
from torch.utils.data import TensorDataset
from sklearn.preprocessing import LabelEncoder

# Local application
from ..base import BaseDataset, AbstractModelArchitecture
from ..trainer import BaseTrainer
from ..tasks.task_factory import AbstractTaskFactory
from ..tasks.task_registry import register_task



class TabularDataset(BaseDataset):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.input_dim = None
    
    def load_dataset(self):
        url = self.config["source"]
        print(url)  # for logging

        df = pd.read_csv(url)
        X = df.iloc[:, :-1].values
        y = df.iloc[:, -1].values

        # Convert labels to ints if they are not numeric
        # if y.dtype == object or isinstance(y[0], str):
        #     y = LabelEncoder().fit_transform(y)
        y = LabelEncoder().fit_transform(y)

        self.num_classes = len(set(y))

        X = StandardScaler().fit_transform(X)
        self.input_dim = X.shape[1]

        X_tensor = torch.tensor(X, dtype=torch.float32)
        y_tensor = torch.tensor(y, dtype=torch.long)

        return TensorDataset(X_tensor, y_tensor)


class TabularModel(AbstractModelArchitecture, torch.nn.Module):
    def __init__(self, input_dim, hidden_dim=64, output_dim=2):
        torch.nn.Module.__init__(self)
        self.model = torch.nn.Sequential(
            torch.nn.Linear(input_dim, hidden_dim),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_dim, output_dim),
        )

    def forward(self, x):
        return self.model(x)

    def save(self, path):
        torch.save(self.state_dict(), path)

    def load(self, path):
        self.load_state_dict(torch.load(path))


class TabularTrainer(BaseTrainer):
    def training_step(self, batch):
        inputs, labels = self.prepare_batch(*batch)
        outputs = self.model(inputs)
        return self.loss_fn(outputs, labels)

    def validation_step(self, batch):
        inputs, labels = self.prepare_batch(*batch)
        outputs = self.model(inputs)
        return self.loss_fn(outputs, labels)

@register_task("tabular_classification")
class TabularFactory(AbstractTaskFactory):
    # def __init__(self):
    #     super().__init__()
    #     # self.dataset = None
    
    def create_dataset(self, config):
        dataset_cfg = config.get("dataset_config", {})
        
        dataset = TabularDataset(
            batch_size=config.get("batch_size", 32),
            split_ratio=config.get("split_ratio", 0.8),
            config=dataset_cfg,
        )
        _ = dataset.get_dataloaders()  # force load, triggers load_dataset and sets input_dim

        input_dim = config.get("input_dim")
        if input_dim is None:
            config["input_dim"] = dataset.input_dim 
        
        config["num_classes"] = dataset.num_classes
        return dataset
    
    def create_model(self, config):
        input_dim = config.get("input_dim")
        num_classes = config.get("num_classes", 2)

        return TabularModel(input_dim=input_dim, output_dim=num_classes)

    def create_trainer(self, model, dataset, config):
        train_loader, val_loader = dataset.get_dataloaders()
        optimizer = torch.optim.Adam(model.parameters(), lr=config.get("lr", 1e-3))
        loss_fn = torch.nn.CrossEntropyLoss()

        return TabularTrainer(
            model=model,
            train_loader=train_loader,
            val_loader=val_loader,
            optimizer=optimizer,
            loss_fn=loss_fn,
            epochs=config.get("epochs", 10),
            device=config.get("device"),
            log_dir=config.get("log_dir"),
            checkpoint_path=config.get("checkpoint_path"),
            )
    