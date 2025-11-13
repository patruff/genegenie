#!/usr/bin/env python3
"""
Complete Longevity Analysis Example

Demonstrates the full longevity genomics analysis pipeline.
"""

import sys
sys.path.insert(0, '../src')

from genegenie import WGSLongevityAnalyzer
from genegenie.utils.longevity_db import (
    get_longevity_variants,
    interpret_apoe_genotype,
    get_gene_info
)


def run_full_analysis(vcf_path: str):
    """Run complete longevity analysis pipeline."""

    print("=" * 70)
    print(" GeneGenie - Comprehensive Longevity Genomics Analysis")
    print("=" * 70)
    print()

    # Initialize analyzer
    print("Initializing analyzer...")
    analyzer = WGSLongevityAnalyzer(vcf_path, output_dir='longevity_results')

    # Run analysis
    print("\nRunning analysis pipeline...")
    print("-" * 70)

    report = analyzer.run_analysis()

    print("\n" + "=" * 70)
    print(" Analysis Complete!")
    print("=" * 70)
    print("\nFull report saved to: longevity_results/longevity_report.md")
    print("Log file saved to: longevity_results/analysis_*.log")

    # Display key findings
    print("\n" + "=" * 70)
    print(" Key Findings Summary")
    print("=" * 70)

    # APOE status
    apoe = analyzer.determine_apoe_status()
    if apoe:
        print(f"\nAPOE Genotype: {apoe}")
        interp = interpret_apoe_genotype(apoe)
        print(f"  Alzheimer's Risk: {interp.get('ad_risk', 'Unknown')}")
        print(f"  Longevity Effect: {interp.get('longevity', 'Unknown')}")
        print(f"  Population Frequency: {interp.get('frequency', 'Unknown')}")

    # Polygenic score
    pgs = analyzer.calculate_polygenic_score()
    print(f"\nPolygenic Longevity Score: {pgs:.3f}")
    if pgs > 0.5:
        print("  → Strong protective genetic profile")
    elif pgs > 0:
        print("  → Favorable genetic profile")
    elif pgs > -0.5:
        print("  → Average genetic profile")
    else:
        print("  → Less favorable genetic profile")

    # Variant summary
    print(f"\nLongevity Variants Analyzed: {len(analyzer.variants)}")
    for rsid, data in analyzer.variants.items():
        gene = data['gene']
        protective = data['protective_alleles']
        print(f"  {rsid} ({gene}): {protective}/2 protective alleles")

    print("\n" + "=" * 70)
    print()


def display_gene_information():
    """Display information about key longevity genes."""

    print("\n" + "=" * 70)
    print(" Key Longevity Genes")
    print("=" * 70)

    genes = ['APOE', 'FOXO3', 'CDKN2B']

    for gene in genes:
        info = get_gene_info(gene)
        if info:
            print(f"\n{gene} - {info['full_name']}")
            print(f"  Function: {info['function']}")
            print(f"  Pathway: {info['pathway']}")
            print(f"  Evidence: {info['evidence_level']}")
            if info['key_variants']:
                print(f"  Key Variants: {', '.join(info['key_variants'])}")

    print()


def display_variant_database():
    """Display longevity variant database summary."""

    print("\n" + "=" * 70)
    print(" Longevity Variant Database")
    print("=" * 70)

    # All variants
    all_variants = get_longevity_variants()
    print(f"\nTotal longevity variants tracked: {len(all_variants)}")

    # By gene
    genes = set(v['gene'] for v in all_variants.values())
    print(f"Genes covered: {len(genes)}")

    for gene in sorted(genes):
        gene_variants = get_longevity_variants([gene])
        print(f"\n{gene} ({len(gene_variants)} variants):")
        for rsid, info in gene_variants.items():
            print(f"  {rsid}: {info['description']}")

    print()


def main():
    if len(sys.argv) != 2:
        print("Usage: python longevity_analysis_example.py <input.vcf.gz>")
        print("\nRuns comprehensive longevity genomics analysis")
        print("\nRequirements:")
        print("  - VCF file must be bgzipped and tabix-indexed")
        print("  - Reference genome: GRCh38 (recommended)")
        print("  - Coverage: 30x WGS (recommended)")
        print()
        sys.exit(1)

    vcf_path = sys.argv[1]

    # Display information
    display_gene_information()
    display_variant_database()

    # Run analysis
    run_full_analysis(vcf_path)


if __name__ == '__main__':
    main()
