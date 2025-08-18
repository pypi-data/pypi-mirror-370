import abc
from abc import abstractmethod

# Abstract factory design pattern
class AbstractTaskFactory(abc.ABC):
    @abstractmethod
    def create_dataset(self, config):
        msg = "create dataset not implemented"
        raise ValueError(msg)
    
    @abstractmethod
    def create_model(self, config):
        msg = "create model not implemented"
        raise ValueError(msg)

    @abstractmethod
    def create_trainer(self, config):
        msg = "create trainer not implemented"
        raise ValueError(msg)
