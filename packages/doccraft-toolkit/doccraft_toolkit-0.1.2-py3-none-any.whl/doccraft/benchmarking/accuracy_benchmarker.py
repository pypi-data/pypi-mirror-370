"""
Accuracy benchmarking module.

This module provides accuracy benchmarking tools for measuring
parser accuracy against ground truth data.
"""

import difflib
import re
from typing import Dict, Any, Union, List, Optional
from pathlib import Path
import logging
import json
from datetime import datetime

from .base_benchmarker import BaseBenchmarker


class AccuracyBenchmarker(BaseBenchmarker):
    """
    Accuracy benchmarking for document parsers.
    
    This benchmarker measures parser accuracy by comparing extracted
    text against ground truth data using various metrics.
    
    Attributes:
        name (str): Benchmarker name ('Accuracy Benchmarker')
        version (str): Version information
        supported_metrics (list): Supported accuracy metrics
    """
    
    def __init__(self):
        """
        Initialize the accuracy benchmarker.
        
        Sets up the benchmarker with accuracy measurement capabilities.
        """
        # Initialize the base benchmarker
        super().__init__(
            name="Accuracy Benchmarker",
            version="1.0.0",
            supported_metrics=['character_accuracy', 'word_accuracy', 'line_accuracy', 'semantic_similarity']
        )
        
        self.logger = logging.getLogger(__name__)
        self.results = []
    
    def benchmark(self, parser, file_path: Union[str, Path], ground_truth: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """
        Benchmark a parser's accuracy against ground truth data.
        
        Args:
            parser: Parser instance to benchmark
            file_path (Union[str, Path]): Path to the test file
            ground_truth (Union[str, Path]): Path to ground truth file or ground truth text
            **kwargs: Benchmark options:
                - normalize_text (bool): Whether to normalize text before comparison
                - ignore_case (bool): Whether to ignore case in comparison
                - ignore_whitespace (bool): Whether to ignore whitespace differences
                - calculate_semantic_similarity (bool): Whether to calculate semantic similarity
                
        Returns:
            Dict[str, Any]: Benchmark results
        """
        file_path = Path(file_path)
        
        # Parse benchmark options
        normalize_text = kwargs.get('normalize_text', True)
        ignore_case = kwargs.get('ignore_case', True)
        ignore_whitespace = kwargs.get('ignore_whitespace', True)
        calculate_semantic_similarity = kwargs.get('calculate_semantic_similarity', False)
        
        # Initialize results
        benchmark_results = {
            'parser_name': parser.name,
            'parser_version': parser.version,
            'file_path': str(file_path),
            'ground_truth_path': str(ground_truth) if isinstance(ground_truth, (str, Path)) else 'inline',
            'timestamp': datetime.now().isoformat(),
            'metrics': {}
        }
        
        self.logger.info(f"Starting accuracy benchmark for {parser.name} on {file_path.name}")
        
        try:
            # Extract text using the parser
            result = parser.extract_text(file_path)
            extracted_text = result.get('text', '')
            metadata = result.get('metadata', {})
            
            # Load or use ground truth
            if isinstance(ground_truth, (str, Path)):
                ground_truth_path = Path(ground_truth)
                # Check if it's actually a file path
                if ground_truth_path.exists() and ground_truth_path.is_file():
                    with open(ground_truth_path, 'r', encoding='utf-8') as f:
                        ground_truth_text = f.read()
                else:
                    # Treat as inline text
                    ground_truth_text = str(ground_truth)
            else:
                ground_truth_text = str(ground_truth)
            
            # Normalize texts if requested
            if normalize_text:
                extracted_text = self._normalize_text(extracted_text)
                ground_truth_text = self._normalize_text(ground_truth_text)
            
            # Calculate accuracy metrics
            accuracy_metrics = self._calculate_accuracy_metrics(
                extracted_text, ground_truth_text, ignore_case, ignore_whitespace
            )
            
            # Calculate semantic similarity if requested
            if calculate_semantic_similarity:
                semantic_similarity = self._calculate_semantic_similarity(
                    extracted_text, ground_truth_text
                )
                accuracy_metrics['semantic_similarity'] = semantic_similarity
            
            # Store results
            benchmark_results['metrics'] = accuracy_metrics
            benchmark_results['extracted_text_length'] = len(extracted_text)
            benchmark_results['ground_truth_length'] = len(ground_truth_text)
            benchmark_results['metadata'] = metadata
            
            self.logger.info(f"Accuracy benchmark completed for {parser.name}")
            
        except Exception as e:
            self.logger.error(f"Accuracy benchmark failed: {e}")
            benchmark_results['error'] = str(e)
        
        # Store results
        self.results.append(benchmark_results)
        
        return benchmark_results
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for comparison.
        
        Args:
            text (str): Input text
            
        Returns:
            str: Normalized text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        return text
    
    def _calculate_accuracy_metrics(self, extracted_text: str, ground_truth_text: str,
                                  ignore_case: bool = True, ignore_whitespace: bool = True) -> Dict[str, Any]:
        """
        Calculate various accuracy metrics.
        
        Args:
            extracted_text (str): Text extracted by the parser
            ground_truth_text (str): Ground truth text
            ignore_case (bool): Whether to ignore case
            ignore_whitespace (bool): Whether to ignore whitespace
            
        Returns:
            Dict[str, Any]: Accuracy metrics
        """
        metrics = {}
        
        # Prepare texts for comparison
        extracted = extracted_text
        ground_truth = ground_truth_text
        
        if ignore_case:
            extracted = extracted.lower()
            ground_truth = ground_truth.lower()
        
        if ignore_whitespace:
            extracted = re.sub(r'\s+', '', extracted)
            ground_truth = re.sub(r'\s+', '', ground_truth)
        
        # Character-level accuracy
        metrics['character_accuracy'] = self._calculate_character_accuracy(extracted, ground_truth)
        
        # Word-level accuracy
        metrics['word_accuracy'] = self._calculate_word_accuracy(extracted_text, ground_truth_text, ignore_case)
        
        # Line-level accuracy
        metrics['line_accuracy'] = self._calculate_line_accuracy(extracted_text, ground_truth_text, ignore_case)
        
        # Edit distance
        metrics['edit_distance'] = self._calculate_edit_distance(extracted, ground_truth)
        
        # Similarity ratio
        metrics['similarity_ratio'] = difflib.SequenceMatcher(None, extracted, ground_truth).ratio()
        
        return metrics
    
    def _calculate_character_accuracy(self, extracted: str, ground_truth: str) -> float:
        """
        Calculate character-level accuracy.
        
        Args:
            extracted (str): Extracted text
            ground_truth (str): Ground truth text
            
        Returns:
            float: Character accuracy (0.0 to 1.0)
        """
        if not ground_truth:
            return 0.0 if extracted else 1.0
        
        # Use difflib for character-level comparison
        matcher = difflib.SequenceMatcher(None, ground_truth, extracted)
        
        # Count matching characters using a different approach
        matches = 0
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                matches += (i2 - i1)  # Length of matching segment
        
        return matches / len(ground_truth)
    
    def _calculate_word_accuracy(self, extracted_text: str, ground_truth_text: str, ignore_case: bool = True) -> float:
        """
        Calculate word-level accuracy.
        
        Args:
            extracted_text (str): Extracted text
            ground_truth_text (str): Ground truth text
            ignore_case (bool): Whether to ignore case
            
        Returns:
            float: Word accuracy (0.0 to 1.0)
        """
        # Split into words
        extracted_words = extracted_text.split()
        ground_truth_words = ground_truth_text.split()
        
        if ignore_case:
            extracted_words = [word.lower() for word in extracted_words]
            ground_truth_words = [word.lower() for word in ground_truth_words]
        
        if not ground_truth_words:
            return 0.0 if extracted_words else 1.0
        
        # Count matching words
        matches = 0
        for word in extracted_words:
            if word in ground_truth_words:
                matches += 1
        
        return matches / len(ground_truth_words)
    
    def _calculate_line_accuracy(self, extracted_text: str, ground_truth_text: str, ignore_case: bool = True) -> float:
        """
        Calculate line-level accuracy.
        
        Args:
            extracted_text (str): Extracted text
            ground_truth_text (str): Ground truth text
            ignore_case (bool): Whether to ignore case
            
        Returns:
            float: Line accuracy (0.0 to 1.0)
        """
        # Split into lines
        extracted_lines = [line.strip() for line in extracted_text.split('\n') if line.strip()]
        ground_truth_lines = [line.strip() for line in ground_truth_text.split('\n') if line.strip()]
        
        if ignore_case:
            extracted_lines = [line.lower() for line in extracted_lines]
            ground_truth_lines = [line.lower() for line in ground_truth_lines]
        
        if not ground_truth_lines:
            return 0.0 if extracted_lines else 1.0
        
        # Count matching lines
        matches = 0
        for line in extracted_lines:
            if line in ground_truth_lines:
                matches += 1
        
        return matches / len(ground_truth_lines)
    
    def _calculate_edit_distance(self, extracted: str, ground_truth: str) -> int:
        """
        Calculate Levenshtein edit distance.
        
        Args:
            extracted (str): Extracted text
            ground_truth (str): Ground truth text
            
        Returns:
            int: Edit distance
        """
        # Simple implementation of Levenshtein distance
        m, n = len(ground_truth), len(extracted)
        
        # Create matrix
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        # Initialize first row and column
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        
        # Fill the matrix
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if ground_truth[i - 1] == extracted[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]) + 1
        
        return dp[m][n]
    
    def _calculate_semantic_similarity(self, extracted_text: str, ground_truth_text: str) -> float:
        """
        Calculate semantic similarity using basic techniques.
        
        Args:
            extracted_text (str): Extracted text
            ground_truth_text (str): Ground truth text
            
        Returns:
            float: Semantic similarity (0.0 to 1.0)
        """
        # Simple semantic similarity using word overlap
        extracted_words = set(re.findall(r'\b\w+\b', extracted_text.lower()))
        ground_truth_words = set(re.findall(r'\b\w+\b', ground_truth_text.lower()))
        
        if not ground_truth_words:
            return 0.0 if extracted_words else 1.0
        
        # Calculate Jaccard similarity
        intersection = len(extracted_words.intersection(ground_truth_words))
        union = len(extracted_words.union(ground_truth_words))
        
        return intersection / union if union > 0 else 0.0
    
    def compare_parsers(self, parsers: List, file_path: Union[str, Path], 
                       ground_truth: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """
        Compare multiple parsers' accuracy on the same file.
        
        Args:
            parsers (List): List of parser instances to compare
            file_path (Union[str, Path]): Path to the test file
            ground_truth (Union[str, Path]): Path to ground truth file or ground truth text
            **kwargs: Benchmark options (same as benchmark method)
            
        Returns:
            Dict[str, Any]: Comparison results
        """
        comparison_results = {
            'file_path': str(file_path),
            'ground_truth_path': str(ground_truth) if isinstance(ground_truth, (str, Path)) else 'inline',
            'timestamp': datetime.now().isoformat(),
            'parsers': [],
            'comparison': {}
        }
        
        # Benchmark each parser
        for parser in parsers:
            parser_results = self.benchmark(parser, file_path, ground_truth, **kwargs)
            comparison_results['parsers'].append(parser_results)
        
        # Calculate comparison metrics
        comparison_results['comparison'] = self._calculate_comparison_metrics(
            comparison_results['parsers']
        )
        
        return comparison_results
    
    def _calculate_comparison_metrics(self, parser_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate comparison metrics between parsers.
        
        Args:
            parser_results (List[Dict[str, Any]]): Results from multiple parsers
            
        Returns:
            Dict[str, Any]: Comparison metrics
        """
        comparison = {
            'most_accurate_parser': None,
            'least_accurate_parser': None,
            'accuracy_ranking': [],
            'character_accuracy_ranking': [],
            'word_accuracy_ranking': []
        }
        
        # Find most and least accurate parsers
        valid_results = [r for r in parser_results if 'metrics' in r and 'similarity_ratio' in r['metrics']]
        
        if valid_results:
            most_accurate = max(valid_results, key=lambda x: x['metrics']['similarity_ratio'])
            least_accurate = min(valid_results, key=lambda x: x['metrics']['similarity_ratio'])
            
            comparison['most_accurate_parser'] = {
                'name': most_accurate['parser_name'],
                'similarity_ratio': most_accurate['metrics']['similarity_ratio']
            }
            
            comparison['least_accurate_parser'] = {
                'name': least_accurate['parser_name'],
                'similarity_ratio': least_accurate['metrics']['similarity_ratio']
            }
            
            # Overall accuracy ranking
            accuracy_ranking = sorted(valid_results, key=lambda x: x['metrics']['similarity_ratio'], reverse=True)
            comparison['accuracy_ranking'] = [
                {
                    'name': r['parser_name'],
                    'similarity_ratio': r['metrics']['similarity_ratio']
                }
                for r in accuracy_ranking
            ]
            
            # Character accuracy ranking
            char_accuracy_ranking = sorted(valid_results, key=lambda x: x['metrics']['character_accuracy'], reverse=True)
            comparison['character_accuracy_ranking'] = [
                {
                    'name': r['parser_name'],
                    'character_accuracy': r['metrics']['character_accuracy']
                }
                for r in char_accuracy_ranking
            ]
            
            # Word accuracy ranking
            word_accuracy_ranking = sorted(valid_results, key=lambda x: x['metrics']['word_accuracy'], reverse=True)
            comparison['word_accuracy_ranking'] = [
                {
                    'name': r['parser_name'],
                    'word_accuracy': r['metrics']['word_accuracy']
                }
                for r in word_accuracy_ranking
            ]
        
        return comparison
    
    def generate_detailed_report(self, output_path: Union[str, Path]) -> Path:
        """
        Generate a detailed accuracy report with differences.
        
        Args:
            output_path (Union[str, Path]): Output file path
            
        Returns:
            Path: Path to the generated report
        """
        output_path = Path(output_path)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report_content = self._generate_detailed_report_content()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.logger.info(f"Detailed report generated: {output_path}")
        
        return output_path
    
    def _generate_detailed_report_content(self) -> str:
        """
        Generate the content of the detailed accuracy report.
        
        Returns:
            str: Report content
        """
        if not self.results:
            return "No accuracy benchmark results available."
        
        report_lines = [
            "# Document Parser Accuracy Benchmark Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            f"Total benchmarks: {len(self.results)}",
            ""
        ]
        
        for i, result in enumerate(self.results, 1):
            report_lines.extend([
                f"## Accuracy Benchmark {i}: {result.get('parser_name', 'Unknown Parser')}",
                f"File: {result.get('file_path', 'Unknown')}",
                f"Ground Truth: {result.get('ground_truth_path', 'Unknown')}",
                f"Timestamp: {result.get('timestamp', 'Unknown')}",
                ""
            ])
            
            if 'metrics' in result:
                metrics = result['metrics']
                
                report_lines.extend([
                    "### Accuracy Metrics",
                    f"- Character Accuracy: {metrics.get('character_accuracy', 0):.3f}",
                    f"- Word Accuracy: {metrics.get('word_accuracy', 0):.3f}",
                    f"- Line Accuracy: {metrics.get('line_accuracy', 0):.3f}",
                    f"- Similarity Ratio: {metrics.get('similarity_ratio', 0):.3f}",
                    f"- Edit Distance: {metrics.get('edit_distance', 0)}",
                    ""
                ])
                
                if 'semantic_similarity' in metrics:
                    report_lines.append(f"- Semantic Similarity: {metrics['semantic_similarity']:.3f}")
                    report_lines.append("")
            
            report_lines.append("---")
            report_lines.append("")
        
        return '\n'.join(report_lines) 