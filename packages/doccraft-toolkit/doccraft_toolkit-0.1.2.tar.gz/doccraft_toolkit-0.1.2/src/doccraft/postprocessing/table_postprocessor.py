"""
Table postprocessing module.

This module provides table postprocessing tools for extracting,
cleaning, and formatting table data from documents.
"""

import re
from typing import Dict, Any, Union, List, Optional
from pathlib import Path
import logging

from .base_postprocessor import BasePostprocessor


class TablePostprocessor(BasePostprocessor):
    """
    Table postprocessing for data extraction and formatting.
    
    This postprocessor handles table data extraction, cleaning,
    and conversion to various formats.
    
    Attributes:
        name (str): Postprocessor name ('Table Postprocessor')
        version (str): Version information
        supported_formats (list): Supported output formats
    """
    
    def __init__(self):
        """
        Initialize the table postprocessor.
        
        Sets up the postprocessor with table processing capabilities.
        """
        # Initialize the base postprocessor
        super().__init__(
            name="Table Postprocessor",
            version="1.0.0",
            supported_formats=['.csv', '.json', '.xlsx', '.html']
        )
        
        self.logger = logging.getLogger(__name__)
    
    def process(self, table_data: Union[List[List[str]], Dict[str, Any]], **kwargs) -> tuple[Union[str, Path], Dict[str, Any]]:
        """
        Process table data with various cleaning and formatting techniques.
        
        Args:
            table_data (Union[List[List[str]], Dict[str, Any]]): Input table data
            **kwargs: Processing options:
                - clean_cells (bool): Clean individual cell data
                - remove_empty_rows (bool): Remove rows with no data
                - remove_empty_columns (bool): Remove columns with no data
                - normalize_headers (bool): Normalize column headers
                - output_format (str): Output format ('csv', 'json', 'xlsx', 'html')
                - output_path (str): Output file path
                
        Returns:
            tuple[Union[str, Path], Dict[str, Any]]: (output_path, metadata)
        """
        # Parse processing options
        clean_cells = kwargs.get('clean_cells', True)
        remove_empty_rows = kwargs.get('remove_empty_rows', True)
        remove_empty_columns = kwargs.get('remove_empty_columns', True)
        normalize_headers = kwargs.get('normalize_headers', True)
        output_format = kwargs.get('output_format', 'csv')
        output_path = kwargs.get('output_path', None)
        
        metadata = {
            'original_rows': 0,
            'original_columns': 0,
            'processing_steps': [],
            'output_format': output_format,
            'table_statistics': {}
        }
        
        # Convert input to standard format
        if isinstance(table_data, dict):
            # Handle dictionary format (from parsers)
            table_matrix = self._dict_to_matrix(table_data)
        else:
            # Handle list format
            table_matrix = table_data
        
        # Store original dimensions
        metadata['original_rows'] = len(table_matrix)
        metadata['original_columns'] = len(table_matrix[0]) if table_matrix else 0
        
        processed_table = table_matrix
        
        # Apply processing steps
        if clean_cells:
            processed_table = self._clean_cells(processed_table)
            metadata['processing_steps'].append('clean_cells')
        
        if remove_empty_rows:
            processed_table = self._remove_empty_rows(processed_table)
            metadata['processing_steps'].append('remove_empty_rows')
        
        if remove_empty_columns:
            processed_table = self._remove_empty_columns(processed_table)
            metadata['processing_steps'].append('remove_empty_columns')
        
        if normalize_headers:
            processed_table = self._normalize_headers(processed_table)
            metadata['processing_steps'].append('normalize_headers')
        
        # Set default output path if not provided
        if output_path is None:
            output_path = f"processed_table.{output_format}"
        else:
            output_path = Path(output_path)
        
        # Convert to desired output format
        if output_format == 'csv':
            output_path = self._convert_to_csv(processed_table, output_path)
        elif output_format == 'json':
            output_path = self._convert_to_json(processed_table, output_path)
        elif output_format == 'xlsx':
            output_path = self._convert_to_xlsx(processed_table, output_path)
        elif output_format == 'html':
            output_path = self._convert_to_html(processed_table, output_path)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
        
        # Update metadata
        metadata['final_rows'] = len(processed_table)
        metadata['final_columns'] = len(processed_table[0]) if processed_table else 0
        metadata['output_path'] = str(output_path)
        metadata['table_statistics'] = self._calculate_table_statistics(processed_table)
        
        self.logger.info(f"Table processing completed. Applied {len(metadata['processing_steps'])} steps")
        
        return output_path, metadata
    
    def _dict_to_matrix(self, table_dict: Dict[str, Any]) -> List[List[str]]:
        """
        Convert dictionary table format to matrix format.
        
        Args:
            table_dict (Dict[str, Any]): Table data in dictionary format
            
        Returns:
            List[List[str]]: Table data in matrix format
        """
        if 'data' in table_dict:
            return table_dict['data']
        elif 'rows' in table_dict:
            return table_dict['rows']
        else:
            # Try to extract table data from various formats
            for key in ['table', 'content', 'cells']:
                if key in table_dict:
                    return table_dict[key]
        
        # If no recognizable format, return empty table
        return []
    
    def _clean_cells(self, table: List[List[str]]) -> List[List[str]]:
        """
        Clean individual cell data.
        
        Args:
            table (List[List[str]]): Input table
            
        Returns:
            List[List[str]]: Table with cleaned cells
        """
        cleaned_table = []
        
        for row in table:
            cleaned_row = []
            for cell in row:
                if cell is None:
                    cleaned_cell = ""
                else:
                    # Convert to string and clean
                    cleaned_cell = str(cell).strip()
                    
                    # Remove excessive whitespace
                    cleaned_cell = re.sub(r'\s+', ' ', cleaned_cell)
                    
                    # Normalize quotes
                    cleaned_cell = cleaned_cell.replace('"', '"').replace('"', '"')
                    cleaned_cell = cleaned_cell.replace(''', "'").replace(''', "'")
                
                cleaned_row.append(cleaned_cell)
            cleaned_table.append(cleaned_row)
        
        return cleaned_table
    
    def _remove_empty_rows(self, table: List[List[str]]) -> List[List[str]]:
        """
        Remove rows that contain no meaningful data.
        
        Args:
            table (List[List[str]]): Input table
            
        Returns:
            List[List[str]]: Table with empty rows removed
        """
        cleaned_table = []
        
        for row in table:
            # Check if row has any non-empty cells
            has_data = any(cell.strip() for cell in row if cell)
            if has_data:
                cleaned_table.append(row)
        
        return cleaned_table
    
    def _remove_empty_columns(self, table: List[List[str]]) -> List[List[str]]:
        """
        Remove columns that contain no meaningful data.
        
        Args:
            table (List[List[str]]): Input table
            
        Returns:
            List[List[str]]: Table with empty columns removed
        """
        if not table:
            return table
        
        # Find columns with data
        num_columns = len(table[0])
        column_has_data = [False] * num_columns
        
        for row in table:
            for i, cell in enumerate(row):
                if i < len(column_has_data) and cell and cell.strip():
                    column_has_data[i] = True
        
        # Keep only columns with data
        cleaned_table = []
        for row in table:
            cleaned_row = [cell for i, cell in enumerate(row) if column_has_data[i]]
            cleaned_table.append(cleaned_row)
        
        return cleaned_table
    
    def _normalize_headers(self, table: List[List[str]]) -> List[List[str]]:
        """
        Normalize column headers for consistency.
        
        Args:
            table (List[List[str]]): Input table
            
        Returns:
            List[List[str]]: Table with normalized headers
        """
        if not table:
            return table
        
        # Process the first row as headers
        headers = table[0]
        normalized_headers = []
        
        for header in headers:
            if header is None:
                normalized_header = "Column"
            else:
                # Convert to string and clean
                normalized_header = str(header).strip()
                
                # Convert to lowercase and replace spaces with underscores
                normalized_header = re.sub(r'\s+', '_', normalized_header.lower())
                
                # Remove special characters
                normalized_header = re.sub(r'[^\w_]', '', normalized_header)
                
                # Ensure it's not empty
                if not normalized_header:
                    normalized_header = "column"
            
            normalized_headers.append(normalized_header)
        
        # Create new table with normalized headers
        normalized_table = [normalized_headers] + table[1:]
        
        return normalized_table
    
    def _convert_to_csv(self, table: List[List[str]], output_path: Union[str, Path]) -> Path:
        """
        Convert table to CSV format.
        
        Args:
            table (List[List[str]]): Input table
            output_path (Union[str, Path]): Output file path
            
        Returns:
            Path: Path to the created CSV file
        """
        import csv
        
        output_path = Path(output_path)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(table)
        
        return output_path
    
    def _convert_to_json(self, table: List[List[str]], output_path: Union[str, Path]) -> Path:
        """
        Convert table to JSON format.
        
        Args:
            table (List[List[str]]): Input table
            output_path (Union[str, Path]): Output file path
            
        Returns:
            Path: Path to the created JSON file
        """
        import json
        
        output_path = Path(output_path)
        
        if not table:
            json_data = {"table": [], "rows": 0, "columns": 0}
        else:
            # Convert to list of dictionaries
            headers = table[0]
            rows = []
            
            for row in table[1:]:
                row_dict = {}
                for i, cell in enumerate(row):
                    if i < len(headers):
                        row_dict[headers[i]] = cell
                    else:
                        row_dict[f"column_{i}"] = cell
                rows.append(row_dict)
            
            json_data = {
                "headers": headers,
                "rows": rows,
                "row_count": len(rows),
                "column_count": len(headers)
            }
        
        with open(output_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(json_data, jsonfile, indent=2)
        
        return output_path
    
    def _convert_to_xlsx(self, table: List[List[str]], output_path: Union[str, Path]) -> Path:
        """
        Convert table to Excel format.
        
        Args:
            table (List[List[str]]): Input table
            output_path (Union[str, Path]): Output file path
            
        Returns:
            Path: Path to the created Excel file
        """
        try:
            import pandas as pd
            
            output_path = Path(output_path)
            
            if not table:
                # Create empty DataFrame
                df = pd.DataFrame()
            else:
                # Create DataFrame from table
                headers = table[0]
                data = table[1:]
                df = pd.DataFrame(data, columns=headers)
            
            # Save to Excel
            df.to_excel(output_path, index=False)
            
        except ImportError:
            raise ImportError(
                "pandas is required for Excel export. Install with: pip install pandas openpyxl"
            )
        
        return output_path
    
    def _convert_to_html(self, table: List[List[str]], output_path: Union[str, Path]) -> Path:
        """
        Convert table to HTML format.
        
        Args:
            table (List[List[str]]): Input table
            output_path (Union[str, Path]): Output file path
            
        Returns:
            Path: Path to the created HTML file
        """
        output_path = Path(output_path)
        
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Extracted Table</title>
    <style>
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        tr:nth-child(even) { background-color: #f9f9f9; }
    </style>
</head>
<body>
    <h2>Extracted Table</h2>
    <table>
"""
        
        if table:
            # Add headers
            html_content += "        <thead>\n            <tr>\n"
            for cell in table[0]:
                html_content += f"                <th>{cell}</th>\n"
            html_content += "            </tr>\n        </thead>\n"
            
            # Add data rows
            html_content += "        <tbody>\n"
            for row in table[1:]:
                html_content += "            <tr>\n"
                for cell in row:
                    html_content += f"                <td>{cell}</td>\n"
                html_content += "            </tr>\n"
            html_content += "        </tbody>\n"
        
        html_content += """
    </table>
</body>
</html>
"""
        
        with open(output_path, 'w', encoding='utf-8') as htmlfile:
            htmlfile.write(html_content)
        
        return output_path
    
    def _calculate_table_statistics(self, table: List[List[str]]) -> Dict[str, Any]:
        """
        Calculate various table statistics.
        
        Args:
            table (List[List[str]]): Input table
            
        Returns:
            Dict[str, Any]: Table statistics
        """
        if not table:
            return {
                'row_count': 0,
                'column_count': 0,
                'total_cells': 0,
                'empty_cells': 0,
                'non_empty_cells': 0
            }
        
        row_count = len(table)
        column_count = len(table[0]) if table else 0
        total_cells = row_count * column_count
        empty_cells = 0
        non_empty_cells = 0
        
        for row in table:
            for cell in row:
                if cell and cell.strip():
                    non_empty_cells += 1
                else:
                    empty_cells += 1
        
        return {
            'row_count': row_count,
            'column_count': column_count,
            'total_cells': total_cells,
            'empty_cells': empty_cells,
            'non_empty_cells': non_empty_cells,
            'fill_rate': (non_empty_cells / total_cells * 100) if total_cells > 0 else 0
        }
    
    def extract_from_text(self, text: str, **kwargs) -> tuple[Union[str, Path], Dict[str, Any]]:
        """
        Extract table data from text and process it.
        
        This method attempts to identify and extract table-like structures
        from text and then processes them.
        
        Args:
            text (str): Input text containing table data
            **kwargs: Additional options (same as process method)
            
        Returns:
            tuple[Union[str, Path], Dict[str, Any]]: (output_path, metadata)
        """
        # Simple table extraction from text
        lines = text.split('\n')
        table_data = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Split by common table separators
                if '\t' in line:
                    row = line.split('\t')
                elif '|' in line:
                    row = [cell.strip() for cell in line.split('|')]
                else:
                    # Try to split by multiple spaces
                    row = re.split(r'\s{2,}', line)
                
                if row:
                    table_data.append(row)
        
        # Process the extracted table
        return self.process(table_data, **kwargs) 