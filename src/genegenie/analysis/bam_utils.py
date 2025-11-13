"""
BAM/CRAM File Utilities

Tools for analyzing aligned sequencing reads using pysam.
Provides functions for coverage analysis, read extraction, and quality assessment.
"""

import pysam
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Iterator
from pathlib import Path


def get_coverage_stats(
    bam_path: str,
    regions: Optional[List[Tuple[str, int, int]]] = None
) -> Dict:
    """
    Calculate coverage statistics for BAM file.

    Args:
        bam_path: Path to BAM or CRAM file (must be indexed)
        regions: Optional list of (chrom, start, end) tuples to analyze

    Returns:
        Dictionary with coverage statistics

    Example:
        >>> stats = get_coverage_stats('sample.bam')
        >>> print(f"Mean coverage: {stats['mean_coverage']:.1f}x")
    """
    bam = pysam.AlignmentFile(bam_path, "rb")

    depths = []
    positions = 0

    if regions:
        # Calculate coverage for specific regions
        for chrom, start, end in regions:
            for pileup_column in bam.pileup(chrom, start, end):
                depths.append(pileup_column.n)
                positions += 1
    else:
        # Sample coverage across genome
        # (full genome would be too slow - sample chromosomes)
        for chrom in ['chr1', 'chr2', 'chr3']:
            count = 0
            for pileup_column in bam.pileup(chrom, 0, 10000000):
                depths.append(pileup_column.n)
                positions += 1
                count += 1
                if count >= 100000:  # Sample 100k positions per chromosome
                    break

    bam.close()

    if not depths:
        return {'error': 'No coverage data collected'}

    stats = {
        'positions_analyzed': positions,
        'mean_coverage': np.mean(depths),
        'median_coverage': np.median(depths),
        'std_coverage': np.std(depths),
        'min_coverage': np.min(depths),
        'max_coverage': np.max(depths),
        'pct_above_10x': np.sum(np.array(depths) >= 10) / len(depths) * 100,
        'pct_above_20x': np.sum(np.array(depths) >= 20) / len(depths) * 100,
        'pct_above_30x': np.sum(np.array(depths) >= 30) / len(depths) * 100,
    }

    return stats


def extract_reads_in_region(
    bam_path: str,
    chrom: str,
    start: int,
    end: int,
    min_mapq: int = 20
) -> List[Dict]:
    """
    Extract all reads overlapping a genomic region.

    Args:
        bam_path: Path to BAM or CRAM file
        chrom: Chromosome name
        start: Start position (0-based)
        end: End position (0-based)
        min_mapq: Minimum mapping quality

    Returns:
        List of dictionaries with read information

    Example:
        >>> reads = extract_reads_in_region('sample.bam', 'chr19', 44908680, 44908690)
        >>> print(f"Found {len(reads)} reads")
    """
    bam = pysam.AlignmentFile(bam_path, "rb")

    reads = []

    for read in bam.fetch(chrom, start, end):
        # Filter by mapping quality
        if read.mapping_quality < min_mapq:
            continue

        reads.append({
            'name': read.query_name,
            'sequence': read.query_sequence,
            'quality': read.query_qualities.tolist() if read.query_qualities is not None else [],
            'position': read.reference_start,
            'end': read.reference_end,
            'mapq': read.mapping_quality,
            'is_reverse': read.is_reverse,
            'is_paired': read.is_paired,
            'cigar': read.cigarstring,
        })

    bam.close()

    return reads


def calculate_depth_profile(
    bam_path: str,
    chrom: str,
    start: int,
    end: int,
    min_base_quality: int = 20
) -> pd.DataFrame:
    """
    Calculate per-position depth profile for a region.

    Args:
        bam_path: Path to BAM or CRAM file
        chrom: Chromosome name
        start: Start position
        end: End position
        min_base_quality: Minimum base quality to count

    Returns:
        DataFrame with columns: position, depth, A_count, C_count, G_count, T_count

    Example:
        >>> profile = calculate_depth_profile('sample.bam', 'chr19', 44908684, 44908822)
        >>> print(profile.head())
    """
    bam = pysam.AlignmentFile(bam_path, "rb")

    positions = []
    depths = []
    base_counts = {'A': [], 'C': [], 'G': [], 'T': []}

    for pileup_column in bam.pileup(chrom, start, end, min_base_quality=min_base_quality):
        if pileup_column.pos < start or pileup_column.pos >= end:
            continue

        positions.append(pileup_column.pos)
        depths.append(pileup_column.n)

        # Count bases at this position
        bases = {'A': 0, 'C': 0, 'G': 0, 'T': 0}
        for pileup_read in pileup_column.pileups:
            if not pileup_read.is_del and not pileup_read.is_refskip:
                base = pileup_read.alignment.query_sequence[pileup_read.query_position]
                if base in bases:
                    bases[base] += 1

        for base in 'ACGT':
            base_counts[base].append(bases[base])

    bam.close()

    df = pd.DataFrame({
        'position': positions,
        'depth': depths,
        'A_count': base_counts['A'],
        'C_count': base_counts['C'],
        'G_count': base_counts['G'],
        'T_count': base_counts['T'],
    })

    return df


def get_read_statistics(bam_path: str, sample_size: int = 100000) -> Dict:
    """
    Calculate overall read statistics from BAM file.

    Args:
        bam_path: Path to BAM or CRAM file
        sample_size: Number of reads to sample

    Returns:
        Dictionary with read statistics

    Example:
        >>> stats = get_read_statistics('sample.bam')
        >>> print(f"Mean read length: {stats['mean_read_length']}")
    """
    bam = pysam.AlignmentFile(bam_path, "rb")

    read_lengths = []
    mapping_qualities = []
    insert_sizes = []
    total_reads = 0
    mapped_reads = 0
    paired_reads = 0
    properly_paired = 0

    for i, read in enumerate(bam.fetch()):
        if i >= sample_size:
            break

        total_reads += 1

        if not read.is_unmapped:
            mapped_reads += 1
            read_lengths.append(read.query_length)
            mapping_qualities.append(read.mapping_quality)

        if read.is_paired:
            paired_reads += 1
            if read.is_proper_pair:
                properly_paired += 1
            if read.template_length != 0:
                insert_sizes.append(abs(read.template_length))

    bam.close()

    stats = {
        'total_reads_sampled': total_reads,
        'mapped_reads': mapped_reads,
        'mapping_rate': mapped_reads / total_reads if total_reads > 0 else 0,
        'paired_reads': paired_reads,
        'properly_paired': properly_paired,
        'proper_pair_rate': properly_paired / paired_reads if paired_reads > 0 else 0,
        'mean_read_length': np.mean(read_lengths) if read_lengths else 0,
        'mean_mapq': np.mean(mapping_qualities) if mapping_qualities else 0,
        'mean_insert_size': np.mean(insert_sizes) if insert_sizes else 0,
        'median_insert_size': np.median(insert_sizes) if insert_sizes else 0,
    }

    return stats


def check_bam_index(bam_path: str) -> bool:
    """
    Check if BAM file has a valid index.

    Args:
        bam_path: Path to BAM file

    Returns:
        True if indexed, False otherwise

    Example:
        >>> if not check_bam_index('sample.bam'):
        >>>     print("Please index with: samtools index sample.bam")
    """
    index_path = Path(f"{bam_path}.bai")
    return index_path.exists()


def convert_bam_to_cram(
    bam_path: str,
    cram_path: str,
    reference_path: str
) -> bool:
    """
    Convert BAM to CRAM format for better compression.

    Args:
        bam_path: Input BAM file path
        cram_path: Output CRAM file path
        reference_path: Reference genome FASTA path

    Returns:
        True if successful

    Example:
        >>> convert_bam_to_cram('sample.bam', 'sample.cram', 'reference.fa')
    """
    try:
        pysam.view(
            '-C',
            '-T', reference_path,
            '-o', cram_path,
            bam_path,
            catch_stdout=False
        )
        return True
    except Exception as e:
        print(f"Error converting BAM to CRAM: {e}")
        return False
