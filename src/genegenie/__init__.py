"""
GeneGenie - Whole Genome Sequencing Analysis Toolkit

A comprehensive Python toolkit for analyzing whole genome sequencing data
with focus on longevity, personality, cognition, behavior, and addiction genetics.
"""

__version__ = "0.2.0"
__author__ = "GeneGenie Contributors"
__license__ = "MIT"

from .longevity_analyzer import WGSLongevityAnalyzer
from .trait_analyzer import TraitAnalyzer

__all__ = ['WGSLongevityAnalyzer', 'TraitAnalyzer']
