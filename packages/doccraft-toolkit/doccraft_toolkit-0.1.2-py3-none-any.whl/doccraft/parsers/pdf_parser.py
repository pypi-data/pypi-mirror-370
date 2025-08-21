"""
PyMuPDF PDF parser implementation.

This module provides a PDF parser using PyMuPDF (fitz) library.
PyMuPDF is a fast and feature-rich PDF processing library that can extract
text, images, and metadata from PDF documents.
"""

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    fitz = None

from typing import Dict, Any, Union, List
from pathlib import Path
import logging

from .base_parser import BaseParser


class PDFParser(BaseParser):
    """
    PDF parser using PyMuPDF library.
    
    This parser can extract text, metadata, and images from PDF documents.
    It's designed to be fast and handle various PDF formats including
    scanned documents and text-based PDFs.
    
    Attributes:
        name (str): Parser name ('PyMuPDF')
        version (str): PyMuPDF version
        supported_formats (list): Supported file formats (['.pdf'])
    """
    
    def __init__(self):
        """
        Initialize the PDF parser with PyMuPDF.
        
        Sets up the parser with PyMuPDF-specific configuration and
        determines the version of PyMuPDF being used.
        """
        if not PYMUPDF_AVAILABLE:
            raise ImportError(
                "PyMuPDF is not installed. Please install it with: pip install PyMuPDF"
            )
        
        # Get PyMuPDF version for tracking
        pymupdf_version = fitz.version[0]  # PyMuPDF version string
        
        # Initialize the base parser with PDF-specific settings
        super().__init__(
            name="PyMuPDF",
            version=pymupdf_version,
            supported_formats=['.pdf']
        )
        
        # Set up logging for debugging and monitoring
        self.logger = logging.getLogger(__name__)
    
    def _extract_text_impl(self, file_path: Union[str, Path], **kwargs) -> tuple[str, Dict[str, Any]]:
        """
        Extract text and metadata from a PDF file using PyMuPDF.
        
        This is the core implementation that does the actual PDF parsing.
        It opens the PDF, extracts text from each page, and collects metadata.
        
        Args:
            file_path (Union[str, Path]): Path to the PDF file
            **kwargs: Additional options:
                - pages (list): Specific pages to extract (e.g., [0, 1, 2])
                - include_images (bool): Whether to extract image information
                - text_only (bool): Whether to extract only text (faster)
                
        Returns:
            tuple[str, Dict[str, Any]]: Tuple of (extracted_text, metadata)
        """
        if not PYMUPDF_AVAILABLE:
            raise ImportError("PyMuPDF is not available")
        
        file_path = Path(file_path)
        
        # Parse additional arguments
        pages = kwargs.get('pages', None)  # Which pages to extract
        include_images = kwargs.get('include_images', False)  # Extract image info
        text_only = kwargs.get('text_only', True)  # Text-only extraction
        
        extracted_text = ""
        metadata = {
            'file_path': str(file_path),
            'file_size': file_path.stat().st_size,
            'total_pages': 0,
            'pages_extracted': [],
            'images_found': [],
            'text_blocks': 0,
            'extraction_method': 'PyMuPDF'
        }
        
        try:
            # Open the PDF document
            self.logger.info(f"Opening PDF: {file_path}")
            doc = fitz.open(file_path)
            
            # Store basic document information
            metadata['total_pages'] = len(doc)
            metadata['document_title'] = doc.metadata.get('title', '')
            metadata['document_author'] = doc.metadata.get('author', '')
            metadata['document_subject'] = doc.metadata.get('subject', '')
            metadata['document_creator'] = doc.metadata.get('creator', '')
            
            # Determine which pages to process
            if pages is None:
                # Extract from all pages
                pages_to_process = range(len(doc))
            else:
                # Extract from specified pages only
                pages_to_process = [p for p in pages if 0 <= p < len(doc)]
            
            self.logger.info(f"Processing {len(pages_to_process)} pages")
            
            # Extract text from each page
            for page_num in pages_to_process:
                page = doc[page_num]
                
                # Extract text from the page
                page_text = self._extract_text_from_page(page, text_only)
                
                # Add page text to the overall extracted text
                if page_text.strip():  # Only add non-empty pages
                    extracted_text += f"\n--- Page {page_num + 1} ---\n"
                    extracted_text += page_text
                    metadata['pages_extracted'].append(page_num + 1)
                
                # Extract image information if requested
                if include_images:
                    page_images = self._extract_images_from_page(page, page_num)
                    metadata['images_found'].extend(page_images)
                
                # Count text blocks for analysis
                text_blocks = page.get_text("dict")
                metadata['text_blocks'] += len(text_blocks.get('blocks', []))
            
            # Clean up the extracted text
            extracted_text = self._clean_extracted_text(extracted_text)
            
            self.logger.info(f"Successfully extracted text from {len(metadata['pages_extracted'])} pages")
            
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF: {e}")
            raise e
        
        finally:
            # Always close the document to free memory
            if 'doc' in locals():
                doc.close()
        
        return extracted_text, metadata
    
    def _extract_text_from_page(self, page, text_only: bool = True) -> str:
        """
        Extract text from a single PDF page.
        
        Args:
            page: PyMuPDF page object
            text_only (bool): Whether to extract only text (faster)
            
        Returns:
            str: Extracted text from the page
        """
        if text_only:
            # Simple text extraction - faster but less detailed
            return page.get_text()
        else:
            # Detailed text extraction with formatting information
            text_dict = page.get_text("dict")
            text_blocks = []
            
            # Extract text from each block while preserving some formatting
            for block in text_dict.get('blocks', []):
                if 'lines' in block:  # Text block
                    for line in block['lines']:
                        line_text = ""
                        for span in line['spans']:
                            line_text += span['text']
                        text_blocks.append(line_text)
            
            return '\n'.join(text_blocks)
    
    def _extract_images_from_page(self, page, page_num: int) -> List[Dict[str, Any]]:
        """
        Extract image information from a PDF page.
        
        Args:
            page: PyMuPDF page object
            page_num (int): Page number (0-indexed)
            
        Returns:
            List[Dict[str, Any]]: List of image information dictionaries
        """
        images = []
        
        # Get image list from the page
        image_list = page.get_images()
        
        for img_index, img in enumerate(image_list):
            image_info = {
                'page': page_num + 1,
                'image_index': img_index,
                'width': img[2],
                'height': img[3],
                'colorspace': img[4],
                'bits_per_component': img[5],
                'image_type': img[6]
            }
            images.append(image_info)
        
        return images
    
    def _clean_extracted_text(self, text: str) -> str:
        """
        Clean and format the extracted text.
        
        This method removes excessive whitespace, normalizes line breaks,
        and makes the text more readable.
        
        Args:
            text (str): Raw extracted text
            
        Returns:
            str: Cleaned and formatted text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Strip whitespace from each line
            cleaned_line = line.strip()
            
            # Only keep non-empty lines
            if cleaned_line:
                cleaned_lines.append(cleaned_line)
        
        # Join lines with proper spacing
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Remove multiple consecutive line breaks
        import re
        cleaned_text = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_text)
        
        return cleaned_text.strip()
    
    def extract_metadata_only(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Extract only metadata from a PDF file (faster than full text extraction).
        
        This is useful when you only need document information like
        page count, title, author, etc., without extracting all the text.
        
        Args:
            file_path (Union[str, Path]): Path to the PDF file
            
        Returns:
            Dict[str, Any]: PDF metadata
        """
        if not PYMUPDF_AVAILABLE:
            raise ImportError("PyMuPDF is not available")
        
        file_path = Path(file_path)
        
        try:
            doc = fitz.open(file_path)
            
            metadata = {
                'file_path': str(file_path),
                'file_size': file_path.stat().st_size,
                'total_pages': len(doc),
                'document_title': doc.metadata.get('title', ''),
                'document_author': doc.metadata.get('author', ''),
                'document_subject': doc.metadata.get('subject', ''),
                'document_creator': doc.metadata.get('creator', ''),
                'document_producer': doc.metadata.get('producer', ''),
                'creation_date': doc.metadata.get('creationDate', ''),
                'modification_date': doc.metadata.get('modDate', ''),
                'extraction_method': 'PyMuPDF (metadata only)'
            }
            
            doc.close()
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting metadata from PDF: {e}")
            raise e 