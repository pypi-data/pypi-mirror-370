"""
Performance benchmarking module.

This module provides performance benchmarking tools for measuring
parser speed, accuracy, and resource usage.
"""

import time
import psutil
import os
from typing import Dict, Any, Union, List, Optional
from pathlib import Path
import logging
import json
from datetime import datetime

from .base_benchmarker import BaseBenchmarker


class PerformanceBenchmarker(BaseBenchmarker):
    """
    Performance benchmarking for document parsers.
    
    This benchmarker measures various performance metrics including
    speed, memory usage, and CPU utilization.
    
    Attributes:
        name (str): Benchmarker name ('Performance Benchmarker')
        version (str): Version information
        supported_metrics (list): Supported performance metrics
    """
    
    def __init__(self):
        """
        Initialize the performance benchmarker.
        
        Sets up the benchmarker with performance monitoring capabilities.
        """
        # Initialize the base benchmarker
        super().__init__(
            name="Performance Benchmarker",
            version="1.0.0",
            supported_metrics=['speed', 'memory', 'cpu', 'accuracy']
        )
        
        self.logger = logging.getLogger(__name__)
        self.results = []
    
    def benchmark(self, parser, file_path: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """
        Benchmark a parser's performance on a given file.
        
        Args:
            parser: Parser instance to benchmark
            file_path (Union[str, Path]): Path to the test file
            **kwargs: Benchmark options:
                - iterations (int): Number of iterations to run
                - warmup_runs (int): Number of warmup runs
                - measure_memory (bool): Whether to measure memory usage
                - measure_cpu (bool): Whether to measure CPU usage
                - timeout (float): Maximum time per run in seconds
                
        Returns:
            Dict[str, Any]: Benchmark results
        """
        file_path = Path(file_path)
        
        # Parse benchmark options
        iterations = kwargs.get('iterations', 3)
        warmup_runs = kwargs.get('warmup_runs', 1)
        measure_memory = kwargs.get('measure_memory', True)
        measure_cpu = kwargs.get('measure_cpu', True)
        timeout = kwargs.get('timeout', 300.0)  # 5 minutes default
        
        # Initialize results
        benchmark_results = {
            'parser_name': parser.name,
            'parser_version': parser.version,
            'file_path': str(file_path),
            'file_size': file_path.stat().st_size,
            'iterations': iterations,
            'warmup_runs': warmup_runs,
            'timestamp': datetime.now().isoformat(),
            'metrics': {},
            'iteration_results': []  # Separate list for iteration results
        }
        
        self.logger.info(f"Starting benchmark for {parser.name} on {file_path.name}")
        
        try:
            # Warmup runs
            if warmup_runs > 0:
                self.logger.info(f"Running {warmup_runs} warmup runs")
                for i in range(warmup_runs):
                    try:
                        parser.extract_text(file_path)
                    except Exception as e:
                        self.logger.warning(f"Warmup run {i+1} failed: {e}")
            
            # Actual benchmark runs
            execution_times = []
            memory_usage = []
            cpu_usage = []
            
            for i in range(iterations):
                self.logger.info(f"Running iteration {i+1}/{iterations}")
                
                # Start monitoring
                start_time = time.time()
                start_memory = self._get_memory_usage() if measure_memory else None
                start_cpu = self._get_cpu_usage() if measure_cpu else None
                
                # Run the parser
                try:
                    result = parser.extract_text(file_path)
                    extracted_text = result.get('text', '')
                    metadata = result.get('metadata', {})
                    success = True
                except Exception as e:
                    self.logger.error(f"Iteration {i+1} failed: {e}")
                    extracted_text = ""
                    metadata = {}
                    success = False
                
                # End monitoring
                end_time = time.time()
                end_memory = self._get_memory_usage() if measure_memory else None
                end_cpu = self._get_cpu_usage() if measure_cpu else None
                
                # Calculate metrics
                execution_time = end_time - start_time
                execution_times.append(execution_time)
                
                if measure_memory and start_memory and end_memory:
                    memory_delta = end_memory - start_memory
                    memory_usage.append(memory_delta)
                
                if measure_cpu and start_cpu and end_cpu:
                    cpu_delta = end_cpu - start_cpu
                    cpu_usage.append(cpu_delta)
                
                # Check timeout
                if execution_time > timeout:
                    self.logger.warning(f"Iteration {i+1} exceeded timeout ({timeout}s)")
                
                # Store iteration results
                iteration_result = {
                    'iteration': i + 1,
                    'success': success,
                    'execution_time': execution_time,
                    'extracted_text_length': len(extracted_text),
                    'metadata': metadata
                }
                
                if measure_memory and start_memory and end_memory:
                    iteration_result['memory_usage'] = memory_delta
                
                if measure_cpu and start_cpu and end_cpu:
                    iteration_result['cpu_usage'] = cpu_delta
                
                benchmark_results['iteration_results'].append(iteration_result)
            
            # Calculate aggregate metrics
            benchmark_results['metrics'] = self._calculate_aggregate_metrics(
                execution_times, memory_usage, cpu_usage
            )
            
            # Add file information
            benchmark_results['file_info'] = {
                'size_bytes': file_path.stat().st_size,
                'size_mb': file_path.stat().st_size / (1024 * 1024),
                'extension': file_path.suffix
            }
            
            self.logger.info(f"Benchmark completed for {parser.name}")
            
        except Exception as e:
            self.logger.error(f"Benchmark failed: {e}")
            benchmark_results['error'] = str(e)
        
        # Store results
        self.results.append(benchmark_results)
        
        return benchmark_results
    
    def _get_memory_usage(self) -> Optional[float]:
        """
        Get current memory usage in MB.
        
        Returns:
            Optional[float]: Memory usage in MB
        """
        try:
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            return memory_info.rss / (1024 * 1024)  # Convert to MB
        except Exception:
            return None
    
    def _get_cpu_usage(self) -> Optional[float]:
        """
        Get current CPU usage percentage.
        
        Returns:
            Optional[float]: CPU usage percentage
        """
        try:
            return psutil.cpu_percent(interval=0.1)
        except Exception:
            return None
    
    def _calculate_aggregate_metrics(self, execution_times: List[float], 
                                   memory_usage: List[float], 
                                   cpu_usage: List[float]) -> Dict[str, Any]:
        """
        Calculate aggregate metrics from individual measurements.
        
        Args:
            execution_times (List[float]): List of execution times
            memory_usage (List[float]): List of memory usage deltas
            cpu_usage (List[float]): List of CPU usage deltas
            
        Returns:
            Dict[str, Any]: Aggregate metrics
        """
        metrics = {}
        
        # Execution time metrics
        if execution_times:
            metrics['execution_time'] = {
                'mean': sum(execution_times) / len(execution_times),
                'min': min(execution_times),
                'max': max(execution_times),
                'std_dev': self._calculate_std_dev(execution_times),
                'total': sum(execution_times)
            }
        
        # Memory usage metrics
        if memory_usage:
            metrics['memory_usage'] = {
                'mean': sum(memory_usage) / len(memory_usage),
                'min': min(memory_usage),
                'max': max(memory_usage),
                'std_dev': self._calculate_std_dev(memory_usage),
                'total': sum(memory_usage)
            }
        
        # CPU usage metrics
        if cpu_usage:
            metrics['cpu_usage'] = {
                'mean': sum(cpu_usage) / len(cpu_usage),
                'min': min(cpu_usage),
                'max': max(cpu_usage),
                'std_dev': self._calculate_std_dev(cpu_usage),
                'total': sum(cpu_usage)
            }
        
        return metrics
    
    def _calculate_std_dev(self, values: List[float]) -> float:
        """
        Calculate standard deviation of a list of values.
        
        Args:
            values (List[float]): List of values
            
        Returns:
            float: Standard deviation
        """
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5
    
    def compare_parsers(self, parsers: List, file_path: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """
        Compare multiple parsers on the same file.
        
        Args:
            parsers (List): List of parser instances to compare
            file_path (Union[str, Path]): Path to the test file
            **kwargs: Benchmark options (same as benchmark method)
            
        Returns:
            Dict[str, Any]: Comparison results
        """
        comparison_results = {
            'file_path': str(file_path),
            'timestamp': datetime.now().isoformat(),
            'parsers': [],
            'comparison': {}
        }
        
        # Benchmark each parser
        for parser in parsers:
            parser_results = self.benchmark(parser, file_path, **kwargs)
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
            'fastest_parser': None,
            'slowest_parser': None,
            'most_memory_efficient': None,
            'least_memory_efficient': None,
            'speed_ranking': [],
            'memory_ranking': []
        }
        
        # Find fastest and slowest parsers
        valid_results = [r for r in parser_results if 'metrics' in r and 'execution_time' in r['metrics']]
        
        if valid_results:
            fastest = min(valid_results, key=lambda x: x['metrics']['execution_time']['mean'])
            slowest = max(valid_results, key=lambda x: x['metrics']['execution_time']['mean'])
            
            comparison['fastest_parser'] = {
                'name': fastest['parser_name'],
                'mean_time': fastest['metrics']['execution_time']['mean']
            }
            
            comparison['slowest_parser'] = {
                'name': slowest['parser_name'],
                'mean_time': slowest['metrics']['execution_time']['mean']
            }
            
            # Speed ranking
            speed_ranking = sorted(valid_results, key=lambda x: x['metrics']['execution_time']['mean'])
            comparison['speed_ranking'] = [
                {
                    'name': r['parser_name'],
                    'mean_time': r['metrics']['execution_time']['mean']
                }
                for r in speed_ranking
            ]
        
        # Find most and least memory efficient parsers
        memory_results = [r for r in parser_results if 'metrics' in r and 'memory_usage' in r['metrics']]
        
        if memory_results:
            most_efficient = min(memory_results, key=lambda x: x['metrics']['memory_usage']['mean'])
            least_efficient = max(memory_results, key=lambda x: x['metrics']['memory_usage']['mean'])
            
            comparison['most_memory_efficient'] = {
                'name': most_efficient['parser_name'],
                'mean_memory': most_efficient['metrics']['memory_usage']['mean']
            }
            
            comparison['least_memory_efficient'] = {
                'name': least_efficient['parser_name'],
                'mean_memory': least_efficient['metrics']['memory_usage']['mean']
            }
            
            # Memory ranking
            memory_ranking = sorted(memory_results, key=lambda x: x['metrics']['memory_usage']['mean'])
            comparison['memory_ranking'] = [
                {
                    'name': r['parser_name'],
                    'mean_memory': r['metrics']['memory_usage']['mean']
                }
                for r in memory_ranking
            ]
        
        return comparison
    
    def save_results(self, output_path: Union[str, Path]) -> Path:
        """
        Save benchmark results to a file.
        
        Args:
            output_path (Union[str, Path]): Output file path
            
        Returns:
            Path: Path to the saved file
        """
        output_path = Path(output_path)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save results as JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        self.logger.info(f"Results saved to {output_path}")
        
        return output_path
    
    def load_results(self, input_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Load benchmark results from a file.
        
        Args:
            input_path (Union[str, Path]): Input file path
            
        Returns:
            List[Dict[str, Any]]: Loaded results
        """
        input_path = Path(input_path)
        
        with open(input_path, 'r', encoding='utf-8') as f:
            self.results = json.load(f)
        
        self.logger.info(f"Results loaded from {input_path}")
        
        return self.results
    
    def generate_report(self, output_path: Union[str, Path]) -> Path:
        """
        Generate a human-readable benchmark report.
        
        Args:
            output_path (Union[str, Path]): Output file path
            
        Returns:
            Path: Path to the generated report
        """
        output_path = Path(output_path)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report_content = self._generate_report_content()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.logger.info(f"Report generated: {output_path}")
        
        return output_path
    
    def _generate_report_content(self) -> str:
        """
        Generate the content of the benchmark report.
        
        Returns:
            str: Report content
        """
        if not self.results:
            return "No benchmark results available."
        
        report_lines = [
            "# Document Parser Benchmark Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            f"Total benchmarks: {len(self.results)}",
            ""
        ]
        
        for i, result in enumerate(self.results, 1):
            report_lines.extend([
                f"## Benchmark {i}: {result.get('parser_name', 'Unknown Parser')}",
                f"File: {result.get('file_path', 'Unknown')}",
                f"Timestamp: {result.get('timestamp', 'Unknown')}",
                ""
            ])
            
            if 'metrics' in result:
                metrics = result['metrics']
                
                if 'execution_time' in metrics:
                    et = metrics['execution_time']
                    report_lines.extend([
                        "### Execution Time",
                        f"- Mean: {et['mean']:.3f} seconds",
                        f"- Min: {et['min']:.3f} seconds",
                        f"- Max: {et['max']:.3f} seconds",
                        f"- Std Dev: {et['std_dev']:.3f} seconds",
                        f"- Total: {et['total']:.3f} seconds",
                        ""
                    ])
                
                if 'memory_usage' in metrics:
                    mu = metrics['memory_usage']
                    report_lines.extend([
                        "### Memory Usage",
                        f"- Mean: {mu['mean']:.2f} MB",
                        f"- Min: {mu['min']:.2f} MB",
                        f"- Max: {mu['max']:.2f} MB",
                        f"- Std Dev: {mu['std_dev']:.2f} MB",
                        ""
                    ])
            
            report_lines.append("---")
            report_lines.append("")
        
        return '\n'.join(report_lines) 