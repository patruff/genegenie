#!/usr/bin/env python3
"""
Performance Optimization Examples

Demonstrates efficient processing of large genomic datasets.
"""

import sys
sys.path.insert(0, '../src')

from genegenie.utils.performance import (
    create_processing_plan,
    estimate_vcf_size,
    parallel_process_chromosomes,
    optimize_vcf_access
)
from cyvcf2 import VCF


def example_processing_plan(vcf_path: str):
    """Create optimal processing plan for VCF."""

    print("=" * 70)
    print(" Creating Processing Plan")
    print("=" * 70)

    # Assume 16GB RAM, 8 CPUs
    plan = create_processing_plan(vcf_path, available_ram_gb=16, n_cpus=8)

    print(f"\nStrategy: {plan['strategy']}")
    print(f"Recommended processes: {plan['recommended_processes']}")
    print(f"Chunk size: {plan['chunk_size']:,} variants")
    print(f"Is indexed: {plan['is_indexed']}")
    print(f"Estimated variants: {plan['estimated_variants']:,}")

    print("\nEstimated processing time:")
    time_est = plan['estimated_time']
    if time_est['hours'] < 1:
        print(f"  {time_est['minutes']:.1f} minutes")
    else:
        print(f"  {time_est['hours']:.1f} hours")

    if plan['warnings']:
        print("\nWarnings:")
        for warning in plan['warnings']:
            print(f"  - {warning}")

    print()


def example_size_estimation(vcf_path: str):
    """Estimate VCF file size and requirements."""

    print("=" * 70)
    print(" VCF Size Estimation")
    print("=" * 70)

    est = estimate_vcf_size(vcf_path, sample_size=10000)

    print(f"\nFile size: {est['file_size_gb']:.2f} GB")
    print(f"Estimated total variants: {est['estimated_total']:,}")
    print(f"Recommended RAM: {est['recommended_ram_gb']} GB")
    print(f"Avg bytes per variant: {est['avg_bytes_per_variant']:.1f}")

    print()


def example_parallel_processing(vcf_path: str):
    """Process chromosomes in parallel."""

    print("=" * 70)
    print(" Parallel Chromosome Processing")
    print("=" * 70)

    # Define processing function
    def count_high_quality_variants(vcf_path: str, chrom: str):
        """Count high-quality variants in a chromosome."""
        vcf = VCF(vcf_path)
        count = 0

        for variant in vcf(chrom):
            if variant.QUAL and variant.QUAL >= 30:
                count += 1

        vcf.close()
        return {'chrom': chrom, 'count': count}

    # Process first 3 chromosomes as example
    chromosomes = ['chr1', 'chr2', 'chr3']

    print(f"\nProcessing {len(chromosomes)} chromosomes in parallel...")
    print("(Counting high-quality variants: QUAL >= 30)\n")

    results = parallel_process_chromosomes(
        vcf_path,
        count_high_quality_variants,
        chromosomes=chromosomes,
        n_processes=3
    )

    # Display results
    total = 0
    for result in results:
        print(f"{result['chrom']}: {result['count']:,} variants")
        total += result['count']

    print(f"\nTotal: {total:,} high-quality variants")
    print()


def example_optimization_check(vcf_path: str):
    """Check if VCF is optimized for analysis."""

    print("=" * 70)
    print(" VCF Optimization Check")
    print("=" * 70)

    is_optimized = optimize_vcf_access(vcf_path)

    print(f"\nVCF is optimized: {is_optimized}")

    if is_optimized:
        print("✓ File is bgzipped and indexed")
        print("✓ Fast random access enabled")
        print("✓ Ready for region-based queries")
    else:
        print("✗ File needs optimization")
        print("\nTo optimize:")
        print(f"  bgzip -c input.vcf > {vcf_path}")
        print(f"  tabix -p vcf {vcf_path}")

    print()


def main():
    if len(sys.argv) != 2:
        print("Usage: python performance_example.py <input.vcf.gz>")
        print("\nDemonstrates performance optimization techniques")
        sys.exit(1)

    vcf_path = sys.argv[1]

    print("\n" + "=" * 70)
    print(" GeneGenie - Performance Optimization Examples")
    print("=" * 70)
    print(f"\nInput file: {vcf_path}\n")

    # Run examples
    example_optimization_check(vcf_path)
    example_size_estimation(vcf_path)
    example_processing_plan(vcf_path)

    # Only run parallel processing if file is indexed
    if optimize_vcf_access(vcf_path):
        example_parallel_processing(vcf_path)
    else:
        print("\nSkipping parallel processing example (file not indexed)")

    print("\n" + "=" * 70)
    print(" Examples complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()
