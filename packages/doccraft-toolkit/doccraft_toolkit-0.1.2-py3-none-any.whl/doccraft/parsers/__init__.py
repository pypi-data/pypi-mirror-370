"""
Document parsers module.

Contains implementations for various document parsing methods:
- OCR engines (Tesseract [key: 'tesseract'], PaddleOCR [key: 'paddleocr'])
- PDF libraries (PyMuPDF, pdfplumber)
- AI model integrations (LayoutLM, DeepSeek-VL)
"""

# Import the base parser class
from .base_parser import BaseParser

# Import specific parser implementations
from .pdf_parser import PDFParser
from .pdfplumber_parser import PDFPlumberParser
from .tesseract_parser import TesseractParser
from .paddle_ocr_parser import PaddleOCRParser
"""
Important: Avoid importing AI parsers at module import time when optional
dependencies (e.g., torch, transformers) are not installed. Keep all AI
imports inside a guarded try/except so core installs work without extras.
"""

# Import AI parsers (optional dependencies)
try:
    from .base_ai_parser import BaseAIParser
    from .layoutlmv3_parser import LayoutLMv3Parser
    from .deepseek_vl_parser import DeepSeekVLParser
    from .qwen_vl_parser import QwenVLParser
    AI_PARSERS_AVAILABLE = True
except ImportError:
    AI_PARSERS_AVAILABLE = False
    BaseAIParser = None
    LayoutLMv3Parser = None
    DeepSeekVLParser = None
    QwenVLParser = None

# Define what gets imported when someone does "from doccraft.parsers import *"
__all__ = [
    'BaseParser',
    'PDFParser',
    'PDFPlumberParser',
    'TesseractParser',
    'PaddleOCRParser',
]

# Add AI parsers to __all__ if available
if AI_PARSERS_AVAILABLE:
    __all__.extend([
        'BaseAIParser',
        'LayoutLMv3Parser',
        'DeepSeekVLParser',
        'QwenVLParser',
    ])

# Parser registry for dynamic lookup
PARSER_REGISTRY = {
    'pdf': PDFParser,
    'pdfplumber': PDFPlumberParser,
    'tesseract': TesseractParser,
    'paddleocr': PaddleOCRParser,
}

if AI_PARSERS_AVAILABLE:
    PARSER_REGISTRY.update({
        'layoutlmv3': LayoutLMv3Parser,
        'deepseekvl': DeepSeekVLParser,
        'qwenvl': QwenVLParser,
    })

def get_parser(parser_name: str):
    """
    Retrieve a parser instance by name from the registry.
    Args:
        parser_name (str): The key for the parser (e.g., 'tesseract', 'paddleocr', 'pdf', etc.)
    Returns:
        BaseParser: An instance of the requested parser.
    Raises:
        ValueError: If the parser name is not found in the registry.
    """
    parser_cls = PARSER_REGISTRY.get(parser_name.lower())
    if parser_cls is None:
        raise ValueError(f"Parser '{parser_name}' not found. Available: {list(PARSER_REGISTRY.keys())}")
    return parser_cls()

__all__.append('get_parser') 