"""
FASTQ File Utilities

Tools for quality control and analysis of raw sequencing reads.
Uses BioPython for efficient FASTQ parsing.
"""

from Bio.SeqIO.QualityIO import FastqGeneralIterator
from Bio import SeqIO
import gzip
import numpy as np
from typing import Dict, List, Tuple, Optional, Iterator
from pathlib import Path


def quality_control_fastq(
    fastq_path: str,
    sample_size: int = 100000
) -> Dict:
    """
    Perform quality control analysis on FASTQ file.

    Args:
        fastq_path: Path to FASTQ file (can be gzipped)
        sample_size: Number of reads to sample for QC

    Returns:
        Dictionary with QC statistics

    Example:
        >>> qc = quality_control_fastq('reads_R1.fastq.gz')
        >>> print(f"Mean quality: {qc['mean_quality']:.1f}")
    """
    # Determine if gzipped
    is_gzipped = fastq_path.endswith('.gz')

    qualities = []
    lengths = []
    gc_contents = []
    count = 0

    if is_gzipped:
        handle = gzip.open(fastq_path, 'rt')
    else:
        handle = open(fastq_path, 'r')

    for title, sequence, quality in FastqGeneralIterator(handle):
        if count >= sample_size:
            break

        # Calculate mean quality for this read
        phred_scores = [ord(q) - 33 for q in quality]
        qualities.extend(phred_scores)

        # Read length
        lengths.append(len(sequence))

        # GC content
        gc_count = sequence.count('G') + sequence.count('C')
        gc_contents.append(gc_count / len(sequence) * 100)

        count += 1

    handle.close()

    stats = {
        'reads_analyzed': count,
        'mean_quality': np.mean(qualities),
        'median_quality': np.median(qualities),
        'mean_read_length': np.mean(lengths),
        'median_read_length': np.median(lengths),
        'mean_gc_content': np.mean(gc_contents),
        'reads_above_q20': sum(q >= 20 for q in qualities) / len(qualities) * 100,
        'reads_above_q30': sum(q >= 30 for q in qualities) / len(qualities) * 100,
    }

    return stats


def filter_reads_by_quality(
    input_fastq: str,
    output_fastq: str,
    min_mean_quality: float = 30.0,
    min_length: int = 50
) -> int:
    """
    Filter FASTQ reads by quality and length.

    Args:
        input_fastq: Input FASTQ file path
        output_fastq: Output FASTQ file path
        min_mean_quality: Minimum mean quality score
        min_length: Minimum read length

    Returns:
        Number of reads passing filters

    Example:
        >>> count = filter_reads_by_quality('raw.fastq.gz', 'filtered.fastq.gz')
        >>> print(f"Retained {count} high-quality reads")
    """
    is_gzipped_in = input_fastq.endswith('.gz')
    is_gzipped_out = output_fastq.endswith('.gz')

    if is_gzipped_in:
        in_handle = gzip.open(input_fastq, 'rt')
    else:
        in_handle = open(input_fastq, 'r')

    if is_gzipped_out:
        out_handle = gzip.open(output_fastq, 'wt')
    else:
        out_handle = open(output_fastq, 'w')

    passed = 0

    for title, sequence, quality in FastqGeneralIterator(in_handle):
        # Calculate mean quality
        phred_scores = [ord(q) - 33 for q in quality]
        mean_qual = sum(phred_scores) / len(phred_scores)

        # Apply filters
        if mean_qual >= min_mean_quality and len(sequence) >= min_length:
            # Write in FASTQ format
            out_handle.write(f"@{title}\n{sequence}\n+\n{quality}\n")
            passed += 1

    in_handle.close()
    out_handle.close()

    return passed


def calculate_read_statistics(fastq_path: str, sample_size: int = 100000) -> Dict:
    """
    Calculate comprehensive read statistics from FASTQ file.

    Args:
        fastq_path: Path to FASTQ file
        sample_size: Number of reads to analyze

    Returns:
        Dictionary with detailed statistics

    Example:
        >>> stats = calculate_read_statistics('reads.fastq.gz')
        >>> print(f"Total bases: {stats['total_bases']:,}")
    """
    is_gzipped = fastq_path.endswith('.gz')

    if is_gzipped:
        handle = gzip.open(fastq_path, 'rt')
    else:
        handle = open(fastq_path, 'r')

    total_reads = 0
    total_bases = 0
    qualities = []
    lengths = []
    base_counts = {'A': 0, 'C': 0, 'G': 0, 'T': 0, 'N': 0}
    position_qualities = {}

    for title, sequence, quality in FastqGeneralIterator(handle):
        if total_reads >= sample_size:
            break

        total_reads += 1
        total_bases += len(sequence)
        lengths.append(len(sequence))

        # Per-base quality
        phred_scores = [ord(q) - 33 for q in quality]
        qualities.extend(phred_scores)

        # Position-specific quality
        for pos, qual in enumerate(phred_scores):
            if pos not in position_qualities:
                position_qualities[pos] = []
            position_qualities[pos].append(qual)

        # Base composition
        for base in sequence:
            if base in base_counts:
                base_counts[base] += 1

    handle.close()

    # Calculate position-wise mean qualities
    pos_mean_qualities = {
        pos: np.mean(quals)
        for pos, quals in position_qualities.items()
    }

    stats = {
        'total_reads': total_reads,
        'total_bases': total_bases,
        'mean_read_length': np.mean(lengths),
        'median_read_length': np.median(lengths),
        'min_read_length': np.min(lengths),
        'max_read_length': np.max(lengths),
        'mean_quality': np.mean(qualities),
        'median_quality': np.median(qualities),
        'gc_content': (base_counts['G'] + base_counts['C']) / total_bases * 100,
        'n_content': base_counts['N'] / total_bases * 100,
        'base_composition': {
            base: count / total_bases * 100
            for base, count in base_counts.items()
        },
        'quality_drop_off': detect_quality_dropoff(pos_mean_qualities),
    }

    return stats


def detect_quality_dropoff(position_qualities: Dict[int, float]) -> Dict:
    """
    Detect quality degradation along read length.

    Args:
        position_qualities: Dictionary mapping position to mean quality

    Returns:
        Dictionary with dropoff analysis
    """
    if not position_qualities:
        return {'detected': False}

    positions = sorted(position_qualities.keys())
    qualities = [position_qualities[pos] for pos in positions]

    # Check if quality drops significantly in last 20% of read
    read_length = len(positions)
    cutoff = int(read_length * 0.8)

    first_80_mean = np.mean(qualities[:cutoff]) if cutoff > 0 else 0
    last_20_mean = np.mean(qualities[cutoff:]) if cutoff < len(qualities) else 0

    dropoff = first_80_mean - last_20_mean

    return {
        'detected': dropoff > 5,  # Quality drops by >5 points
        'dropoff_amount': dropoff,
        'first_80pct_mean': first_80_mean,
        'last_20pct_mean': last_20_mean,
    }


def count_reads(fastq_path: str) -> int:
    """
    Count total number of reads in FASTQ file.

    Args:
        fastq_path: Path to FASTQ file

    Returns:
        Total read count

    Example:
        >>> count = count_reads('reads.fastq.gz')
        >>> print(f"File contains {count:,} reads")
    """
    is_gzipped = fastq_path.endswith('.gz')

    if is_gzipped:
        handle = gzip.open(fastq_path, 'rt')
    else:
        handle = open(fastq_path, 'r')

    count = sum(1 for _ in FastqGeneralIterator(handle))

    handle.close()

    return count


def paired_end_qc(
    fastq_r1: str,
    fastq_r2: str,
    sample_size: int = 100000
) -> Dict:
    """
    Quality control for paired-end FASTQ files.

    Args:
        fastq_r1: Path to R1 (forward) FASTQ file
        fastq_r2: Path to R2 (reverse) FASTQ file
        sample_size: Number of read pairs to analyze

    Returns:
        Dictionary with paired-end QC statistics

    Example:
        >>> qc = paired_end_qc('reads_R1.fastq.gz', 'reads_R2.fastq.gz')
        >>> print(f"R1 mean quality: {qc['r1_mean_quality']:.1f}")
        >>> print(f"R2 mean quality: {qc['r2_mean_quality']:.1f}")
    """
    # Run QC on both files
    r1_stats = quality_control_fastq(fastq_r1, sample_size)
    r2_stats = quality_control_fastq(fastq_r2, sample_size)

    # Combine results
    stats = {
        'r1_mean_quality': r1_stats['mean_quality'],
        'r2_mean_quality': r2_stats['mean_quality'],
        'r1_mean_length': r1_stats['mean_read_length'],
        'r2_mean_length': r2_stats['mean_read_length'],
        'quality_asymmetry': abs(r1_stats['mean_quality'] - r2_stats['mean_quality']),
        'r1_stats': r1_stats,
        'r2_stats': r2_stats,
    }

    return stats
