"""
Base benchmarker module.

This module provides the base class for all benchmarking tools
in the DocCraft package.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Union, List
from pathlib import Path
import logging


class BaseBenchmarker(ABC):
    """
    Base class for all benchmarkers in DocCraft.
    
    This abstract base class defines the common interface and functionality
    that all benchmarkers must implement.
    
    Attributes:
        name (str): Benchmarker name
        version (str): Version information
        supported_metrics (list): List of supported metrics
    """
    
    def __init__(self, name: str, version: str, supported_metrics: List[str]):
        """
        Initialize the base benchmarker.
        
        Args:
            name (str): Benchmarker name
            version (str): Version information
            supported_metrics (List[str]): List of supported metrics
        """
        self.name = name
        self.version = version
        self.supported_metrics = supported_metrics
        self.logger = logging.getLogger(__name__)
    
    @abstractmethod
    def benchmark(self, parser, file_path: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """
        Benchmark a parser using this benchmarker.
        
        Args:
            parser: Parser instance to benchmark
            file_path (Union[str, Path]): Path to the test file
            **kwargs: Additional benchmark options
            
        Returns:
            Dict[str, Any]: Benchmark results
        """
        pass
    
    def get_supported_metrics(self) -> List[str]:
        """
        Get list of supported metrics for this benchmarker.
        
        Returns:
            List[str]: List of supported metrics
        """
        return self.supported_metrics
    
    def validate_parser(self, parser) -> bool:
        """
        Validate that a parser is compatible with this benchmarker.
        
        Args:
            parser: Parser instance to validate
            
        Returns:
            bool: True if parser is valid, False otherwise
        """
        # Check if parser has required methods
        required_methods = ['extract_text']
        
        for method in required_methods:
            if not hasattr(parser, method):
                self.logger.warning(f"Parser missing required method: {method}")
                return False
        
        return True
    
    def get_benchmarker_info(self) -> Dict[str, Any]:
        """
        Get information about this benchmarker.
        
        Returns:
            Dict[str, Any]: Benchmarker information
        """
        return {
            'name': self.name,
            'version': self.version,
            'supported_metrics': self.supported_metrics,
            'class': self.__class__.__name__
        } 