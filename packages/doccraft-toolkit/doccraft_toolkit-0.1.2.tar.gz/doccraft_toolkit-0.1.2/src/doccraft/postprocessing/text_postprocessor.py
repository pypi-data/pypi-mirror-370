"""
Text postprocessing module.

This module provides text postprocessing tools for cleaning,
formatting, and structuring extracted text.
"""

import re
from typing import Dict, Any, Union, List, Optional
from pathlib import Path
import logging

from .base_postprocessor import BasePostprocessor


class TextPostprocessor(BasePostprocessor):
    """
    Text postprocessing for cleaning and formatting.
    
    This postprocessor applies various text cleaning and formatting
    techniques to improve the quality of extracted text.
    
    Attributes:
        name (str): Postprocessor name ('Text Postprocessor')
        version (str): Version information
        supported_formats (list): Supported output formats
    """
    
    def __init__(self):
        """
        Initialize the text postprocessor.
        
        Sets up the postprocessor with text processing capabilities.
        """
        # Initialize the base postprocessor
        super().__init__(
            name="Text Postprocessor",
            version="1.0.0",
            supported_formats=['.txt', '.json', '.csv']
        )
        
        self.logger = logging.getLogger(__name__)
    
    def process(self, text: str, **kwargs) -> tuple[str, Dict[str, Any]]:
        """
        Process extracted text with various cleaning and formatting techniques.
        
        Args:
            text (str): Input text to process
            **kwargs: Processing options:
                - remove_extra_whitespace (bool): Remove excessive whitespace
                - fix_line_breaks (bool): Fix inconsistent line breaks
                - remove_special_chars (bool): Remove special characters
                - normalize_quotes (bool): Normalize quote characters
                - fix_common_ocr_errors (bool): Fix common OCR mistakes (e.g., for Tesseract or PaddleOCR)
                - extract_paragraphs (bool): Extract structured paragraphs
                - output_format (str): Output format ('text', 'json', 'csv')
                
        Returns:
            tuple[str, Dict[str, Any]]: (processed_text, metadata)
        """
        # Parse processing options
        remove_extra_whitespace = kwargs.get('remove_extra_whitespace', True)
        fix_line_breaks = kwargs.get('fix_line_breaks', True)
        remove_special_chars = kwargs.get('remove_special_chars', False)
        normalize_quotes = kwargs.get('normalize_quotes', True)
        fix_common_ocr_errors = kwargs.get('fix_common_ocr_errors', True)
        extract_paragraphs = kwargs.get('extract_paragraphs', False)
        output_format = kwargs.get('output_format', 'text')
        
        metadata = {
            'original_length': len(text),
            'processing_steps': [],
            'text_statistics': {},
            'output_format': output_format
        }
        
        processed_text = text
        
        # Apply processing steps
        if remove_extra_whitespace:
            processed_text = self._remove_extra_whitespace(processed_text)
            metadata['processing_steps'].append('remove_extra_whitespace')
        
        if fix_line_breaks:
            processed_text = self._fix_line_breaks(processed_text)
            metadata['processing_steps'].append('fix_line_breaks')
        
        if remove_special_chars:
            processed_text = self._remove_special_chars(processed_text)
            metadata['processing_steps'].append('remove_special_chars')
        
        if normalize_quotes:
            processed_text = self._normalize_quotes(processed_text)
            metadata['processing_steps'].append('normalize_quotes')
        
        if fix_common_ocr_errors:
            processed_text = self._fix_common_ocr_errors(processed_text)
            metadata['processing_steps'].append('fix_common_ocr_errors')
        
        if extract_paragraphs:
            processed_text = self._extract_paragraphs(processed_text)
            metadata['processing_steps'].append('extract_paragraphs')
        
        # Convert to desired output format
        if output_format == 'json':
            processed_text = self._convert_to_json(processed_text)
        elif output_format == 'csv':
            processed_text = self._convert_to_csv(processed_text)
        
        # Update metadata
        metadata['final_length'] = len(processed_text)
        metadata['text_statistics'] = self._calculate_text_statistics(processed_text)
        
        self.logger.info(f"Text processing completed. Applied {len(metadata['processing_steps'])} steps")
        
        return processed_text, metadata
    
    def _remove_extra_whitespace(self, text: str) -> str:
        """
        Remove excessive whitespace from text.
        
        Args:
            text (str): Input text
            
        Returns:
            str: Text with normalized whitespace
        """
        # Remove multiple spaces
        text = re.sub(r' +', ' ', text)
        
        # Remove multiple newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove leading/trailing whitespace from lines
        lines = text.split('\n')
        cleaned_lines = [line.strip() for line in lines]
        
        # Remove empty lines at the beginning and end
        while cleaned_lines and not cleaned_lines[0].strip():
            cleaned_lines.pop(0)
        while cleaned_lines and not cleaned_lines[-1].strip():
            cleaned_lines.pop()
        
        return '\n'.join(cleaned_lines)
    
    def _fix_line_breaks(self, text: str) -> str:
        """
        Fix inconsistent line breaks and formatting.
        
        Args:
            text (str): Input text
            
        Returns:
            str: Text with consistent line breaks
        """
        # Replace various line break characters with standard newlines
        text = text.replace('\r\n', '\n')
        text = text.replace('\r', '\n')
        
        # Fix hyphenated words at line breaks
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
        
        # Fix broken sentences at line breaks
        text = re.sub(r'([a-z])\s*\n\s*([A-Z])', r'\1 \2', text)
        
        return text
    
    def _remove_special_chars(self, text: str) -> str:
        """
        Remove special characters while preserving readability.
        
        Args:
            text (str): Input text
            
        Returns:
            str: Text with special characters removed
        """
        # Keep alphanumeric, spaces, basic punctuation, and newlines
        text = re.sub(r'[^\w\s.,!?;:()\-\'\"/\n]', '', text)
        
        return text
    
    def _normalize_quotes(self, text: str) -> str:
        """
        Normalize quote characters to standard ASCII quotes.
        
        Args:
            text (str): Input text
            
        Returns:
            str: Text with normalized quotes
        """
        # Replace smart quotes with standard quotes
        text = text.replace('"', '"')
        text = text.replace('"', '"')
        text = text.replace(''', "'")
        text = text.replace(''', "'")
        
        return text
    
    def _fix_common_ocr_errors(self, text: str) -> str:
        """
        Fix common OCR errors and typos (e.g., for Tesseract or PaddleOCR).
        
        Args:
            text (str): Input text
            
        Returns:
            str: Text with common OCR errors fixed
        """
        # Common OCR replacements (for Tesseract/PaddleOCR)
        replacements = {
            '0': 'O',  # Zero to O (context-dependent)
            '1': 'l',  # One to lowercase L (context-dependent)
            '5': 'S',  # Five to S (context-dependent)
            '8': 'B',  # Eight to B (context-dependent)
            '|': 'I',  # Pipe to I
            'l': 'I',  # Lowercase L to I (context-dependent)
        }
        
        # Apply replacements (be careful with context)
        for old, new in replacements.items():
            # Only replace in specific contexts to avoid over-correction
            if old == '0' and new == 'O':
                # Only replace 0 with O in word contexts
                text = re.sub(r'\b0\b', 'O', text)
            elif old == '1' and new == 'l':
                # Only replace 1 with l in word contexts
                text = re.sub(r'\b1\b', 'l', text)
            else:
                text = text.replace(old, new)
        
        # Fix common word errors
        word_fixes = {
            'teh': 'the',
            'adn': 'and',
            'thier': 'their',
            'recieve': 'receive',
            'seperate': 'separate',
            'occured': 'occurred',
            'begining': 'beginning',
        }
        
        for wrong, correct in word_fixes.items():
            text = re.sub(r'\b' + wrong + r'\b', correct, text, flags=re.IGNORECASE)
        
        return text
    
    def _extract_paragraphs(self, text: str) -> str:
        """
        Extract and structure paragraphs from text.
        
        Args:
            text (str): Input text
            
        Returns:
            str: Text with structured paragraphs
        """
        # Split into lines
        lines = text.split('\n')
        paragraphs = []
        current_paragraph = []
        
        for line in lines:
            line = line.strip()
            
            if line:
                # Add line to current paragraph
                current_paragraph.append(line)
            elif current_paragraph:
                # Empty line indicates paragraph break
                paragraphs.append(' '.join(current_paragraph))
                current_paragraph = []
        
        # Add the last paragraph if it exists
        if current_paragraph:
            paragraphs.append(' '.join(current_paragraph))
        
        return '\n\n'.join(paragraphs)
    
    def _convert_to_json(self, text: str) -> str:
        """
        Convert processed text to JSON format.
        
        Args:
            text (str): Input text
            
        Returns:
            str: JSON-formatted text
        """
        import json
        
        # Split into paragraphs
        paragraphs = text.split('\n\n')
        
        # Create JSON structure
        json_data = {
            'text': text,
            'paragraphs': paragraphs,
            'word_count': len(text.split()),
            'paragraph_count': len(paragraphs),
            'character_count': len(text)
        }
        
        return json.dumps(json_data, indent=2)
    
    def _convert_to_csv(self, text: str) -> str:
        """
        Convert processed text to CSV format.
        
        Args:
            text (str): Input text
            
        Returns:
            str: CSV-formatted text
        """
        import csv
        from io import StringIO
        
        # Split into paragraphs
        paragraphs = text.split('\n\n')
        
        # Create CSV structure
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['paragraph_number', 'text', 'word_count'])
        
        # Write data
        for i, paragraph in enumerate(paragraphs, 1):
            word_count = len(paragraph.split())
            writer.writerow([i, paragraph, word_count])
        
        return output.getvalue()
    
    def _calculate_text_statistics(self, text: str) -> Dict[str, Any]:
        """
        Calculate various text statistics.
        
        Args:
            text (str): Input text
            
        Returns:
            Dict[str, Any]: Text statistics
        """
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        paragraphs = text.split('\n\n')
        non_empty_sentences = [s for s in sentences if s.strip()]
        return {
            'word_count': len(words),
            'sentence_count': len(non_empty_sentences),
            'paragraph_count': len([p for p in paragraphs if p.strip()]),
            'character_count': len(text),
            'average_word_length': sum(len(word) for word in words) / len(words) if words else 0,
            'average_sentence_length': len(words) / len(non_empty_sentences) if non_empty_sentences else 0
        }
    
    def clean_for_ocr(self, text: str, **kwargs) -> tuple[str, Dict[str, Any]]:
        """
        Apply OCR-specific text cleaning (for Tesseract/PaddleOCR).
        
        This method applies a specific set of cleaning techniques that are
        particularly beneficial for OCR-extracted text (e.g., from Tesseract or PaddleOCR).
        
        Args:
            text (str): Input text
            **kwargs: Additional options (same as process method)
            
        Returns:
            tuple[str, Dict[str, Any]]: (cleaned_text, metadata)
        """
        # Set default OCR-optimized parameters (for Tesseract/PaddleOCR)
        ocr_kwargs = {
            'remove_extra_whitespace': True,
            'fix_line_breaks': True,
            'remove_special_chars': False,  # Keep special chars for OCR engines
            'normalize_quotes': True,
            'fix_common_ocr_errors': True,
            'extract_paragraphs': True,
            'output_format': 'text'
        }
        
        # Update with user-provided parameters
        ocr_kwargs.update(kwargs)
        
        return self.process(text, **ocr_kwargs) 