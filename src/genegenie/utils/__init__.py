"""Utility modules for GeneGenie."""

from .longevity_db import LONGEVITY_PANEL, get_longevity_variants
from .trait_db import (
    ALL_TRAIT_SNPS,
    get_snps_by_category,
    get_snps_by_trait,
    get_all_categories,
    get_snp_info
)
from .performance import chunk_by_chromosome, parallel_process_chromosomes

__all__ = [
    'LONGEVITY_PANEL',
    'get_longevity_variants',
    'ALL_TRAIT_SNPS',
    'get_snps_by_category',
    'get_snps_by_trait',
    'get_all_categories',
    'get_snp_info',
    'chunk_by_chromosome',
    'parallel_process_chromosomes',
]
