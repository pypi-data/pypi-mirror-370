"""
Document benchmarking module.

Contains tools for performance evaluation:
- Speed and accuracy metrics
- Comparison across different parsers
- Performance reporting and visualization
"""

# Import the base benchmarker class
from .base_benchmarker import BaseBenchmarker

# Import specific benchmarker implementations
from .performance_benchmarker import PerformanceBenchmarker
from .accuracy_benchmarker import AccuracyBenchmarker
from .docvqa_benchmarker import DocVQABenchmarker

# Define what gets imported when someone does "from doccraft.benchmarking import *"
__all__ = [
    'BaseBenchmarker',
    'PerformanceBenchmarker',
    'AccuracyBenchmarker',
    'DocVQABenchmarker',
]

# Benchmarker registry for dynamic lookup
BENCHMARKER_REGISTRY = {
    'accuracy': AccuracyBenchmarker,
    'performance': PerformanceBenchmarker,
    'docvqa': DocVQABenchmarker,
}

def get_benchmarker(benchmarker_name: str, **kwargs):
    """
    Retrieve a benchmarker instance by name from the registry.
    Args:
        benchmarker_name (str): The key for the benchmarker (e.g., 'accuracy', 'performance', 'docvqa')
        **kwargs: Additional arguments to pass to the benchmarker constructor
    Returns:
        BaseBenchmarker: An instance of the requested benchmarker.
    Raises:
        ValueError: If the benchmarker name is not found in the registry.
    """
    benchmarker_cls = BENCHMARKER_REGISTRY.get(benchmarker_name.lower())
    if benchmarker_cls is None:
        raise ValueError(f"Benchmarker '{benchmarker_name}' not found. Available: {list(BENCHMARKER_REGISTRY.keys())}")
    return benchmarker_cls(**kwargs)

__all__.extend(['BENCHMARKER_REGISTRY', 'get_benchmarker']) 