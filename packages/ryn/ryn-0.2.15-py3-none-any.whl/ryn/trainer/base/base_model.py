# Standard library
import abc

class AbstractModelArchitecture(metaclass=abc.ABCMeta):
    """
    Abstract base class for model architectures.
    Users should subclass this to define their own models.
    """
    @abc.abstractmethod
    def forward(self, x):
        """
        Defines the forward pass.
        Must be implemented by subclasses.
        """
        msg = "Subclasses must implement forward()"
        raise NotImplementedError(msg)
    
    @abc.abstractmethod
    def save():
        """
        Save model-specific parameters or structure.
        """
        msg = "Subclasses must implement save()"
        raise NotImplementedError(msg)

    
    @abc.abstractmethod
    def load():
        """
        Load model-specific parameters or structure.
        """
        msg = "Subclasses must implement load()"
        raise NotImplementedError(msg)
