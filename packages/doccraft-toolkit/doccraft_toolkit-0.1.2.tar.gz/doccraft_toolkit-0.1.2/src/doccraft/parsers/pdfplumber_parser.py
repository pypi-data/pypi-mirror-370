"""
pdfplumber PDF parser implementation.

This module provides a PDF parser using pdfplumber library.
pdfplumber is excellent for extracting text, tables, and maintaining
text positioning information from PDF documents.
"""

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    pdfplumber = None

from typing import Dict, Any, Union, List
from pathlib import Path
import logging

from .base_parser import BaseParser


class PDFPlumberParser(BaseParser):
    """
    PDF parser using pdfplumber library.
    
    This parser is particularly good at extracting tables and maintaining
    text positioning information. It's excellent for structured documents
    and forms.
    
    Attributes:
        name (str): Parser name ('pdfplumber')
        version (str): pdfplumber version
        supported_formats (list): Supported file formats (['.pdf'])
    """
    
    def __init__(self):
        """
        Initialize the PDF parser with pdfplumber.
        
        Sets up the parser with pdfplumber-specific configuration and
        determines the version of pdfplumber being used.
        """
        if not PDFPLUMBER_AVAILABLE:
            raise ImportError(
                "pdfplumber is not installed. Please install it with: pip install pdfplumber"
            )
        
        # Get pdfplumber version for tracking
        pdfplumber_version = pdfplumber.__version__
        
        # Initialize the base parser with PDF-specific settings
        super().__init__(
            name="pdfplumber",
            version=pdfplumber_version,
            supported_formats=['.pdf']
        )
        
        # Set up logging for debugging and monitoring
        self.logger = logging.getLogger(__name__)
    
    def _extract_text_impl(self, file_path: Union[str, Path], **kwargs) -> tuple[str, Dict[str, Any]]:
        """
        Extract text and metadata from a PDF file using pdfplumber.
        
        This is the core implementation that does the actual PDF parsing.
        It opens the PDF, extracts text from each page, and collects metadata.
        
        Args:
            file_path (Union[str, Path]): Path to the PDF file
            **kwargs: Additional options:
                - pages (list): Specific pages to extract (e.g., [0, 1, 2])
                - extract_tables (bool): Whether to extract table information
                - preserve_layout (bool): Whether to preserve text layout
                - text_only (bool): Whether to extract only text (faster)
                
        Returns:
            tuple[str, Dict[str, Any]]: Tuple of (extracted_text, metadata)
        """
        if not PDFPLUMBER_AVAILABLE:
            raise ImportError("pdfplumber is not available")
        
        file_path = Path(file_path)
        
        # Parse additional arguments
        pages = kwargs.get('pages', None)  # Which pages to extract
        extract_tables = kwargs.get('extract_tables', True)  # Extract table info
        preserve_layout = kwargs.get('preserve_layout', False)  # Preserve layout
        text_only = kwargs.get('text_only', False)  # Text-only extraction
        
        extracted_text = ""
        metadata = {
            'file_path': str(file_path),
            'file_size': file_path.stat().st_size,
            'total_pages': 0,
            'pages_extracted': [],
            'tables_found': [],
            'text_blocks': 0,
            'extraction_method': 'pdfplumber'
        }
        
        try:
            # Open the PDF document
            self.logger.info(f"Opening PDF with pdfplumber: {file_path}")
            with pdfplumber.open(file_path) as pdf:
                # Store basic document information
                metadata['total_pages'] = len(pdf.pages)
                
                # Determine which pages to process
                if pages is None:
                    # Extract from all pages
                    pages_to_process = range(len(pdf.pages))
                else:
                    # Extract from specified pages only
                    pages_to_process = [p for p in pages if 0 <= p < len(pdf.pages)]
                
                self.logger.info(f"Processing {len(pages_to_process)} pages")
                
                # Extract text from each page
                for page_num in pages_to_process:
                    page = pdf.pages[page_num]
                    
                    # Extract text from the page
                    page_text = self._extract_text_from_page(
                        page, text_only, preserve_layout
                    )
                    
                    # Add page text to the overall extracted text
                    if page_text.strip():  # Only add non-empty pages
                        extracted_text += f"\n--- Page {page_num + 1} ---\n"
                        extracted_text += page_text
                        metadata['pages_extracted'].append(page_num + 1)
                    
                    # Extract table information if requested
                    if extract_tables:
                        page_tables = self._extract_tables_from_page(page, page_num)
                        metadata['tables_found'].extend(page_tables)
                    
                    # Count text blocks for analysis
                    if hasattr(page, 'chars'):
                        metadata['text_blocks'] += len(page.chars)
            
            # Clean up the extracted text
            extracted_text = self._clean_extracted_text(extracted_text)
            
            self.logger.info(f"Successfully extracted text from {len(metadata['pages_extracted'])} pages")
            
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF: {e}")
            raise e
        
        return extracted_text, metadata
    
    def _extract_text_from_page(self, page, text_only: bool = False, preserve_layout: bool = False) -> str:
        """
        Extract text from a single PDF page.
        
        Args:
            page: pdfplumber page object
            text_only (bool): Whether to extract only text (faster)
            preserve_layout (bool): Whether to preserve text layout
            
        Returns:
            str: Extracted text from the page
        """
        if text_only:
            # Simple text extraction - faster but less detailed
            return page.extract_text()
        elif preserve_layout:
            # Extract text with layout preservation
            return self._extract_text_with_layout(page)
        else:
            # Standard text extraction
            return page.extract_text()
    
    def _extract_text_with_layout(self, page) -> str:
        """
        Extract text while preserving layout information.
        
        Args:
            page: pdfplumber page object
            
        Returns:
            str: Extracted text with layout preserved
        """
        text_lines = []
        
        # Get all text objects with their positions
        chars = page.chars
        
        if not chars:
            return ""
        
        # Group characters by their y-position (lines)
        lines = {}
        for char in chars:
            y_pos = round(char['top'], 2)  # Round to avoid floating point issues
            if y_pos not in lines:
                lines[y_pos] = []
            lines[y_pos].append(char)
        
        # Sort lines by y-position (top to bottom)
        sorted_lines = sorted(lines.items(), key=lambda x: x[0])
        
        # Process each line
        for y_pos, line_chars in sorted_lines:
            # Sort characters in line by x-position (left to right)
            line_chars.sort(key=lambda x: x['x0'])
            
            # Extract text from characters in this line
            line_text = ''.join(char['text'] for char in line_chars)
            text_lines.append(line_text)
        
        return '\n'.join(text_lines)
    
    def _extract_tables_from_page(self, page, page_num: int) -> List[Dict[str, Any]]:
        """
        Extract table information from a PDF page.
        
        Args:
            page: pdfplumber page object
            page_num (int): Page number (0-indexed)
            
        Returns:
            List[Dict[str, Any]]: List of table information dictionaries
        """
        tables = []
        
        try:
            # Find tables on the page
            page_tables = page.find_tables()
            
            for table_idx, table in enumerate(page_tables):
                table_info = {
                    'page': page_num + 1,
                    'table_index': table_idx,
                    'bbox': table.bbox,
                    'rows': len(table.extract()),
                    'columns': len(table.extract()[0]) if table.extract() else 0
                }
                tables.append(table_info)
                
        except Exception as e:
            self.logger.warning(f"Error extracting tables from page {page_num + 1}: {e}")
        
        return tables
    
    def _clean_extracted_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text (str): Raw extracted text
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Strip whitespace from each line
            cleaned_line = line.strip()
            if cleaned_line:  # Only keep non-empty lines
                cleaned_lines.append(cleaned_line)
        
        # Join lines with single newlines
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Remove multiple consecutive newlines
        while '\n\n\n' in cleaned_text:
            cleaned_text = cleaned_text.replace('\n\n\n', '\n\n')
        
        return cleaned_text.strip()
    
    def extract_tables(self, file_path: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """
        Extract tables from a PDF file.
        
        Args:
            file_path (Union[str, Path]): Path to the PDF file
            **kwargs: Additional options (same as extract_text)
            
        Returns:
            Dict[str, Any]: Dictionary containing tables and metadata
        """
        if not PDFPLUMBER_AVAILABLE:
            raise ImportError("pdfplumber is not available")
        
        file_path = Path(file_path)
        pages = kwargs.get('pages', None)
        
        tables_data = {
            'file_path': str(file_path),
            'tables': [],
            'total_tables': 0
        }
        
        try:
            with pdfplumber.open(file_path) as pdf:
                # Determine which pages to process
                if pages is None:
                    pages_to_process = range(len(pdf.pages))
                else:
                    pages_to_process = [p for p in pages if 0 <= p < len(pdf.pages)]
                
                for page_num in pages_to_process:
                    page = pdf.pages[page_num]
                    
                    try:
                        # Extract tables from the page
                        page_tables = page.extract_tables()
                        
                        for table_idx, table in enumerate(page_tables):
                            table_data = {
                                'page': page_num + 1,
                                'table_index': table_idx,
                                'data': table,
                                'rows': len(table),
                                'columns': len(table[0]) if table else 0
                            }
                            tables_data['tables'].append(table_data)
                            
                    except Exception as e:
                        self.logger.warning(f"Error extracting tables from page {page_num + 1}: {e}")
                
                tables_data['total_tables'] = len(tables_data['tables'])
                
        except Exception as e:
            self.logger.error(f"Error extracting tables from PDF: {e}")
            raise e
        
        return tables_data 