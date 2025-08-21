"""
Base postprocessor class for document/text postprocessing.

Defines the interface for all postprocessing modules (e.g., spell correction, normalization).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

class BasePostprocessor(ABC):
    """
    Abstract base class for all postprocessors.
    
    All postprocessors must implement the process() method.
    """
    def __init__(self, name: str, version: str, supported_formats: list):
        self.name = name
        self.version = version
        self.supported_formats = supported_formats
    
    @abstractmethod
    def process(self, data: Any, **kwargs) -> Any:
        """
        Process the input data and return the result.
        Args:
            data (Any): Input data (e.g., text)
            **kwargs: Additional options
        Returns:
            Any: Processed data
        """
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """
        Return information about this postprocessor.
        """
        return {
            "name": self.name,
            "version": self.version,
            "supported_formats": self.supported_formats,
            "type": self.__class__.__name__
        } 