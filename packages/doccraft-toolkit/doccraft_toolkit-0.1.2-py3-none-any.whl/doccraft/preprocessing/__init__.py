"""
Document preprocessing module.

Contains tools for document preparation:
- Image enhancement (deskew, binarization)
- PDF splitting and conversion
- Format standardization
"""

# Import the base preprocessor class
from .base_preprocessor import BasePreprocessor

# Import specific preprocessor implementations
from .image_preprocessor import ImagePreprocessor
from .pdf_preprocessor import PDFPreprocessor

# Define what gets imported when someone does "from doccraft.preprocessing import *"
__all__ = [
    'BasePreprocessor',
    'ImagePreprocessor',
    'PDFPreprocessor',
]

# Preprocessor registry for dynamic lookup
PREPROCESSOR_REGISTRY = {
    'image': ImagePreprocessor,
    'pdf': PDFPreprocessor,
}

def get_preprocessor(preprocessor_name: str):
    """
    Retrieve a preprocessor instance by name from the registry.
    Args:
        preprocessor_name (str): The key for the preprocessor (e.g., 'image', 'pdf')
    Returns:
        BasePreprocessor: An instance of the requested preprocessor.
    Raises:
        ValueError: If the preprocessor name is not found in the registry.
    """
    preprocessor_cls = PREPROCESSOR_REGISTRY.get(preprocessor_name.lower())
    if preprocessor_cls is None:
        raise ValueError(f"Preprocessor '{preprocessor_name}' not found. Available: {list(PREPROCESSOR_REGISTRY.keys())}")
    return preprocessor_cls()

__all__.extend(['PREPROCESSOR_REGISTRY', 'get_preprocessor']) 