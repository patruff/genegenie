"""
Visualization module for GeneGenie.

Provides interactive HTML visualizations for genetic trait analysis.
"""

from .trait_visualizer import (
    generate_html_report,
    create_visualization_from_analyzer,
    create_scale_svg,
    generate_trait_card_html,
    CATEGORY_INFO
)

__all__ = [
    'generate_html_report',
    'create_visualization_from_analyzer',
    'create_scale_svg',
    'generate_trait_card_html',
    'CATEGORY_INFO'
]
