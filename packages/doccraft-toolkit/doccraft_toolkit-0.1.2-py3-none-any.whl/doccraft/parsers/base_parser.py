"""
Base parser class for document parsing.

This module defines the base interface that all document parsers must implement.
It ensures consistency across different parsing methods (Tesseract, PaddleOCR, PDF, AI models).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
from pathlib import Path
import time


class BaseParser(ABC):
    """
    Abstract base class for all document parsers.
    
    This class defines the common interface that all parsers must implement.
    It provides basic functionality like timing and error handling.
    
    Attributes:
        name (str): Name of the parser (e.g., 'PyMuPDF', 'Tesseract')
        version (str): Version of the parser
        supported_formats (list): List of supported file formats
    """
    
    def __init__(self, name: str, version: str, supported_formats: list):
        """
        Initialize the base parser.
        
        Args:
            name (str): Name of the parser
            version (str): Version of the parser
            supported_formats (list): List of supported file formats (e.g., ['.pdf', '.jpg'])
        """
        self.name = name
        self.version = version
        self.supported_formats = supported_formats
        self._extraction_time = 0.0  # Track how long extraction takes
    
    def can_parse(self, file_path: Union[str, Path]) -> bool:
        """
        Check if this parser can handle the given file.
        
        Args:
            file_path (Union[str, Path]): Path to the file to check
            
        Returns:
            bool: True if the parser can handle this file type
        """
        file_path = Path(file_path)
        return file_path.suffix.lower() in self.supported_formats
    
    def extract_text(self, file_path: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """
        Extract text from a document with timing and error handling.
        
        This is the main method that users will call. It wraps the actual
        parsing logic with timing, error handling, and result formatting.
        
        Args:
            file_path (Union[str, Path]): Path to the document to parse
            **kwargs: Additional arguments passed to the specific parser
            
        Returns:
            Dict[str, Any]: Dictionary containing:
                - 'text': Extracted text
                - 'metadata': Document metadata
                - 'extraction_time': Time taken for extraction
                - 'parser_info': Information about the parser used
                - 'error': Error message if extraction failed
        """
        start_time = time.time()
        result = {
            'text': '',
            'metadata': {},
            'extraction_time': 0.0,
            'parser_info': {
                'name': self.name,
                'version': self.version
            },
            'error': None
        }
        
        try:
            # Check if we can parse this file type
            if not self.can_parse(file_path):
                raise ValueError(f"File format not supported. Supported formats: {self.supported_formats}")
            
            # Perform the actual text extraction (implemented by subclasses)
            text, metadata = self._extract_text_impl(file_path, **kwargs)
            
            # Store the results
            result['text'] = text
            result['metadata'] = metadata
            
        except Exception as e:
            # Store any errors that occurred
            result['error'] = str(e)
            
        finally:
            # Always record the time taken
            result['extraction_time'] = time.time() - start_time
            self._extraction_time = result['extraction_time']
        
        return result
    
    @abstractmethod
    def _extract_text_impl(self, file_path: Union[str, Path], **kwargs) -> tuple[str, Dict[str, Any]]:
        """
        Abstract method that subclasses must implement.
        
        This is where the actual parsing logic goes. Each parser type
        (PDF, Tesseract, PaddleOCR, AI model) will implement this differently.
        
        Args:
            file_path (Union[str, Path]): Path to the document to parse
            **kwargs: Additional arguments specific to the parser
            
        Returns:
            tuple[str, Dict[str, Any]]: Tuple of (extracted_text, metadata)
        """
        pass
    
    def get_last_extraction_time(self) -> float:
        """
        Get the time taken for the last text extraction.
        
        Returns:
            float: Time in seconds for the last extraction
        """
        return self._extraction_time
    
    def get_parser_info(self) -> Dict[str, Any]:
        """
        Get information about this parser.
        
        Returns:
            Dict[str, Any]: Dictionary with parser information
        """
        return {
            'name': self.name,
            'version': self.version,
            'supported_formats': self.supported_formats
        } 