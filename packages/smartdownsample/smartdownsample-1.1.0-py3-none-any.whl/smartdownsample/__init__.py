"""
SmartDownsample: Intelligent image downsampling for camera traps and large datasets.

Smart downsampling library that selects the most diverse images from large datasets,
perfect for camera trap data and machine learning workflows.
"""

from .core import sample_diverse, sample_diverse_with_stats
from .viz import (
    plot_bucket_distribution,
    plot_hash_similarity_scatter, 
    print_bucket_summary
)

__version__ = "1.1.0"
__author__ = "Smart Image Downsampler"
__email__ = "your.email@example.com"

__all__ = [
    "sample_diverse", 
    "sample_diverse_with_stats",
    "plot_bucket_distribution",
    "plot_hash_similarity_scatter", 
    "print_bucket_summary"
]