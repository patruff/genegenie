#!/usr/bin/env python3
"""
Trait Visualization Module

Generates interactive HTML visualizations of genetic trait analysis results.
Creates a grid of trait cards showing genetic predisposition scores.
"""

from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
import json


# Category icons and metadata
CATEGORY_INFO = {
    'cognition': {
        'emoji': '🧠',
        'color': '#6366f1',  # Indigo
        'light_color': '#e0e7ff',
        'traits': ['Intelligence', 'Memory', 'Processing speed']
    },
    'personality': {
        'emoji': '🎭',
        'color': '#8b5cf6',  # Purple
        'light_color': '#ede9fe',
        'traits': ['Neuroticism', 'Extraversion', 'Openness', 'Conscientiousness', 'Agreeableness']
    },
    'addiction': {
        'emoji': '🚬',
        'color': '#ef4444',  # Red
        'light_color': '#fee2e2',
        'traits': ['Alcohol dependence', 'Nicotine dependence', 'Cannabis use', 'Caffeine metabolism']
    },
    'behavior': {
        'emoji': '⚡',
        'color': '#f59e0b',  # Amber
        'light_color': '#fef3c7',
        'traits': ['Risk-taking', 'Sleep duration', 'Chronotype', 'Aggression']
    },
    'mental_health': {
        'emoji': '💭',
        'color': '#10b981',  # Emerald
        'light_color': '#d1fae5',
        'traits': ['Depression', 'Anxiety', 'ADHD', 'Bipolar', 'Schizophrenia']
    },
    'physical': {
        'emoji': '💪',
        'color': '#06b6d4',  # Cyan
        'light_color': '#cffafe',
        'traits': ['Athletic performance', 'Muscle strength', 'Pain sensitivity']
    },
    'sensory': {
        'emoji': '👃',
        'color': '#ec4899',  # Pink
        'light_color': '#fce7f3',
        'traits': ['Bitter taste', 'Cilantro aversion', 'Smell sensitivity', 'Perfect pitch']
    }
}


def create_scale_svg(score: float, width: int = 300, height: int = 40) -> str:
    """
    Create an SVG scale indicator showing genetic score.

    Args:
        score: Genetic score (0-100, 50 = average)
        width: SVG width in pixels
        height: SVG height in pixels

    Returns:
        SVG markup string
    """
    # Calculate position (0-100 scale)
    position = (score / 100) * width

    # Determine color based on score
    if score >= 60:
        marker_color = '#10b981'  # Green
    elif score >= 55:
        marker_color = '#3b82f6'  # Blue
    elif score >= 45:
        marker_color = '#6b7280'  # Gray
    elif score >= 40:
        marker_color = '#f59e0b'  # Orange
    else:
        marker_color = '#ef4444'  # Red

    svg = f'''
    <svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
        <!-- Background track -->
        <rect x="0" y="{height//2 - 3}" width="{width}" height="6" fill="#e5e7eb" rx="3"/>

        <!-- Center line (average) -->
        <line x1="{width//2}" y1="{height//2 - 8}" x2="{width//2}" y2="{height//2 + 8}"
              stroke="#9ca3af" stroke-width="2" stroke-dasharray="4,2"/>

        <!-- Tick marks -->
        <line x1="0" y1="{height//2 + 10}" x2="0" y2="{height//2 + 15}"
              stroke="#9ca3af" stroke-width="1.5"/>
        <line x1="{width}" y1="{height//2 + 10}" x2="{width}" y2="{height//2 + 15}"
              stroke="#9ca3af" stroke-width="1.5"/>

        <!-- Score marker -->
        <circle cx="{position}" cy="{height//2}" r="8" fill="{marker_color}"
                stroke="white" stroke-width="2"/>

        <!-- Labels -->
        <text x="0" y="{height - 5}" font-size="11" fill="#6b7280" font-family="system-ui">Less</text>
        <text x="{width}" y="{height - 5}" font-size="11" fill="#6b7280"
              font-family="system-ui" text-anchor="end">More</text>
        <text x="{width//2}" y="{height - 5}" font-size="10" fill="#9ca3af"
              font-family="system-ui" text-anchor="middle">Avg</text>

        <!-- Score value -->
        <text x="{position}" y="{height//2 - 12}" font-size="12" font-weight="bold"
              fill="{marker_color}" font-family="system-ui" text-anchor="middle">{score:.0f}</text>
    </svg>
    '''
    return svg.strip()


def generate_trait_card_html(
    category: str,
    score: float,
    variant_count: int,
    interpretation: str,
    top_variants: List[Dict] = None
) -> str:
    """
    Generate HTML for a single trait card.

    Args:
        category: Category name (e.g., 'cognition')
        score: Genetic score (0-100)
        variant_count: Number of variants analyzed
        interpretation: Text interpretation of score
        top_variants: Optional list of top variants for this category

    Returns:
        HTML markup string
    """
    info = CATEGORY_INFO.get(category, {
        'emoji': '🧬',
        'color': '#6b7280',
        'light_color': '#f3f4f6'
    })

    emoji = info['emoji']
    color = info['color']
    light_color = info['light_color']
    category_name = category.replace('_', ' ').title()

    # Generate variant list if provided
    variant_html = ''
    if top_variants:
        variant_items = []
        for v in top_variants[:3]:  # Top 3 variants
            variant_items.append(f'''
                <div class="variant-item">
                    <strong>{v['rsid']}</strong> <span class="gene-tag">{v['gene']}</span>
                    <div class="variant-detail">{v['trait']}: {v['effect_count']}/2 effect alleles</div>
                </div>
            ''')
        variant_html = '<div class="variant-list">' + ''.join(variant_items) + '</div>'

    card_html = f'''
    <div class="trait-card" style="border-left: 4px solid {color};">
        <div class="card-header" style="background: {light_color};">
            <div class="category-icon" style="background: {color};">{emoji}</div>
            <div class="category-title">
                <h3>{category_name}</h3>
                <p class="snp-count">{variant_count} SNPs analyzed</p>
            </div>
        </div>
        <div class="card-body">
            <div class="score-scale">
                {create_scale_svg(score)}
            </div>
            <div class="interpretation">
                <span class="interpretation-badge">{interpretation}</span>
            </div>
            {variant_html}
        </div>
    </div>
    '''
    return card_html


def generate_html_report(
    scores: Dict,
    extracted_variants: Dict,
    vcf_path: str,
    output_path: Optional[Path] = None
) -> str:
    """
    Generate complete interactive HTML visualization report.

    Args:
        scores: Dictionary of category scores from TraitAnalyzer
        extracted_variants: Dictionary of extracted variants
        vcf_path: Path to VCF file analyzed
        output_path: Optional path to save HTML file

    Returns:
        Complete HTML document as string
    """
    # Generate cards for each category
    cards_html = []

    for category, data in sorted(scores.items()):
        score = data['score']
        count = data['variant_count']

        # Interpret score
        if score >= 60:
            interpretation = "Above average"
        elif score >= 55:
            interpretation = "Slightly above average"
        elif score >= 45:
            interpretation = "Average"
        elif score >= 40:
            interpretation = "Slightly below average"
        else:
            interpretation = "Below average"

        # Get top variants for this category
        category_variants = [
            v for v in extracted_variants.values()
            if v['category'] == category
        ]
        # Sort by effect count descending
        category_variants.sort(key=lambda x: x['effect_count'], reverse=True)

        card = generate_trait_card_html(
            category=category,
            score=score,
            variant_count=count,
            interpretation=interpretation,
            top_variants=category_variants
        )
        cards_html.append(card)

    # Complete HTML document
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Genetic Trait Analysis Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .header {{
            background: white;
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}

        .header h1 {{
            font-size: 2.5rem;
            color: #1f2937;
            margin-bottom: 0.5rem;
        }}

        .header .subtitle {{
            color: #6b7280;
            font-size: 1rem;
        }}

        .header .meta {{
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid #e5e7eb;
            display: flex;
            gap: 2rem;
            flex-wrap: wrap;
        }}

        .meta-item {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: #4b5563;
        }}

        .meta-item strong {{
            color: #1f2937;
        }}

        .traits-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}

        .trait-card {{
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .trait-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);
        }}

        .card-header {{
            padding: 1.5rem;
            display: flex;
            align-items: center;
            gap: 1rem;
        }}

        .category-icon {{
            width: 50px;
            height: 50px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.75rem;
            color: white;
        }}

        .category-title h3 {{
            font-size: 1.25rem;
            color: #1f2937;
            margin-bottom: 0.25rem;
        }}

        .snp-count {{
            font-size: 0.875rem;
            color: #6b7280;
        }}

        .card-body {{
            padding: 1.5rem;
        }}

        .score-scale {{
            margin-bottom: 1rem;
        }}

        .interpretation {{
            text-align: center;
            margin-bottom: 1.5rem;
        }}

        .interpretation-badge {{
            display: inline-block;
            padding: 0.5rem 1.5rem;
            background: #f3f4f6;
            color: #374151;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 500;
        }}

        .variant-list {{
            border-top: 1px solid #e5e7eb;
            padding-top: 1rem;
        }}

        .variant-item {{
            padding: 0.75rem;
            background: #f9fafb;
            border-radius: 8px;
            margin-bottom: 0.5rem;
        }}

        .variant-item:last-child {{
            margin-bottom: 0;
        }}

        .variant-item strong {{
            color: #1f2937;
            font-size: 0.875rem;
        }}

        .gene-tag {{
            display: inline-block;
            padding: 0.125rem 0.5rem;
            background: #e0e7ff;
            color: #4338ca;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-left: 0.5rem;
        }}

        .variant-detail {{
            font-size: 0.8125rem;
            color: #6b7280;
            margin-top: 0.25rem;
        }}

        .footer {{
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}

        .disclaimer {{
            padding: 1rem;
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            border-radius: 8px;
            margin-bottom: 1rem;
        }}

        .disclaimer h4 {{
            color: #92400e;
            margin-bottom: 0.5rem;
        }}

        .disclaimer p {{
            color: #78350f;
            font-size: 0.875rem;
            line-height: 1.5;
        }}

        .disclaimer ul {{
            margin-top: 0.5rem;
            margin-left: 1.5rem;
            color: #78350f;
            font-size: 0.875rem;
        }}

        .disclaimer li {{
            margin-bottom: 0.25rem;
        }}

        @media (max-width: 768px) {{
            body {{
                padding: 1rem;
            }}

            .header h1 {{
                font-size: 1.75rem;
            }}

            .traits-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧬 Genetic Trait Analysis Report</h1>
            <p class="subtitle">Personalized genetic predisposition analysis based on published GWAS studies</p>
            <div class="meta">
                <div class="meta-item">
                    <strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </div>
                <div class="meta-item">
                    <strong>Input:</strong> {Path(vcf_path).name}
                </div>
                <div class="meta-item">
                    <strong>Total SNPs:</strong> {len(extracted_variants)}
                </div>
                <div class="meta-item">
                    <strong>Categories:</strong> {len(scores)}
                </div>
            </div>
        </div>

        <div class="traits-grid">
            {''.join(cards_html)}
        </div>

        <div class="footer">
            <div class="disclaimer">
                <h4>⚠️ Important Information</h4>
                <p><strong>This report is for research and educational purposes only.</strong></p>
                <ul>
                    <li>Most traits are highly polygenic (influenced by hundreds to thousands of variants)</li>
                    <li>Individual SNP effects are generally small; environment and gene-environment interactions are critical</li>
                    <li>These scores represent genetic predisposition only, not destiny</li>
                    <li>Most GWAS studies were conducted in European populations; results may not apply equally to all ancestries</li>
                    <li>Consult a genetic counselor or healthcare provider for clinical interpretation</li>
                    <li>Do not make medical or life decisions based solely on this information</li>
                </ul>
            </div>
            <p style="text-align: center; color: #6b7280; font-size: 0.875rem; margin-top: 1rem;">
                Generated by GeneGenie - Whole Genome Analysis Toolkit
            </p>
        </div>
    </div>
</body>
</html>
'''

    # Save to file if path provided
    if output_path:
        output_path.write_text(html)

    return html


def create_visualization_from_analyzer(analyzer, output_filename: str = 'trait_report.html') -> Path:
    """
    Create HTML visualization from TraitAnalyzer instance.

    Args:
        analyzer: TraitAnalyzer instance with completed analysis
        output_filename: Name of output HTML file

    Returns:
        Path to generated HTML file
    """
    if not analyzer.extracted_variants:
        raise ValueError("No variants extracted. Run extract_all_trait_snps() first.")

    if not analyzer.trait_scores:
        raise ValueError("No scores calculated. Run calculate_category_scores() first.")

    output_path = analyzer.output_dir / output_filename

    generate_html_report(
        scores=analyzer.trait_scores,
        extracted_variants=analyzer.extracted_variants,
        vcf_path=analyzer.vcf_path,
        output_path=output_path
    )

    return output_path
