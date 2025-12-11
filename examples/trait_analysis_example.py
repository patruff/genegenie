#!/usr/bin/env python3
"""
Comprehensive Trait Analysis Examples

Demonstrates analysis of personality, cognition, behavior, and addiction traits.
"""

import sys
sys.path.insert(0, '../src')

from genegenie.trait_analyzer import TraitAnalyzer
from genegenie.utils.trait_db import (
    get_snps_by_category,
    get_snps_by_trait,
    get_all_categories,
    get_snp_info
)


def display_trait_database():
    """Display information about the trait SNP database."""

    print("=" * 70)
    print(" Trait SNP Database Overview")
    print("=" * 70)
    print()

    categories = get_all_categories()
    print(f"Total categories: {len(categories)}\n")

    for category in sorted(categories):
        snps = get_snps_by_category(category)
        print(f"{category.replace('_', ' ').title()}: {len(snps)} SNPs")

        # Show example traits
        traits = set(info['trait'] for info in snps.values())
        print(f"  Traits: {', '.join(sorted(list(traits))[:5])}")
        print()


def display_category_details(category: str):
    """Display detailed information about a specific category."""

    print(f"\n{'=' * 70}")
    print(f" {category.replace('_', ' ').title()} SNPs")
    print("=" * 70)
    print()

    snps = get_snps_by_category(category)

    for rsid, info in list(snps.items())[:10]:  # Show first 10
        print(f"{rsid} ({info['gene']})")
        print(f"  Trait: {info['trait']}")
        print(f"  Effect allele: {info.get('effect_allele', 'N/A')}")
        print(f"  Effect size: {info.get('effect_size', 'N/A')}")
        print(f"  Description: {info['description']}")
        print(f"  Paper: {info.get('paper', 'N/A')[:50]}...")
        print()


def run_full_trait_analysis(vcf_path: str):
    """Run complete trait analysis pipeline."""

    print("\n" + "=" * 70)
    print(" Running Comprehensive Trait Analysis")
    print("=" * 70)
    print()

    # Initialize analyzer
    print("Initializing trait analyzer...")
    analyzer = TraitAnalyzer(vcf_path, output_dir='trait_results')

    # Run analysis
    print("\nRunning analysis pipeline...")
    print("-" * 70)

    report = analyzer.run_analysis()

    print("\n" + "=" * 70)
    print(" Analysis Complete!")
    print("=" * 70)
    print("\nResults saved to:")
    print("  - trait_results/trait_genetics_report.md")
    print("  - trait_results/trait_variants.csv")
    print("  - trait_results/trait_analysis_*.log")

    # Display key findings
    print("\n" + "=" * 70)
    print(" Key Findings Summary")
    print("=" * 70)
    print()

    # Category scores
    print("Category Scores (0-100, 50=average):\n")
    for category, data in sorted(analyzer.trait_scores.items()):
        score = data['score']
        count = data['variant_count']

        bar_length = int(score / 2)  # Scale to 50 chars
        bar = '█' * bar_length + '░' * (50 - bar_length)

        print(f"{category.replace('_', ' ').title():20} {score:5.1f} {bar}")
        print(f"{'':20} ({count} SNPs)")
        print()

    # Notable variants
    print("\n" + "=" * 70)
    print(" Notable Variants")
    print("=" * 70)
    print()

    # Highlight interesting findings
    interesting_categories = ['cognition', 'personality', 'addiction']

    for category in interesting_categories:
        report_data = analyzer.get_category_report(category)
        if 'error' in report_data:
            continue

        print(f"\n{category.replace('_', ' ').title()}:")
        print(f"  Score: {report_data['score']:.1f}")
        print(f"  Avg effect alleles: {report_data['avg_effect_alleles']:.2f}/2.0")

        # Show top variants
        top_variants = sorted(
            report_data['variants'],
            key=lambda x: x['effect_count'],
            reverse=True
        )[:3]

        for variant in top_variants:
            print(f"\n  {variant['rsid']} ({variant['gene']}) - {variant['trait']}")
            print(f"    Genotype: {variant['genotype']}")
            print(f"    Effect alleles: {variant['effect_count']}/2")


def show_specific_trait(vcf_path: str, trait: str):
    """Analyze specific trait (e.g., Intelligence, Neuroticism)."""

    print(f"\n{'=' * 70}")
    print(f" {trait} Analysis")
    print("=" * 70)
    print()

    # Get SNPs for this trait
    trait_snps = get_snps_by_trait(trait)

    print(f"Database contains {len(trait_snps)} SNPs for {trait}\n")

    # Extract from VCF (simplified)
    from genegenie.analysis.vcf_utils import extract_variants_by_position

    positions = [(info['chrom'], info['pos']) for info in trait_snps.values()]

    print(f"Extracting from genome...")
    # This would extract the variants from the VCF
    # For demo purposes, we'll just show the database entries

    for rsid, info in list(trait_snps.items())[:5]:
        print(f"\n{rsid} ({info['gene']})")
        print(f"  Position: {info['chrom']}:{info['pos']}")
        print(f"  Effect allele: {info.get('effect_allele', 'N/A')}")
        print(f"  {info['description']}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python trait_analysis_example.py <command> [options]")
        print("\nCommands:")
        print("  database              - Show trait database overview")
        print("  category <name>       - Show SNPs in category")
        print("  analyze <vcf>         - Run full trait analysis")
        print("  trait <vcf> <trait>   - Analyze specific trait")
        print()
        print("Categories:")
        for cat in sorted(get_all_categories()):
            print(f"  - {cat}")
        print()
        sys.exit(1)

    command = sys.argv[1]

    if command == 'database':
        display_trait_database()

    elif command == 'category':
        if len(sys.argv) < 3:
            print("Usage: python trait_analysis_example.py category <name>")
            sys.exit(1)
        display_category_details(sys.argv[2])

    elif command == 'analyze':
        if len(sys.argv) < 3:
            print("Usage: python trait_analysis_example.py analyze <vcf.gz>")
            sys.exit(1)

        # Show database first
        display_trait_database()

        # Run analysis
        run_full_trait_analysis(sys.argv[2])

    elif command == 'trait':
        if len(sys.argv) < 4:
            print("Usage: python trait_analysis_example.py trait <vcf.gz> <trait>")
            print("\nExample traits: Intelligence, Neuroticism, Risk-taking")
            sys.exit(1)
        show_specific_trait(sys.argv[2], sys.argv[3])

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
