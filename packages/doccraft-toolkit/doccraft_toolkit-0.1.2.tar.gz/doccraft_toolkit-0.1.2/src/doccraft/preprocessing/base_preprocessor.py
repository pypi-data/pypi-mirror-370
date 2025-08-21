"""
Base preprocessor class for document/image preprocessing.

Defines the interface for all preprocessing modules (e.g., binarization, resizing, denoising).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

class BasePreprocessor(ABC):
    """
    Abstract base class for all preprocessors.
    
    All preprocessors must implement the process() method.
    """
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def process(self, data: Any, **kwargs) -> Any:
        """
        Process the input data and return the result.
        Args:
            data (Any): Input data (e.g., image, text)
            **kwargs: Additional options
        Returns:
            Any: Processed data
        """
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """
        Return information about this preprocessor.
        """
        return {"name": self.name, "type": self.__class__.__name__} 