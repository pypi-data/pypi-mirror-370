import requests

import torch
from torch.utils.data import Dataset

from ..base import BaseDataset, AbstractModelArchitecture
from ..trainer import BaseTrainer
from ..tasks.task_registry import register_task
from ..tasks.task_factory import AbstractTaskFactory


class TextPredictionDataset(BaseDataset):
    def __init__(self, seq_len=100, **kwargs):
        super().__init__(**kwargs)
        self.seq_len = seq_len
        self.vocab_size = None

    def load_dataset(self):
        url = self.config.get("source")
        text = requests.get(url).text

        chars = sorted(list(set(text)))
        self.vocab_size = len(chars)

        class CharDataset(Dataset):
            def __init__(self, text, seq_len):
                chars = sorted(list(set(text)))
                self.vocab_size = len(chars)
                self.char2idx = {ch: idx for idx, ch in enumerate(chars)}
                self.idx2char = {idx: ch for idx, ch in enumerate(chars)}
                self.data = [self.char2idx[c] for c in text]
                self.seq_len = seq_len

            def __len__(self):
                return len(self.data) - self.seq_len

            def __getitem__(self, idx):
                x = torch.tensor(self.data[idx : idx + self.seq_len])
                y = torch.tensor(self.data[idx + 1 : idx + self.seq_len + 1])
                return x, y

        return CharDataset(text, self.seq_len)


class TextPredictionModel(AbstractModelArchitecture, torch.nn.Module):
    def __init__(self, vocab_size, embedding_dim=64, hidden_dim=128):
        torch.nn.Module.__init__(self)  # Explicit init for nn.Module
        self.embedding = torch.nn.Embedding(vocab_size, embedding_dim)
        self.rnn = torch.nn.GRU(embedding_dim, hidden_dim, batch_first=True)
        self.fc = torch.nn.Linear(hidden_dim, vocab_size)

    def forward(self, x):
        x = self.embedding(x)
        out, _ = self.rnn(x)
        out = self.fc(out)
        return out

    def save(self, path):
        torch.save(self.state_dict(), path)

    def load(self, path):
        self.load_state_dict(torch.load(path))

class TextPredictionTrainer(BaseTrainer):
    def training_step(self, batch):
        inputs, targets = self.prepare_batch(*batch)
        outputs = self.model(inputs)
        return self.loss_fn(outputs.view(-1, outputs.shape[-1]), targets.view(-1))

    def validation_step(self, batch):
        inputs, targets = self.prepare_batch(*batch)
        outputs = self.model(inputs)
        return self.loss_fn(outputs.view(-1, outputs.shape[-1]), targets.view(-1))
@register_task("text_prediction")
class TextPredictionFactory(AbstractTaskFactory):
    def create_dataset(self, config):
        dataset_cfg = config.get("dataset_config", {})

        dataset = TextPredictionDataset(
            seq_len=dataset_cfg.get("seq_len", 100),
            batch_size=config.get("batch_size", 32),
            split_ratio=config.get("split_ratio", 0.8),
            config=dataset_cfg,
        )

        _ = dataset.get_dataloaders()  # 👉 forces load_dataset() to run, populating vocab_size

        # Save vocab_size into config for create_model()
        vocab_size = config.get("vocab_size")
        if vocab_size is None:
            config["vocab_size"] = dataset.vocab_size

        return dataset

    def create_model(self, config):
        vocab_size = config.get("vocab_size")
        assert vocab_size is not None, "vocab_size should be set by create_dataset"

        return TextPredictionModel(
            vocab_size=vocab_size,
            embedding_dim=config.get("embedding_dim", 64),
            hidden_dim=config.get("hidden_dim", 128),
        )

    def create_trainer(self, model, dataset, config):
        train_loader, val_loader = dataset.get_dataloaders()
        optimizer = torch.optim.Adam(model.parameters(), lr=config.get("lr", 1e-3))
        loss_fn = torch.nn.CrossEntropyLoss()

        return TextPredictionTrainer(
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
