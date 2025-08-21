"""
Tesseract OCR parser implementation.

This module provides an OCR parser using Tesseract OCR engine.
Tesseract is a powerful open-source OCR engine that can extract
text from images, scanned documents, and other visual content.
"""

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    pytesseract = None
    Image = None

from typing import Dict, Any, Union, List, Optional
from pathlib import Path
import logging
import numpy as np

from .base_parser import BaseParser


class TesseractParser(BaseParser):
    """
    Tesseract parser using Tesseract engine.
    
    This parser can extract text from images, scanned documents, and other
    visual content using the Tesseract OCR engine. It supports various
    image formats and provides configurable OCR settings.
    
    Attributes:
        name (str): Parser name ('Tesseract OCR')
        version (str): Tesseract version
        supported_formats (list): Supported image formats
    """
    
    def __init__(self, tesseract_path: Optional[str] = None, language: str = 'eng'):
        """
        Initialize the OCR parser with Tesseract.
        
        Args:
            tesseract_path (Optional[str]): Path to tesseract executable
            language (str): OCR language code (default: 'eng' for English)
        """
        if not TESSERACT_AVAILABLE:
            raise ImportError(
                "Tesseract dependencies are not installed. Please install with: "
                "pip install pytesseract Pillow"
            )
        
        # Set up Tesseract path if provided
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        # Get Tesseract version for tracking
        try:
            tesseract_version = pytesseract.get_tesseract_version()
        except Exception:
            tesseract_version = "Unknown"
        
        # Initialize the base parser with OCR-specific settings
        super().__init__(
            name="Tesseract OCR",
            version=str(tesseract_version),
            supported_formats=['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']
        )
        
        # Store OCR configuration
        self.language = language
        self.logger = logging.getLogger(__name__)
        
        # Test Tesseract availability
        self._test_tesseract_availability()
    
    def _test_tesseract_availability(self):
        """
        Test if Tesseract is properly installed and accessible.
        
        This method checks if Tesseract can be executed and provides
        helpful error messages if it's not available.
        """
        try:
            # Try to get Tesseract version
            version = pytesseract.get_tesseract_version()
            self.logger.info(f"Tesseract version: {version}")
        except Exception as e:
            error_msg = (
                "Tesseract is not properly installed or not in PATH. "
                "Please install Tesseract:\n"
                "- macOS: brew install tesseract\n"
                "- Ubuntu: sudo apt-get install tesseract-ocr\n"
                "- Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
            )
            self.logger.error(error_msg)
            raise ImportError(error_msg) from e
    
    def _extract_text_impl(self, file_path: Union[str, Path], **kwargs) -> tuple[str, Dict[str, Any]]:
        """
        Extract text from an image file using Tesseract OCR.
        
        This is the core implementation that does the actual OCR processing.
        It loads the image, applies preprocessing if needed, and runs OCR.
        
        Args:
            file_path (Union[str, Path]): Path to the image file
            **kwargs: Additional OCR options:
                - language (str): OCR language code
                - config (str): Tesseract configuration string
                - preprocess (bool): Whether to apply image preprocessing
                - confidence_threshold (int): Minimum confidence score (0-100)
                
        Returns:
            tuple[str, Dict[str, Any]]: Tuple of (extracted_text, metadata)
        """
        if not TESSERACT_AVAILABLE:
            raise ImportError("Tesseract dependencies are not available")
        
        file_path = Path(file_path)
        
        # Parse additional arguments
        language = kwargs.get('language', self.language)
        config = kwargs.get('config', '')
        preprocess = kwargs.get('preprocess', True)
        confidence_threshold = kwargs.get('confidence_threshold', 0)
        
        extracted_text = ""
        metadata = {
            'file_path': str(file_path),
            'file_size': file_path.stat().st_size,
            'ocr_language': language,
            'preprocessing_applied': preprocess,
            'confidence_threshold': confidence_threshold,
            'extraction_method': 'Tesseract OCR',
            'image_info': {},
            'ocr_confidence': 0.0
        }
        
        try:
            # Load the image
            self.logger.info(f"Loading image: {file_path}")
            image = Image.open(file_path)
            
            # Store image information
            metadata['image_info'] = {
                'format': image.format,
                'mode': image.mode,
                'size': image.size,
                'width': image.width,
                'height': image.height
            }
            
            # Apply preprocessing if requested
            if preprocess:
                image = self._preprocess_image(image)
                metadata['preprocessing_applied'] = True
            
            # Perform OCR with confidence scores
            self.logger.info(f"Running OCR with language: {language}")
            ocr_data = pytesseract.image_to_data(
                image, 
                lang=language, 
                config=config,
                output_type=pytesseract.Output.DICT
            )
            
            # Extract text and confidence scores
            extracted_text, confidence_score = self._process_ocr_results(
                ocr_data, confidence_threshold
            )
            
            # Store confidence information
            metadata['ocr_confidence'] = confidence_score
            metadata['text_blocks'] = len(ocr_data.get('text', []))
            
            self.logger.info(f"OCR completed. Confidence: {confidence_score:.2f}%")
            
        except Exception as e:
            self.logger.error(f"Error during OCR processing: {e}")
            raise e
        
        finally:
            # Clean up image object
            if 'image' in locals():
                image.close()
        
        return extracted_text, metadata
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Apply image preprocessing to improve OCR accuracy.
        
        This method applies various image enhancement techniques:
        - Grayscale conversion
        - Noise reduction
        - Contrast enhancement
        - Binarization (if needed)
        
        Args:
            image (Image.Image): Input image to preprocess
            
        Returns:
            Image.Image: Preprocessed image
        """
        try:
            # Convert to grayscale if not already
            if image.mode != 'L':
                image = image.convert('L')
            
            # Convert to numpy array for processing
            img_array = np.array(image)
            
            # Apply basic preprocessing
            # 1. Normalize contrast
            img_array = self._normalize_contrast(img_array)
            
            # 2. Apply noise reduction (simple median filter)
            img_array = self._reduce_noise(img_array)
            
            # 3. Apply thresholding for better text recognition
            img_array = self._apply_threshold(img_array)
            
            # Convert back to PIL Image
            processed_image = Image.fromarray(img_array)
            
            self.logger.debug("Image preprocessing completed")
            return processed_image
            
        except Exception as e:
            self.logger.warning(f"Preprocessing failed, using original image: {e}")
            return image
    
    def _normalize_contrast(self, img_array: np.ndarray) -> np.ndarray:
        """
        Normalize image contrast for better OCR results.
        
        Args:
            img_array (np.ndarray): Input image array
            
        Returns:
            np.ndarray: Contrast-normalized image array
        """
        # Calculate image statistics
        min_val = np.min(img_array)
        max_val = np.max(img_array)
        
        # Avoid division by zero
        if max_val > min_val:
            # Normalize to 0-255 range
            normalized = ((img_array - min_val) / (max_val - min_val)) * 255
            return normalized.astype(np.uint8)
        else:
            return img_array
    
    def _reduce_noise(self, img_array: np.ndarray) -> np.ndarray:
        """
        Apply simple noise reduction to the image.
        
        Args:
            img_array (np.ndarray): Input image array
            
        Returns:
            np.ndarray: Noise-reduced image array
        """
        # Simple median filter for noise reduction
        # This helps remove salt-and-pepper noise
        try:
            from scipy import ndimage
            return ndimage.median_filter(img_array, size=2)
        except ImportError:
            # If scipy is not available, return original
            self.logger.debug("scipy not available, skipping noise reduction")
            return img_array
    
    def _apply_threshold(self, img_array: np.ndarray) -> np.ndarray:
        """
        Apply adaptive thresholding for better text recognition.
        
        Args:
            img_array (np.ndarray): Input image array
            
        Returns:
            np.ndarray: Thresholded image array
        """
        # Simple Otsu thresholding
        # This converts grayscale to binary (black and white)
        threshold = np.mean(img_array)
        binary = (img_array > threshold).astype(np.uint8) * 255
        return binary
    
    def _process_ocr_results(self, ocr_data: Dict[str, Any], confidence_threshold: int) -> tuple[str, float]:
        """
        Process OCR results and extract text with confidence filtering.
        
        Args:
            ocr_data (Dict[str, Any]): Raw OCR data from Tesseract
            confidence_threshold (int): Minimum confidence score (0-100)
            
        Returns:
            tuple[str, float]: Tuple of (extracted_text, average_confidence)
        """
        text_blocks = []
        confidences = []
        
        # Extract text and confidence for each detected text block
        for i, text in enumerate(ocr_data.get('text', [])):
            confidence = ocr_data.get('conf', [0])[i] if i < len(ocr_data.get('conf', [])) else 0
            
            # Only include text blocks above confidence threshold
            if confidence >= confidence_threshold and text.strip():
                text_blocks.append(text)
                confidences.append(confidence)
        
        # Join text blocks with proper spacing
        extracted_text = ' '.join(text_blocks)
        
        # Calculate average confidence
        average_confidence = np.mean(confidences) if confidences else 0.0
        
        return extracted_text, average_confidence
    
    def extract_text_with_confidence(self, file_path: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """
        Extract text with detailed confidence information for each word.
        
        This method provides more detailed information about OCR confidence
        for each detected text element, useful for post-processing.
        
        Args:
            file_path (Union[str, Path]): Path to the image file
            **kwargs: Additional OCR options
            
        Returns:
            Dict[str, Any]: Detailed OCR results with confidence scores
        """
        if not TESSERACT_AVAILABLE:
            raise ImportError("Tesseract dependencies are not available")
        
        file_path = Path(file_path)
        
        try:
            # Load and preprocess image
            image = Image.open(file_path)
            if kwargs.get('preprocess', True):
                image = self._preprocess_image(image)
            
            # Get detailed OCR data
            ocr_data = pytesseract.image_to_data(
                image,
                lang=kwargs.get('language', self.language),
                config=kwargs.get('config', ''),
                output_type=pytesseract.Output.DICT
            )
            
            # Process results
            text_blocks = []
            for i, text in enumerate(ocr_data.get('text', [])):
                if text.strip():
                    block_info = {
                        'text': text,
                        'confidence': ocr_data.get('conf', [0])[i] if i < len(ocr_data.get('conf', [])) else 0,
                        'bbox': {
                            'left': ocr_data.get('left', [0])[i] if i < len(ocr_data.get('left', [])) else 0,
                            'top': ocr_data.get('top', [0])[i] if i < len(ocr_data.get('top', [])) else 0,
                            'width': ocr_data.get('width', [0])[i] if i < len(ocr_data.get('width', [])) else 0,
                            'height': ocr_data.get('height', [0])[i] if i < len(ocr_data.get('height', [])) else 0
                        }
                    }
                    text_blocks.append(block_info)
            
            return {
                'text_blocks': text_blocks,
                'total_blocks': len(text_blocks),
                'average_confidence': np.mean([b['confidence'] for b in text_blocks]) if text_blocks else 0.0
            }
            
        except Exception as e:
            self.logger.error(f"Error in detailed OCR extraction: {e}")
            raise e
        
        finally:
            if 'image' in locals():
                image.close()
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported OCR languages.
        
        Returns:
            List[str]: List of available language codes
        """
        try:
            # Get available languages from Tesseract
            languages = pytesseract.get_languages()
            return languages
        except Exception as e:
            self.logger.warning(f"Could not get supported languages: {e}")
            return ['eng']  # Default to English 