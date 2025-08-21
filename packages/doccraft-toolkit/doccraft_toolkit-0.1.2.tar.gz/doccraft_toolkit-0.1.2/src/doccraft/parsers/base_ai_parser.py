"""
Base AI parser class for AI-powered document parsing.

This module defines the base interface for AI-powered document parsers
that use deep learning models for document understanding.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
import time
import logging
import torch
from PIL import Image
import numpy as np
import io

from .base_parser import BaseParser


class BaseAIParser(BaseParser, ABC):
    """
    Abstract base class for AI-powered document parsers.
    
    This class extends BaseParser to provide common functionality for
    AI models like LayoutLMv3, Qwen-VL-Plus, and other deep learning
    models used for document understanding.
    
    Attributes:
        model: The loaded AI model
        tokenizer: The model's tokenizer (if applicable)
        device: The device to run inference on (CPU/GPU)
        model_name: Name of the AI model
        batch_size: Batch size for processing multiple documents
    """
    
    def __init__(self, 
                 model_name: str,
                 device: str = "auto",
                 batch_size: int = 1,
                 cache_dir: Optional[str] = None,
                 **kwargs):
        """
        Initialize the AI parser.
        
        Args:
            model_name: Name or path of the AI model to load
            device: Device to run inference on ("auto", "cpu", "cuda", "mps")
            batch_size: Batch size for processing multiple documents
            cache_dir: Directory to cache model files
            **kwargs: Additional model-specific arguments
        """
        # Determine device
        self.device = self._determine_device(device)
        
        # Store configuration
        self.model_name = model_name
        self.batch_size = batch_size
        self.cache_dir = cache_dir
        
        # Initialize model components
        self.model = None
        self.tokenizer = None
        self.processor = None
        
        # Setup logging
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize the model
        self._initialize_model(**kwargs)
        
        # Call parent constructor with AI-specific settings
        super().__init__(
            name=f"AI-{self.__class__.__name__}",
            version=self._get_model_version(),
            supported_formats=['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.pdf']
        )
    
    def _determine_device(self, device: str) -> str:
        """
        Determine the best device to use for inference.
        
        Args:
            device: Device specification
            
        Returns:
            str: Device to use ("cpu", "cuda", or "mps")
        """
        if device == "auto":
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return "mps"
            else:
                return "cpu"
        return device
    
    @abstractmethod
    def _initialize_model(self, **kwargs):
        """
        Initialize the AI model, tokenizer, and processor.
        
        This method must be implemented by subclasses to load
        the specific AI model and its components.
        
        Args:
            **kwargs: Model-specific initialization arguments
        """
        pass
    
    @abstractmethod
    def _get_model_version(self) -> str:
        """
        Get the version of the loaded model.
        
        Returns:
            str: Model version
        """
        pass
    
    def _extract_text_impl(self, file_path: Union[str, Path], **kwargs) -> tuple[str, Dict[str, Any]]:
        """
        Extract text from a document using AI model.
        
        This is the main implementation that uses the AI model to
        extract text from documents with understanding of layout
        and visual context.
        
        Args:
            file_path: Path to the document to parse
            **kwargs: Additional arguments for AI processing
            
        Returns:
            tuple[str, Dict[str, Any]]: Tuple of (extracted_text, metadata)
        """
        start_time = time.time()
        
        # Load and preprocess the document
        document = self._load_document(file_path)
        
        # Process with AI model
        ai_result = self._process_with_ai(document, **kwargs)
        
        # Post-process the AI output
        extracted_text = self._post_process_ai_output(ai_result)
        
        # Prepare metadata
        metadata = self._prepare_metadata(file_path, ai_result, time.time() - start_time)
        
        return extracted_text, metadata
    
    def _load_document(self, file_path: Union[str, Path]) -> Any:
        """
        Load and preprocess the document for AI processing.
        
        Args:
            file_path: Path to the document
            
        Returns:
            Any: Preprocessed document ready for AI model
        """
        file_path = Path(file_path)
        
        if str(file_path).lower().endswith('.pdf'):
            # Convert PDF to image for AI processing
            return self._pdf_to_image(file_path)
        else:
            # Load image directly
            return Image.open(file_path).convert('RGB')
    
    def _pdf_to_image(self, pdf_path: Path) -> Image.Image:
        """
        Convert PDF to image for AI processing.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            PIL.Image: First page of PDF as image
        """
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(pdf_path)
            page = doc[0]  # Get first page
            pix = page.get_pixmap()
            img_data = pix.tobytes("png")
            doc.close()
            
            return Image.open(io.BytesIO(img_data))
        except ImportError:
            raise ImportError("PyMuPDF is required for PDF processing. Install with: pip install PyMuPDF")
    
    @abstractmethod
    def _process_with_ai(self, document: Any, **kwargs) -> Dict[str, Any]:
        """
        Process the document with the AI model.
        
        Args:
            document: Preprocessed document
            **kwargs: Additional processing arguments
            
        Returns:
            Dict[str, Any]: AI model output
        """
        pass
    
    def _post_process_ai_output(self, ai_result: Dict[str, Any]) -> str:
        """
        Post-process the AI model output to extract text.
        
        Args:
            ai_result: Raw AI model output
            
        Returns:
            str: Extracted and cleaned text
        """
        # Default implementation - can be overridden by subclasses
        if 'text' in ai_result:
            return ai_result['text']
        elif 'predictions' in ai_result:
            # Handle structured predictions
            return self._extract_text_from_predictions(ai_result['predictions'])
        else:
            return str(ai_result)
    
    def _extract_text_from_predictions(self, predictions: List[Dict[str, Any]]) -> str:
        """
        Extract text from structured predictions.
        
        Args:
            predictions: List of prediction dictionaries
            
        Returns:
            str: Combined text from predictions
        """
        texts = []
        for pred in predictions:
            if 'text' in pred:
                texts.append(pred['text'])
            elif 'label' in pred:
                texts.append(pred['label'])
        
        return ' '.join(texts)
    
    def _prepare_metadata(self, file_path: Union[str, Path], 
                         ai_result: Dict[str, Any], 
                         processing_time: float) -> Dict[str, Any]:
        """
        Prepare metadata about the AI processing.
        
        Args:
            file_path: Path to the processed file
            ai_result: AI model output
            processing_time: Time taken for processing
            
        Returns:
            Dict[str, Any]: Metadata dictionary
        """
        return {
            'file_path': str(file_path),
            'model_name': self.model_name,
            'device': self.device,
            'processing_time': processing_time,
            'ai_model_output': ai_result,
            'extraction_method': f'AI-{self.__class__.__name__}',
            'model_version': self._get_model_version(),
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded AI model.
        
        Returns:
            Dict[str, Any]: Model information
        """
        return {
            'model_name': self.model_name,
            'model_version': self._get_model_version(),
            'device': self.device,
            'batch_size': self.batch_size,
            'cache_dir': self.cache_dir,
        }
    
    def set_device(self, device: str):
        """
        Change the device used for inference.
        
        Args:
            device: New device to use ("cpu", "cuda", "mps")
        """
        old_device = self.device
        self.device = self._determine_device(device)
        
        if self.device != old_device and self.model is not None:
            self.logger.info(f"Moving model from {old_device} to {self.device}")
            self.model = self.model.to(self.device)
    
    def enable_batch_processing(self, batch_size: int):
        """
        Enable batch processing for multiple documents.
        
        Args:
            batch_size: Number of documents to process in each batch
        """
        self.batch_size = batch_size
        self.logger.info(f"Batch processing enabled with batch size: {batch_size}")
    
    def clear_cache(self):
        """
        Clear any cached model data or intermediate results.
        """
        if hasattr(self, 'model') and self.model is not None:
            if hasattr(self.model, 'cpu'):
                self.model.cpu()
            torch.cuda.empty_cache() if torch.cuda.is_available() else None
            self.logger.info("Model cache cleared") 