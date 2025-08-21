"""
DocCraft: Intelligent Document Processing & Benchmarking

A Python package for unified document parsing, preprocessing, and benchmarking.
"""

__version__ = "0.1.2"
__author__ = "Simon Wu"
__email__ = "simon.wu@rwth-aachen.de"

# Import main components for easy access
from .parsers import *
from .preprocessing import *
from .postprocessing import *
from .benchmarking import *

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    # Parser classes
    "BaseParser",
    "PDFParser", 
    "PDFPlumberParser",
    "TesseractParser",
    "PaddleOCRParser",
    # Preprocessor classes
    "BasePreprocessor",
    "ImagePreprocessor",
    "PDFPreprocessor",
    # Postprocessor classes
    "BasePostprocessor", 
    "TextPostprocessor",
    "TablePostprocessor",
    # Benchmarker classes
    "BaseBenchmarker",
    "PerformanceBenchmarker",
    "AccuracyBenchmarker",
    "DocVQABenchmarker",
] 