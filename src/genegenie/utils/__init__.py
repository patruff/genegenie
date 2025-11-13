"""Utility modules for GeneGenie."""

from .longevity_db import LONGEVITY_PANEL, get_longevity_variants
from .performance import chunk_by_chromosome, parallel_process_chromosomes

__all__ = [
    'LONGEVITY_PANEL',
    'get_longevity_variants',
    'chunk_by_chromosome',
    'parallel_process_chromosomes',
]
