"""
Performance Optimization Utilities

Tools for efficient processing of large genomic datasets.
Includes parallelization, chunking, and memory management utilities.
"""

from multiprocessing import Pool, cpu_count
from cyvcf2 import VCF
import numpy as np
from typing import Callable, Dict, List, Tuple, Any, Iterator
from pathlib import Path


def chunk_by_chromosome(
    vcf_path: str,
    include_chromosomes: List[str] = None
) -> List[str]:
    """
    Get list of chromosomes for parallel processing.

    Args:
        vcf_path: Path to VCF file
        include_chromosomes: Specific chromosomes to include (None = all)

    Returns:
        List of chromosome names

    Example:
        >>> chroms = chunk_by_chromosome('genome.vcf.gz')
        >>> print(f"Processing {len(chroms)} chromosomes in parallel")
    """
    if include_chromosomes:
        return include_chromosomes

    # Standard human chromosomes
    autosomes = [f'chr{i}' for i in range(1, 23)]
    sex_chroms = ['chrX', 'chrY']
    mito = ['chrM']

    return autosomes + sex_chroms + mito


def parallel_process_chromosomes(
    vcf_path: str,
    process_func: Callable[[str, str], Any],
    chromosomes: List[str] = None,
    n_processes: int = None
) -> List[Any]:
    """
    Process chromosomes in parallel using multiprocessing.

    Args:
        vcf_path: Path to VCF file
        process_func: Function that takes (vcf_path, chrom) and returns result
        chromosomes: List of chromosomes to process (None = all)
        n_processes: Number of parallel processes (None = CPU count)

    Returns:
        List of results from each chromosome

    Example:
        >>> def count_variants(vcf_path, chrom):
        >>>     vcf = VCF(vcf_path)
        >>>     return sum(1 for _ in vcf(chrom))
        >>>
        >>> results = parallel_process_chromosomes('genome.vcf.gz', count_variants)
    """
    if chromosomes is None:
        chromosomes = chunk_by_chromosome(vcf_path)

    if n_processes is None:
        n_processes = min(cpu_count(), len(chromosomes))

    # Create argument tuples for each chromosome
    args = [(vcf_path, chrom) for chrom in chromosomes]

    with Pool(processes=n_processes) as pool:
        results = pool.starmap(process_func, args)

    return results


def stream_variants_in_chunks(
    vcf_path: str,
    chunk_size: int = 10000
) -> Iterator[List]:
    """
    Stream variants in memory-efficient chunks.

    Args:
        vcf_path: Path to VCF file
        chunk_size: Number of variants per chunk

    Yields:
        Lists of variants

    Example:
        >>> for chunk in stream_variants_in_chunks('genome.vcf.gz', 1000):
        >>>     # Process 1000 variants at a time
        >>>     process_chunk(chunk)
    """
    vcf = VCF(vcf_path)

    chunk = []
    for variant in vcf:
        chunk.append(variant)

        if len(chunk) >= chunk_size:
            yield chunk
            chunk = []

    # Yield remaining variants
    if chunk:
        yield chunk

    vcf.close()


def estimate_vcf_size(vcf_path: str, sample_size: int = 10000) -> Dict:
    """
    Estimate total variant count and memory requirements.

    Args:
        vcf_path: Path to VCF file
        sample_size: Number of variants to sample

    Returns:
        Dictionary with size estimates

    Example:
        >>> est = estimate_vcf_size('genome.vcf.gz')
        >>> print(f"Estimated variants: {est['estimated_total']:,}")
    """
    vcf = VCF(vcf_path)

    # Sample variants to estimate size
    sample_count = 0
    total_bases = 0

    for i, variant in enumerate(vcf):
        if i >= sample_size:
            break
        sample_count += 1
        # Estimate memory per variant
        total_bases += len(variant.REF) + sum(len(a) for a in variant.ALT)

    vcf.close()

    # Rough estimates
    avg_bytes_per_variant = (total_bases / sample_count) if sample_count > 0 else 100

    # Try to get file size
    file_size = Path(vcf_path).stat().st_size

    # Very rough estimate - compression ratio ~10:1 for VCF
    estimated_total = file_size // (avg_bytes_per_variant // 10)

    return {
        'sampled_variants': sample_count,
        'avg_bytes_per_variant': avg_bytes_per_variant,
        'file_size_bytes': file_size,
        'file_size_gb': file_size / (1024**3),
        'estimated_total': int(estimated_total),
        'recommended_ram_gb': int(estimated_total * avg_bytes_per_variant / (1024**3)),
    }


def optimize_vcf_access(vcf_path: str) -> bool:
    """
    Check if VCF is optimized for random access.

    Args:
        vcf_path: Path to VCF file

    Returns:
        True if optimized (bgzipped + indexed)

    Example:
        >>> if not optimize_vcf_access('variants.vcf.gz'):
        >>>     print("Please bgzip and index the VCF file")
    """
    vcf_file = Path(vcf_path)

    # Check if bgzipped
    is_bgzipped = vcf_path.endswith('.gz')

    # Check if indexed (.tbi or .csi)
    has_tbi = Path(f"{vcf_path}.tbi").exists()
    has_csi = Path(f"{vcf_path}.csi").exists()

    return is_bgzipped and (has_tbi or has_csi)


def calculate_processing_time_estimate(
    total_variants: int,
    variants_per_second: int = 10000
) -> Dict:
    """
    Estimate processing time for variant analysis.

    Args:
        total_variants: Total number of variants
        variants_per_second: Processing speed (variants/second)

    Returns:
        Dictionary with time estimates

    Example:
        >>> est = calculate_processing_time_estimate(3_000_000_000)
        >>> print(f"Estimated time: {est['hours']:.1f} hours")
    """
    total_seconds = total_variants / variants_per_second

    return {
        'total_seconds': total_seconds,
        'minutes': total_seconds / 60,
        'hours': total_seconds / 3600,
        'variants_per_second': variants_per_second,
        'recommendation': (
            'Use parallel processing by chromosome'
            if total_seconds > 3600
            else 'Single-threaded processing acceptable'
        ),
    }


def memory_efficient_aggregation(
    vcf_path: str,
    aggregation_func: Callable,
    chunk_size: int = 10000
) -> Any:
    """
    Perform aggregation on large VCF without loading all variants into memory.

    Args:
        vcf_path: Path to VCF file
        aggregation_func: Function that takes list of variants and returns aggregate
        chunk_size: Number of variants to process at once

    Returns:
        Aggregated result

    Example:
        >>> def count_high_qual(variants):
        >>>     return sum(1 for v in variants if v.QUAL >= 30)
        >>>
        >>> total = memory_efficient_aggregation('genome.vcf.gz', count_high_qual)
    """
    vcf = VCF(vcf_path)

    results = []
    chunk = []

    for variant in vcf:
        chunk.append(variant)

        if len(chunk) >= chunk_size:
            # Process chunk and store result
            result = aggregation_func(chunk)
            results.append(result)
            chunk = []

    # Process remaining variants
    if chunk:
        result = aggregation_func(chunk)
        results.append(result)

    vcf.close()

    # Combine results (assuming summation - adjust as needed)
    return sum(results)


def get_optimal_chunk_size(available_ram_gb: int = 8) -> int:
    """
    Calculate optimal chunk size based on available RAM.

    Args:
        available_ram_gb: Available RAM in GB

    Returns:
        Recommended chunk size

    Example:
        >>> chunk_size = get_optimal_chunk_size(16)
        >>> print(f"Use chunk size: {chunk_size:,}")
    """
    # Rough estimate: 1KB per variant in memory
    bytes_per_variant = 1024

    # Use 50% of available RAM for chunk
    chunk_bytes = (available_ram_gb * 1024**3) * 0.5

    chunk_size = int(chunk_bytes / bytes_per_variant)

    # Clamp to reasonable range
    chunk_size = max(1000, min(chunk_size, 1000000))

    return chunk_size


def create_processing_plan(
    vcf_path: str,
    available_ram_gb: int = 8,
    n_cpus: int = None
) -> Dict:
    """
    Create optimal processing plan for VCF analysis.

    Args:
        vcf_path: Path to VCF file
        available_ram_gb: Available RAM in GB
        n_cpus: Number of CPUs (None = auto-detect)

    Returns:
        Dictionary with processing recommendations

    Example:
        >>> plan = create_processing_plan('genome.vcf.gz', available_ram_gb=64)
        >>> print(plan['strategy'])
    """
    if n_cpus is None:
        n_cpus = cpu_count()

    # Get VCF statistics
    size_est = estimate_vcf_size(vcf_path)
    is_optimized = optimize_vcf_access(vcf_path)

    # Determine strategy
    if size_est['estimated_total'] > 100_000_000:  # > 100M variants
        strategy = 'parallel_by_chromosome'
        recommended_processes = min(n_cpus, 24)
    elif size_est['estimated_total'] > 10_000_000:  # > 10M variants
        strategy = 'chunked_streaming'
        recommended_processes = 1
    else:
        strategy = 'single_pass'
        recommended_processes = 1

    chunk_size = get_optimal_chunk_size(available_ram_gb)

    plan = {
        'strategy': strategy,
        'recommended_processes': recommended_processes,
        'chunk_size': chunk_size,
        'is_indexed': is_optimized,
        'estimated_variants': size_est['estimated_total'],
        'estimated_time': calculate_processing_time_estimate(
            size_est['estimated_total'],
            variants_per_second=10000 * recommended_processes
        ),
        'warnings': [],
    }

    # Add warnings
    if not is_optimized:
        plan['warnings'].append(
            'VCF not optimized - bgzip and tabix index for faster access'
        )

    if size_est['recommended_ram_gb'] > available_ram_gb:
        plan['warnings'].append(
            f'Recommended RAM ({size_est["recommended_ram_gb"]}GB) '
            f'exceeds available ({available_ram_gb}GB) - use streaming'
        )

    return plan
