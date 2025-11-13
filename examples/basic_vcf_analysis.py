#!/usr/bin/env python3
"""
Basic VCF Analysis Examples

Demonstrates common VCF analysis workflows using GeneGenie.
"""

import sys
sys.path.insert(0, '../src')

from genegenie.analysis.vcf_utils import (
    extract_variants_by_rsid,
    extract_variants_by_position,
    get_apoe_genotype,
    calculate_variant_statistics
)


def example_extract_longevity_snps(vcf_path: str):
    """Extract specific longevity SNPs from VCF."""
    print("=" * 60)
    print("Example 1: Extract Longevity SNPs")
    print("=" * 60)

    # Define key longevity variants
    longevity_snps = [
        'rs7412',      # APOE
        'rs429358',    # APOE
        'rs2802292',   # FOXO3
        'rs1063192',   # CDKN2B
    ]

    print(f"\nExtracting {len(longevity_snps)} longevity variants...")

    try:
        variants = extract_variants_by_rsid(vcf_path, longevity_snps)

        print(f"\nFound {len(variants)} variants:\n")
        for rsid, data in variants.items():
            print(f"{rsid}:")
            print(f"  Position: {data['position']}")
            print(f"  Genotype: {data['genotype']}")
            print(f"  Depth: {data['depth']}x")
            print(f"  Quality: {data['quality']:.1f}")
            print()

    except Exception as e:
        print(f"Error: {e}")


def example_apoe_genotyping(vcf_path: str):
    """Determine APOE genotype."""
    print("=" * 60)
    print("Example 2: APOE Genotyping")
    print("=" * 60)

    print("\nDetermining APOE genotype...")

    try:
        apoe = get_apoe_genotype(vcf_path)

        if apoe:
            print(f"\nAPOE Genotype: {apoe}")

            # Provide interpretation
            interpretations = {
                'ε2/ε2': 'Strongest AD protection, increased longevity',
                'ε2/ε3': 'Protective against AD, favorable',
                'ε2/ε4': 'Mixed effects',
                'ε3/ε3': 'Most common, neutral reference',
                'ε3/ε4': 'Moderately increased AD risk',
                'ε4/ε4': 'Highest AD risk, reduced longevity',
            }

            print(f"Interpretation: {interpretations.get(apoe, 'Unknown')}")
        else:
            print("Could not determine APOE genotype (variants not found)")

    except Exception as e:
        print(f"Error: {e}")


def example_vcf_statistics(vcf_path: str):
    """Calculate VCF quality statistics."""
    print("=" * 60)
    print("Example 3: VCF Quality Statistics")
    print("=" * 60)

    print("\nCalculating statistics (sampling 10,000 variants)...")

    try:
        stats = calculate_variant_statistics(vcf_path, sample_size=10000)

        print("\nResults:")
        print(f"  Total sampled: {stats['total_sampled']:,}")
        print(f"  SNPs: {stats['snp_count']:,} ({stats['snp_ratio']*100:.1f}%)")
        print(f"  Indels: {stats['indel_count']:,}")
        print(f"  Heterozygosity: {stats['het_ratio']*100:.1f}%")
        print(f"  Mean quality: {stats['mean_quality']:.1f}")
        print(f"  Mean depth: {stats['mean_depth']:.1f}x")

    except Exception as e:
        print(f"Error: {e}")


def example_position_query(vcf_path: str):
    """Query variants at specific genomic positions."""
    print("=" * 60)
    print("Example 4: Position-Based Query")
    print("=" * 60)

    # APOE region on chr19 (GRCh38)
    positions = [
        ('chr19', 44908684),  # rs7412
        ('chr19', 44908822),  # rs429358
    ]

    print(f"\nQuerying {len(positions)} positions in APOE region...")

    try:
        variants = extract_variants_by_position(vcf_path, positions)

        print(f"\nFound {len(variants)} variants:\n")
        for (chrom, pos), data in variants.items():
            print(f"{chrom}:{pos}")
            print(f"  rsID: {data['rsid']}")
            print(f"  REF/ALT: {data['ref']}/{data['alt']}")
            print(f"  Genotype: {data['genotype']}")
            print()

    except Exception as e:
        print(f"Error: {e}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python basic_vcf_analysis.py <input.vcf.gz>")
        print("\nRuns example VCF analysis workflows")
        print("Note: VCF must be bgzipped and tabix-indexed")
        sys.exit(1)

    vcf_path = sys.argv[1]

    print("\n" + "=" * 60)
    print("GeneGenie - Basic VCF Analysis Examples")
    print("=" * 60)
    print(f"\nInput file: {vcf_path}\n")

    # Run examples
    example_extract_longevity_snps(vcf_path)
    example_apoe_genotyping(vcf_path)
    example_vcf_statistics(vcf_path)
    example_position_query(vcf_path)

    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
