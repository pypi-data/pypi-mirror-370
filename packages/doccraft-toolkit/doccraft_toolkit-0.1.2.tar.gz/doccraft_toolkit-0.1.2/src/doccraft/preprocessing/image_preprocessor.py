"""
Image preprocessing module.

This module provides image preprocessing tools for enhancing
document images before OCR (e.g., Tesseract, PaddleOCR) processing.
"""

try:
    import cv2
    import numpy as np
    from PIL import Image, ImageEnhance, ImageFilter
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    cv2 = None
    np = None
    Image = None
    ImageEnhance = None
    ImageFilter = None

from typing import Dict, Any, Union, Optional
from pathlib import Path
import logging

from .base_preprocessor import BasePreprocessor


class ImagePreprocessor(BasePreprocessor):
    """
    Image preprocessing for document enhancement.
    
    This preprocessor applies various image enhancement techniques
    to improve OCR accuracy and document readability (e.g., for Tesseract or PaddleOCR).
    
    Attributes:
        name (str): Preprocessor name ('Image Preprocessor')
        version (str): Version information
        supported_formats (list): Supported image formats
    """
    
    def __init__(self):
        """
        Initialize the image preprocessor.
        
        Sets up the preprocessor with image processing capabilities
        and determines available libraries.
        """
        if not OPENCV_AVAILABLE:
            raise ImportError(
                "OpenCV and PIL are not installed. Please install with: "
                "pip install opencv-python Pillow"
            )
        
        # Initialize the base preprocessor (only pass name)
        super().__init__(
            name="Image Preprocessor"
        )
        self.version = "1.0.0"
        self.supported_formats = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']
        self.logger = logging.getLogger(__name__)
    
    def process(self, file_path: Union[str, Path], **kwargs) -> tuple[Union[str, Path], Dict[str, Any]]:
        """
        Process an image file with various enhancement techniques.
        
        Args:
            file_path (Union[str, Path]): Path to the input image file
            **kwargs: Processing options:
                - deskew (bool): Whether to deskew the image
                - denoise (bool): Whether to apply noise reduction
                - enhance_contrast (bool): Whether to enhance contrast
                - binarize (bool): Whether to binarize the image
                - resize_factor (float): Resize factor (1.0 = no resize)
                - output_path (str): Output path for processed image
                
        Returns:
            tuple[Union[str, Path], Dict[str, Any]]: (output_path, metadata)
        """
        if not OPENCV_AVAILABLE:
            raise ImportError("OpenCV is not available")
        
        file_path = Path(file_path)
        
        # Parse processing options
        deskew = kwargs.get('deskew', True)
        denoise = kwargs.get('denoise', True)
        enhance_contrast = kwargs.get('enhance_contrast', True)
        binarize = kwargs.get('binarize', False)
        resize_factor = kwargs.get('resize_factor', 1.0)
        output_path = kwargs.get('output_path', None)
        
        # Set default output path if not provided
        if output_path is None:
            output_path = file_path.parent / f"processed_{file_path.name}"
        else:
            output_path = Path(output_path)
        
        metadata = {
            'input_path': str(file_path),
            'output_path': str(output_path),
            'processing_steps': [],
            'image_info': {},
            'enhancement_applied': False
        }
        
        try:
            # Load the image
            self.logger.info(f"Loading image: {file_path}")
            image = cv2.imread(str(file_path))
            
            if image is None:
                raise ValueError(f"Could not load image: {file_path}")
            
            # Store original image information
            metadata['image_info'] = {
                'original_size': image.shape,
                'original_width': image.shape[1],
                'original_height': image.shape[0],
                'channels': image.shape[2] if len(image.shape) > 2 else 1
            }
            
            # Apply preprocessing steps
            if resize_factor != 1.0:
                image = self._resize_image(image, resize_factor)
                metadata['processing_steps'].append('resize')
            
            if deskew:
                image = self._deskew_image(image)
                metadata['processing_steps'].append('deskew')
            
            if denoise:
                image = self._denoise_image(image)
                metadata['processing_steps'].append('denoise')
            
            if enhance_contrast:
                image = self._enhance_contrast(image)
                metadata['processing_steps'].append('contrast_enhancement')
            
            if binarize:
                image = self._binarize_image(image)
                metadata['processing_steps'].append('binarization')
            
            # Save the processed image
            cv2.imwrite(str(output_path), image)
            
            # Update metadata
            metadata['enhancement_applied'] = True
            metadata['final_size'] = image.shape
            metadata['final_width'] = image.shape[1]
            metadata['final_height'] = image.shape[0]
            
            self.logger.info(f"Image processing completed. Output: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error processing image: {e}")
            raise e
        
        return output_path, metadata
    
    def _resize_image(self, image: np.ndarray, factor: float) -> np.ndarray:
        """
        Resize image by a given factor.
        
        Args:
            image (np.ndarray): Input image
            factor (float): Resize factor
            
        Returns:
            np.ndarray: Resized image
        """
        if factor == 1.0:
            return image
        
        height, width = image.shape[:2]
        new_width = int(width * factor)
        new_height = int(height * factor)
        
        return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
    
    def _deskew_image(self, image: np.ndarray) -> np.ndarray:
        """
        Deskew (rotate) image to correct orientation.
        
        Args:
            image (np.ndarray): Input image
            
        Returns:
            np.ndarray: Deskewed image
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply threshold to get binary image
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return image
        
        # Find the largest contour (assumed to be the main content)
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Fit a rotated rectangle
        rect = cv2.minAreaRect(largest_contour)
        angle = rect[2]
        
        # Normalize angle
        if angle < -45:
            angle = 90 + angle
        
        # Rotate the image
        if abs(angle) > 0.5:  # Only rotate if angle is significant
            height, width = image.shape[:2]
            center = (width // 2, height // 2)
            
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(image, rotation_matrix, (width, height), 
                                   flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            return rotated
        
        return image
    
    def _denoise_image(self, image: np.ndarray) -> np.ndarray:
        """
        Apply noise reduction to the image.
        
        Args:
            image (np.ndarray): Input image
            
        Returns:
            np.ndarray: Denoised image
        """
        # Apply bilateral filter for noise reduction while preserving edges
        denoised = cv2.bilateralFilter(image, 9, 75, 75)
        return denoised
    
    def _enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """
        Enhance image contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization).
        
        Args:
            image (np.ndarray): Input image
            
        Returns:
            np.ndarray: Contrast-enhanced image
        """
        # Convert to LAB color space
        if len(image.shape) == 3:
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            
            # Apply CLAHE to L channel
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            lab[:, :, 0] = clahe.apply(lab[:, :, 0])
            
            # Convert back to BGR
            enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        else:
            # For grayscale images
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(image)
        
        return enhanced
    
    def _binarize_image(self, image: np.ndarray) -> np.ndarray:
        """
        Convert image to binary (black and white) using adaptive thresholding.
        
        Args:
            image (np.ndarray): Input image
            
        Returns:
            np.ndarray: Binary image
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply adaptive thresholding
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY, 11, 2)
        
        return binary
    
    def enhance_for_ocr(self, file_path: Union[str, Path], **kwargs) -> tuple[Union[str, Path], Dict[str, Any]]:
        """
        Apply OCR-optimized preprocessing to an image.
        
        This method applies a specific set of enhancements that are
        particularly beneficial for OCR accuracy (e.g., for Tesseract or PaddleOCR).
        
        Args:
            file_path (Union[str, Path]): Path to the input image file
            **kwargs: Additional options (same as process method)
            
        Returns:
            tuple[Union[str, Path], Dict[str, Any]]: (output_path, metadata)
        """
        # Set default OCR-optimized parameters (for Tesseract/PaddleOCR)
        ocr_kwargs = {
            'deskew': True,
            'denoise': True,
            'enhance_contrast': True,
            'binarize': False,  # Usually not needed for modern OCR engines
            'resize_factor': 1.0
        }
        
        # Update with user-provided parameters
        ocr_kwargs.update(kwargs)
        
        return self.process(file_path, **ocr_kwargs) 