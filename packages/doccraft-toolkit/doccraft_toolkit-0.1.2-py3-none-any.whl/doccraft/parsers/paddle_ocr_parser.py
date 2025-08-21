"""
PaddleOCR parser implementation.

This module provides an OCR parser using PaddleOCR engine.
PaddleOCR is a modern OCR engine with excellent accuracy for
various languages and document types.
"""

try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False
    PaddleOCR = None

from typing import Dict, Any, Union, List, Optional
from pathlib import Path
import logging
import numpy as np
from PIL import Image

from .base_parser import BaseParser


class PaddleOCRParser(BaseParser):
    """
    OCR parser using PaddleOCR engine.
    
    This parser can extract text from images, scanned documents, and other
    visual content using the PaddleOCR engine. It supports multiple languages
    and provides high accuracy for various document types.
    
    Attributes:
        name (str): Parser name ('PaddleOCR')
        version (str): PaddleOCR version
        supported_formats (list): Supported image formats
    """
    
    def __init__(self, language: str = 'en', use_gpu: bool = False, use_angle_cls: bool = True):
        """
        Initialize the OCR parser with PaddleOCR.
        
        Args:
            language (str): OCR language code (default: 'en' for English)
            use_gpu (bool): Whether to use GPU acceleration
            use_angle_cls (bool): Whether to use angle classification
        """
        if not PADDLEOCR_AVAILABLE:
            raise ImportError(
                "PaddleOCR is not installed. Please install it with: "
                "pip install paddlepaddle paddleocr"
            )
        
        # Initialize PaddleOCR
        try:
            # Try without use_gpu parameter first (newer versions don't support it)
            try:
                self.ocr = PaddleOCR(
                    lang=language,
                    use_angle_cls=use_angle_cls
                )
            except TypeError:
                # If that fails, try with use_gpu parameter (older versions)
                self.ocr = PaddleOCR(
                    lang=language,
                    use_gpu=use_gpu,
                    use_angle_cls=use_angle_cls
                )
        except Exception as e:
            raise ImportError(f"Failed to initialize PaddleOCR: {e}")
        
        # Get PaddleOCR version for tracking
        try:
            import paddleocr
            paddleocr_version = paddleocr.__version__
        except Exception:
            paddleocr_version = "Unknown"
        
        # Initialize the base parser with OCR-specific settings
        super().__init__(
            name="PaddleOCR",
            version=paddleocr_version,
            supported_formats=['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']
        )
        
        # Store OCR configuration
        self.language = language
        self.use_gpu = use_gpu
        self.use_angle_cls = use_angle_cls
        self.logger = logging.getLogger(__name__)
        
        # Test PaddleOCR availability
        self._test_paddleocr_availability()
    
    def _test_paddleocr_availability(self):
        """
        Test if PaddleOCR is properly installed and accessible.
        
        This method checks if PaddleOCR can be initialized and provides
        helpful error messages if it's not available.
        """
        try:
            # Simple test - just check if OCR object exists
            if hasattr(self, 'ocr') and self.ocr is not None:
                self.logger.info("PaddleOCR initialized successfully")
            else:
                raise Exception("PaddleOCR object not properly initialized")
        except Exception as e:
            error_msg = (
                "PaddleOCR is not properly installed or configured. "
                "Please install PaddleOCR:\n"
                "pip install paddlepaddle paddleocr"
            )
            self.logger.error(error_msg)
            raise ImportError(error_msg) from e
    
    def _extract_text_impl(self, file_path: Union[str, Path], **kwargs) -> tuple[str, Dict[str, Any]]:
        """
        Extract text from an image file using PaddleOCR.
        
        This is the core implementation that does the actual OCR processing.
        It loads the image, applies preprocessing if needed, and runs OCR.
        
        Args:
            file_path (Union[str, Path]): Path to the image file
            **kwargs: Additional OCR options:
                - language (str): OCR language code
                - preprocess (bool): Whether to apply image preprocessing
                - confidence_threshold (float): Minimum confidence score (0.0-1.0)
                - det_db_thresh (float): Detection threshold
                - det_db_box_thresh (float): Detection box threshold
                
        Returns:
            tuple[str, Dict[str, Any]]: Tuple of (extracted_text, metadata)
        """
        if not PADDLEOCR_AVAILABLE:
            raise ImportError("PaddleOCR is not available")
        
        file_path = Path(file_path)
        
        # Parse additional arguments
        language = kwargs.get('language', self.language)
        preprocess = kwargs.get('preprocess', True)
        confidence_threshold = kwargs.get('confidence_threshold', 0.0)
        det_db_thresh = kwargs.get('det_db_thresh', 0.3)
        det_db_box_thresh = kwargs.get('det_db_box_thresh', 0.5)
        
        extracted_text = ""
        metadata = {
            'file_path': str(file_path),
            'file_size': file_path.stat().st_size,
            'ocr_language': language,
            'preprocessing_applied': preprocess,
            'confidence_threshold': confidence_threshold,
            'extraction_method': 'PaddleOCR',
            'image_info': {},
            'ocr_confidence': 0.0,
            'text_blocks': 0
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
            
            # Convert to numpy array for PaddleOCR
            image_array = np.array(image)
            
            # Apply preprocessing if requested
            if preprocess:
                image_array = self._preprocess_image(image_array)
                metadata['preprocessing_applied'] = True
            
            # Perform OCR
            self.logger.info(f"Running PaddleOCR with language: {language}")
            ocr_result = self.ocr.ocr(image_array)
            
            # Extract text and confidence scores
            extracted_text, confidence_score, text_blocks = self._process_ocr_results(
                ocr_result, confidence_threshold
            )
            
            # Store confidence information
            metadata['ocr_confidence'] = confidence_score
            metadata['text_blocks'] = text_blocks
            
            self.logger.info(f"PaddleOCR completed. Confidence: {confidence_score:.2f}%")
            
        except Exception as e:
            self.logger.error(f"Error during PaddleOCR processing: {e}")
            raise e
        
        finally:
            # Clean up image object
            if 'image' in locals():
                image.close()
        
        return extracted_text, metadata
    
    def _preprocess_image(self, image_array: np.ndarray) -> np.ndarray:
        """
        Apply image preprocessing to improve OCR accuracy.
        
        This method applies various image enhancement techniques:
        - Grayscale conversion
        - Noise reduction
        - Contrast enhancement
        - Binarization (if needed)
        
        Args:
            image_array (np.ndarray): Input image as numpy array
            
        Returns:
            np.ndarray: Preprocessed image array
        """
        # Convert to grayscale if it's a color image
        if len(image_array.shape) == 3 and image_array.shape[2] == 3:
            # Convert RGB to grayscale using luminance formula
            gray = np.dot(image_array[..., :3], [0.299, 0.587, 0.114])
            image_array = gray.astype(np.uint8)
        
        # Normalize contrast
        image_array = self._normalize_contrast(image_array)
        
        # Reduce noise
        image_array = self._reduce_noise(image_array)
        
        return image_array
    
    def _normalize_contrast(self, img_array: np.ndarray) -> np.ndarray:
        """
        Normalize image contrast using histogram equalization.
        
        Args:
            img_array (np.ndarray): Input image array
            
        Returns:
            np.ndarray: Contrast-normalized image array
        """
        # Simple contrast normalization
        min_val = np.min(img_array)
        max_val = np.max(img_array)
        
        if max_val > min_val:
            normalized = ((img_array - min_val) / (max_val - min_val)) * 255
            return normalized.astype(np.uint8)
        
        return img_array
    
    def _reduce_noise(self, img_array: np.ndarray) -> np.ndarray:
        """
        Reduce noise in the image using simple filtering.
        
        Args:
            img_array (np.ndarray): Input image array
            
        Returns:
            np.ndarray: Denoised image array
        """
        # Simple median filtering for noise reduction
        from scipy import ndimage
        
        try:
            # Apply median filter to reduce noise
            denoised = ndimage.median_filter(img_array, size=3)
            return denoised
        except ImportError:
            # If scipy is not available, return original
            self.logger.warning("scipy not available, skipping noise reduction")
            return img_array
    
    def _process_ocr_results(self, ocr_result: List, confidence_threshold: float) -> tuple[str, float, int]:
        """
        Process PaddleOCR results and extract text with confidence scores.
        
        Args:
            ocr_result (List): Raw PaddleOCR result
            confidence_threshold (float): Minimum confidence threshold
            
        Returns:
            tuple[str, float, int]: (extracted_text, average_confidence, text_blocks_count)
        """
        if not ocr_result or not ocr_result[0]:
            return "", 0.0, 0
        
        extracted_lines = []
        confidence_scores = []
        text_blocks_count = 0
        
        # Process each detected text region
        for line in ocr_result[0]:
            if len(line) >= 2:
                # Extract text and confidence
                text = line[1][0]  # Text content
                confidence = line[1][1]  # Confidence score
                
                # Apply confidence threshold
                if confidence >= confidence_threshold:
                    extracted_lines.append(text)
                    confidence_scores.append(confidence)
                    text_blocks_count += 1
        
        # Calculate average confidence
        avg_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
        
        # Join lines with newlines
        extracted_text = '\n'.join(extracted_lines)
        
        return extracted_text, avg_confidence * 100, text_blocks_count
    
    def extract_text_with_bbox(self, file_path: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """
        Extract text with bounding box information.
        
        Args:
            file_path (Union[str, Path]): Path to the image file
            **kwargs: Additional options (same as extract_text)
            
        Returns:
            Dict[str, Any]: Dictionary containing text, bounding boxes, and metadata
        """
        if not PADDLEOCR_AVAILABLE:
            raise ImportError("PaddleOCR is not available")
        
        file_path = Path(file_path)
        
        try:
            # Load the image
            image = Image.open(file_path)
            image_array = np.array(image)
            
            # Apply preprocessing if requested
            preprocess = kwargs.get('preprocess', True)
            if preprocess:
                image_array = self._preprocess_image(image_array)
            
            # Perform OCR
            ocr_result = self.ocr.ocr(image_array, cls=True)
            
            # Extract text with bounding boxes
            text_blocks = []
            if ocr_result and ocr_result[0]:
                for line in ocr_result[0]:
                    if len(line) >= 2:
                        bbox = line[0]  # Bounding box coordinates
                        text = line[1][0]  # Text content
                        confidence = line[1][1]  # Confidence score
                        
                        text_blocks.append({
                            'bbox': bbox,
                            'text': text,
                            'confidence': confidence
                        })
            
            result = {
                'file_path': str(file_path),
                'text_blocks': text_blocks,
                'total_blocks': len(text_blocks),
                'extraction_method': 'PaddleOCR'
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting text with bbox: {e}")
            raise e
        
        finally:
            if 'image' in locals():
                image.close()
        
        return result
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported languages for PaddleOCR.
        
        Returns:
            List[str]: List of supported language codes
        """
        return [
            'en', 'ch', 'french', 'german', 'korean', 'japan',
            'chinese_cht', 'ta', 'te', 'ka', 'latin', 'arabic',
            'cyrillic', 'devanagari'
        ] 