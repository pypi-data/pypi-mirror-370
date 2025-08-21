"""
Document postprocessing module.

Contains tools for output processing:
- Text cleanup and formatting
- Table extraction and conversion
- Output standardization (JSON/CSV)
"""

# Import the base postprocessor class
from .base_postprocessor import BasePostprocessor

# Import specific postprocessor implementations
from .text_postprocessor import TextPostprocessor
from .table_postprocessor import TablePostprocessor

# Define what gets imported when someone does "from doccraft.postprocessing import *"
__all__ = [
    'BasePostprocessor',
    'TextPostprocessor',
    'TablePostprocessor',
]

# Postprocessor registry for dynamic lookup
POSTPROCESSOR_REGISTRY = {
    'text': TextPostprocessor,
    'table': TablePostprocessor,
}

def get_postprocessor(postprocessor_name: str):
    """
    Retrieve a postprocessor instance by name from the registry.
    Args:
        postprocessor_name (str): The key for the postprocessor (e.g., 'text', 'table')
    Returns:
        BasePostprocessor: An instance of the requested postprocessor.
    Raises:
        ValueError: If the postprocessor name is not found in the registry.
    """
    postprocessor_cls = POSTPROCESSOR_REGISTRY.get(postprocessor_name.lower())
    if postprocessor_cls is None:
        raise ValueError(f"Postprocessor '{postprocessor_name}' not found. Available: {list(POSTPROCESSOR_REGISTRY.keys())}")
    return postprocessor_cls()

__all__.extend(['POSTPROCESSOR_REGISTRY', 'get_postprocessor']) 