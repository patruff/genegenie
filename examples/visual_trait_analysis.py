#!/usr/bin/env python3
"""
Visual Trait Analysis Example

Demonstrates how to generate interactive HTML visualizations of genetic trait analysis.
Creates a grid of trait cards showing genetic predisposition scores with visual scales.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from genegenie.trait_analyzer import TraitAnalyzer


def main():
    """
    Run trait analysis with visual HTML report generation.
    """
    print("=" * 70)
    print("Visual Genetic Trait Analysis")
    print("=" * 70)
    print()

    # Example VCF file path
    if len(sys.argv) > 1:
        vcf_path = sys.argv[1]
    else:
        print("Usage: python visual_trait_analysis.py <input.vcf.gz>")
        print()
        print("Example:")
        print("  python visual_trait_analysis.py ../data/my_genome.vcf.gz")
        print()
        print("This will generate:")
        print("  1. trait_results/trait_report.html - Interactive visual report")
        print("  2. trait_results/trait_genetics_report.md - Markdown report")
        print("  3. trait_results/trait_variants.csv - Raw variant data")
        print()
        return

    # Verify file exists
    if not Path(vcf_path).exists():
        print(f"❌ Error: File not found: {vcf_path}")
        return

    if not Path(f"{vcf_path}.tbi").exists():
        print(f"❌ Error: Index file not found: {vcf_path}.tbi")
        print(f"Create index with: tabix -p vcf {vcf_path}")
        return

    print(f"📁 Input VCF: {vcf_path}")
    print(f"📊 Output directory: trait_results/")
    print()

    # Initialize analyzer
    analyzer = TraitAnalyzer(vcf_path, output_dir='trait_results')

    # Run complete analysis with HTML visualization
    print("🧬 Analyzing genetic traits...")
    print()
    report = analyzer.run_analysis(generate_html=True)

    print()
    print("=" * 70)
    print("✅ Analysis Complete!")
    print("=" * 70)
    print()
    print("Generated files:")
    print("  📊 trait_results/trait_report.html - Open this in your browser!")
    print("  📝 trait_results/trait_genetics_report.md")
    print("  📁 trait_results/trait_variants.csv")
    print()

    # Display summary
    print("Category Summary:")
    print("-" * 70)
    for category, data in sorted(analyzer.trait_scores.items()):
        score = data['score']
        count = data['variant_count']

        # Determine emoji based on score
        if score >= 60:
            emoji = "📈"
        elif score >= 55:
            emoji = "↗️"
        elif score >= 45:
            emoji = "➡️"
        elif score >= 40:
            emoji = "↘️"
        else:
            emoji = "📉"

        category_name = category.replace('_', ' ').title()
        print(f"  {emoji} {category_name:20s} Score: {score:5.1f}  ({count} SNPs)")

    print()
    print("🌐 Open the HTML report in your browser to see the visual trait grid!")
    print(f"   file://{Path('trait_results/trait_report.html').absolute()}")
    print()


def demo_programmatic_usage():
    """
    Example of programmatically accessing trait analysis results.
    """
    print("\n" + "=" * 70)
    print("Programmatic Access Example")
    print("=" * 70 + "\n")

    # Example: Access specific category data
    vcf_path = "data/genome.vcf.gz"

    analyzer = TraitAnalyzer(vcf_path)
    analyzer.extract_all_trait_snps()
    analyzer.calculate_category_scores()

    # Get cognition report
    cognition = analyzer.get_category_report('cognition')

    print(f"Cognition Score: {cognition['score']:.1f}")
    print(f"Variants analyzed: {cognition['variant_count']}")
    print()
    print("Top variants:")
    for variant in cognition['variants'][:3]:
        print(f"  - {variant['rsid']} ({variant['gene']}): {variant['genotype']}")
        print(f"    {variant['description']}")
        print()

    # Generate only HTML (no markdown)
    html_path = analyzer.generate_visual_report()
    print(f"Visual report: {html_path}")


if __name__ == '__main__':
    main()

    # Uncomment to see programmatic usage example:
    # demo_programmatic_usage()
