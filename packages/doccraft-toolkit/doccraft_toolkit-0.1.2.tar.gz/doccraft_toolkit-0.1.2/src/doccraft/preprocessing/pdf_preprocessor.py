"""
PDF preprocessing module.

This module provides PDF preprocessing tools for splitting,
merging, and converting PDF documents.
"""

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    fitz = None

from typing import Dict, Any, Union, List, Optional
from pathlib import Path
import logging

from .base_preprocessor import BasePreprocessor


class PDFPreprocessor(BasePreprocessor):
    """
    PDF preprocessing for document manipulation.
    
    This preprocessor provides tools for splitting, merging, and
    converting PDF documents.
    
    Attributes:
        name (str): Preprocessor name ('PDF Preprocessor')
        version (str): Version information
        supported_formats (list): Supported file formats
    """
    
    def __init__(self):
        """
        Initialize the PDF preprocessor.
        
        Sets up the preprocessor with PDF manipulation capabilities
        and determines available libraries.
        """
        if not PYMUPDF_AVAILABLE:
            raise ImportError(
                "PyMuPDF is not installed. Please install with: "
                "pip install PyMuPDF"
            )
        
        # Initialize the base preprocessor
        super().__init__(
            name="PDF Preprocessor"
        )
        self.version = "1.0.0"
        self.supported_formats = ['.pdf']
        self.logger = logging.getLogger(__name__)
    
    def process(self, file_path: Union[str, Path], **kwargs) -> tuple[Union[str, Path], Dict[str, Any]]:
        """
        Process a PDF file with various manipulation techniques.
        
        Args:
            file_path (Union[str, Path]): Path to the input PDF file
            **kwargs: Processing options:
                - operation (str): Operation to perform ('split', 'merge', 'convert')
                - pages (list): Pages to include (for split/merge)
                - output_path (str): Output path for processed file
                - password (str): Password for encrypted PDFs
                
        Returns:
            tuple[Union[str, Path], Dict[str, Any]]: (output_path, metadata)
        """
        if not PYMUPDF_AVAILABLE:
            raise ImportError("PyMuPDF is not available")
        
        file_path = Path(file_path)
        operation = kwargs.get('operation', None)
        
        if operation == 'split':
            return self._split_pdf(file_path, **kwargs)
        elif operation == 'merge':
            return self._merge_pdfs(file_path, **kwargs)
        elif operation == 'convert':
            return self._convert_pdf(file_path, **kwargs)
        elif operation is None:
            # No-op: return original file path and metadata
            metadata = {
                'input_path': str(file_path),
                'operation': 'noop',
                'output_path': str(file_path),
                'note': 'No preprocessing operation performed.'
            }
            return file_path, metadata
        else:
            raise ValueError(f"Unsupported operation: {operation}")
    
    def _split_pdf(self, file_path: Path, **kwargs) -> tuple[Union[str, Path], Dict[str, Any]]:
        """
        Split a PDF into multiple files.
        
        Args:
            file_path (Path): Path to the input PDF file
            **kwargs: Split options:
                - pages (list): List of page ranges to split (e.g., [[0,2], [3,5]])
                - output_dir (str): Output directory for split files
                - password (str): Password for encrypted PDFs
                
        Returns:
            tuple[Union[str, Path], Dict[str, Any]]: (output_path, metadata)
        """
        pages = kwargs.get('pages', None)
        output_dir = kwargs.get('output_dir', file_path.parent)
        password = kwargs.get('password', None)
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        metadata = {
            'input_path': str(file_path),
            'operation': 'split',
            'output_files': [],
            'total_pages': 0,
            'split_ranges': pages
        }
        
        try:
            # Open the PDF
            doc = fitz.open(file_path)
            
            if password:
                doc.authenticate(password)
            
            metadata['total_pages'] = len(doc)
            
            # If no pages specified, split by individual pages
            if pages is None:
                pages = [[i, i] for i in range(len(doc))]
            
            # Create split files
            for i, page_range in enumerate(pages):
                start_page, end_page = page_range
                
                # Create new document for this range
                new_doc = fitz.open()
                new_doc.insert_pdf(doc, from_page=start_page, to_page=end_page)
                
                # Generate output filename
                output_filename = f"{file_path.stem}_part_{i+1:03d}.pdf"
                output_path = output_dir / output_filename
                
                # Save the split document
                new_doc.save(output_path)
                new_doc.close()
                
                metadata['output_files'].append(str(output_path))
            
            doc.close()
            
            self.logger.info(f"PDF split into {len(metadata['output_files'])} files")
            
        except Exception as e:
            self.logger.error(f"Error splitting PDF: {e}")
            raise e
        
        return output_dir, metadata
    
    def _merge_pdfs(self, file_path: Path, **kwargs) -> tuple[Union[str, Path], Dict[str, Any]]:
        """
        Merge multiple PDF files into one.
        
        Args:
            file_path (Path): Path to the first PDF file (or list of files)
            **kwargs: Merge options:
                - additional_files (list): List of additional PDF files to merge
                - output_path (str): Output path for merged file
                - passwords (dict): Dictionary of file paths to passwords
                
        Returns:
            tuple[Union[str, Path], Dict[str, Any]]: (output_path, metadata)
        """
        additional_files = kwargs.get('additional_files', [])
        output_path = kwargs.get('output_path', None)
        passwords = kwargs.get('passwords', {})
        
        # Prepare list of files to merge
        files_to_merge = [file_path] + [Path(f) for f in additional_files]
        
        # Set default output path if not provided
        if output_path is None:
            output_path = file_path.parent / f"merged_{file_path.name}"
        else:
            output_path = Path(output_path)
        
        metadata = {
            'input_files': [str(f) for f in files_to_merge],
            'output_path': str(output_path),
            'operation': 'merge',
            'total_files': len(files_to_merge),
            'total_pages': 0
        }
        
        try:
            # Create new document for merging
            merged_doc = fitz.open()
            
            # Merge each file
            for pdf_file in files_to_merge:
                # Open the PDF
                doc = fitz.open(pdf_file)
                
                # Authenticate if password provided
                if str(pdf_file) in passwords:
                    doc.authenticate(passwords[str(pdf_file)])
                
                # Insert all pages from this document
                merged_doc.insert_pdf(doc)
                metadata['total_pages'] += len(doc)
                
                doc.close()
            
            # Save the merged document
            merged_doc.save(output_path)
            merged_doc.close()
            
            self.logger.info(f"PDFs merged into: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error merging PDFs: {e}")
            raise e
        
        return output_path, metadata
    
    def _convert_pdf(self, file_path: Path, **kwargs) -> tuple[Union[str, Path], Dict[str, Any]]:
        """
        Convert PDF to images or other formats.
        
        Args:
            file_path (Path): Path to the input PDF file
            **kwargs: Conversion options:
                - format (str): Output format ('png', 'jpg', 'tiff')
                - dpi (int): Resolution for image conversion
                - pages (list): Specific pages to convert
                - output_dir (str): Output directory for converted files
                - password (str): Password for encrypted PDFs
                
        Returns:
            tuple[Union[str, Path], Dict[str, Any]]: (output_path, metadata)
        """
        format_type = kwargs.get('format', 'png')
        dpi = kwargs.get('dpi', 300)
        pages = kwargs.get('pages', None)
        output_dir = kwargs.get('output_dir', file_path.parent)
        password = kwargs.get('password', None)
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        metadata = {
            'input_path': str(file_path),
            'operation': 'convert',
            'output_format': format_type,
            'dpi': dpi,
            'output_files': [],
            'total_pages': 0
        }
        
        try:
            # Open the PDF
            doc = fitz.open(file_path)
            
            if password:
                doc.authenticate(password)
            
            metadata['total_pages'] = len(doc)
            
            # Determine which pages to convert
            if pages is None:
                pages_to_convert = range(len(doc))
            else:
                pages_to_convert = [p for p in pages if 0 <= p < len(doc)]
            
            # Convert each page
            for page_num in pages_to_convert:
                page = doc[page_num]
                
                # Create transformation matrix for desired DPI
                mat = fitz.Matrix(dpi/72, dpi/72)
                
                # Render page to image
                pix = page.get_pixmap(matrix=mat)
                
                # Generate output filename
                output_filename = f"{file_path.stem}_page_{page_num+1:03d}.{format_type}"
                output_path = output_dir / output_filename
                
                # Save the image
                pix.save(output_path)
                metadata['output_files'].append(str(output_path))
            
            doc.close()
            
            self.logger.info(f"PDF converted to {len(metadata['output_files'])} {format_type} files")
            
        except Exception as e:
            self.logger.error(f"Error converting PDF: {e}")
            raise e
        
        return output_dir, metadata
    
    def extract_pages(self, file_path: Union[str, Path], pages: List[int], 
                     output_path: Optional[Union[str, Path]] = None, **kwargs) -> tuple[Union[str, Path], Dict[str, Any]]:
        """
        Extract specific pages from a PDF.
        
        Args:
            file_path (Union[str, Path]): Path to the input PDF file
            pages (List[int]): List of page numbers to extract (0-indexed)
            output_path (Optional[Union[str, Path]]): Output path for extracted pages
            **kwargs: Additional options (password, etc.)
            
        Returns:
            tuple[Union[str, Path], Dict[str, Any]]: (output_path, metadata)
        """
        file_path = Path(file_path)
        
        if output_path is None:
            output_path = file_path.parent / f"extracted_{file_path.name}"
        else:
            output_path = Path(output_path)
        
        # Use the split operation with specific page ranges
        split_kwargs = {
            'operation': 'split',
            'pages': [[p, p] for p in pages],
            'output_path': str(output_path),
            **kwargs
        }
        
        return self.process(file_path, **split_kwargs)
    
    def rotate_pages(self, file_path: Union[str, Path], rotation: int = 90, 
                    pages: Optional[List[int]] = None, **kwargs) -> tuple[Union[str, Path], Dict[str, Any]]:
        """
        Rotate pages in a PDF.
        
        Args:
            file_path (Union[str, Path]): Path to the input PDF file
            rotation (int): Rotation angle in degrees (90, 180, 270)
            pages (Optional[List[int]]): Specific pages to rotate (None = all pages)
            **kwargs: Additional options (output_path, password, etc.)
            
        Returns:
            tuple[Union[str, Path], Dict[str, Any]]: (output_path, metadata)
        """
        if not PYMUPDF_AVAILABLE:
            raise ImportError("PyMuPDF is not available")
        
        file_path = Path(file_path)
        output_path = kwargs.get('output_path', None)
        password = kwargs.get('password', None)
        
        if output_path is None:
            output_path = file_path.parent / f"rotated_{file_path.name}"
        else:
            output_path = Path(output_path)
        
        metadata = {
            'input_path': str(file_path),
            'output_path': str(output_path),
            'operation': 'rotate',
            'rotation_angle': rotation,
            'pages_rotated': pages or 'all'
        }
        
        try:
            # Open the PDF
            doc = fitz.open(file_path)
            
            if password:
                doc.authenticate(password)
            
            # Determine which pages to rotate
            if pages is None:
                pages_to_rotate = range(len(doc))
            else:
                pages_to_rotate = [p for p in pages if 0 <= p < len(doc)]
            
            # Rotate each page
            for page_num in pages_to_rotate:
                page = doc[page_num]
                page.set_rotation(rotation)
            
            # Save the modified document
            doc.save(output_path)
            doc.close()
            
            self.logger.info(f"PDF pages rotated by {rotation} degrees")
            
        except Exception as e:
            self.logger.error(f"Error rotating PDF pages: {e}")
            raise e
        
        return output_path, metadata 