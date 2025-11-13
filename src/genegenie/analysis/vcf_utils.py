"""
VCF File Utilities

High-performance tools for parsing and analyzing VCF files using cyvcf2.
Optimized for handling billions of variants in whole genome sequencing data.
"""

from cyvcf2 import VCF, Writer
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Set
from pathlib import Path


def extract_variants_by_rsid(
    vcf_path: str,
    rsids: List[str],
    require_all: bool = False
) -> Dict[str, Dict]:
    """
    Extract specific variants by rsID from VCF file.

    Args:
        vcf_path: Path to bgzipped and indexed VCF file
        rsids: List of rsIDs to extract (e.g., ['rs7412', 'rs429358'])
        require_all: If True, raise error if any rsID not found

    Returns:
        Dictionary mapping rsID to variant information

    Example:
        >>> variants = extract_variants_by_rsid('genome.vcf.gz', ['rs7412'])
        >>> print(variants['rs7412']['genotype'])
    """
    vcf = VCF(vcf_path)
    target_snps = set(rsids)
    results = {}

    for variant in vcf:
        if variant.ID and variant.ID in target_snps:
            gt = variant.genotypes[0]  # Assuming single sample

            results[variant.ID] = {
                'position': f"{variant.CHROM}:{variant.POS}",
                'ref': variant.REF,
                'alt': variant.ALT[0] if variant.ALT else None,
                'genotype': f"{gt[0]}/{gt[1]}",
                'phased': bool(gt[2]),
                'depth': variant.gt_depths[0] if len(variant.gt_depths) > 0 else 0,
                'quality': variant.gt_quals[0] if len(variant.gt_quals) > 0 else 0,
            }

            # Stop early if we found all targets
            if len(results) == len(target_snps):
                break

    vcf.close()

    # Check if all requested variants were found
    if require_all:
        missing = target_snps - set(results.keys())
        if missing:
            raise ValueError(f"Variants not found: {missing}")

    return results


def extract_variants_by_position(
    vcf_path: str,
    positions: List[Tuple[str, int]],
) -> Dict[Tuple[str, int], Dict]:
    """
    Extract variants at specific genomic positions.

    Args:
        vcf_path: Path to bgzipped and indexed VCF file
        positions: List of (chromosome, position) tuples

    Returns:
        Dictionary mapping (chrom, pos) to variant information

    Example:
        >>> positions = [('chr19', 44908684), ('chr19', 44908822)]
        >>> variants = extract_variants_by_position('genome.vcf.gz', positions)
    """
    vcf = VCF(vcf_path)
    results = {}

    for chrom, pos in positions:
        for variant in vcf(f'{chrom}:{pos}-{pos}'):
            gt = variant.genotypes[0]

            results[(chrom, pos)] = {
                'rsid': variant.ID,
                'ref': variant.REF,
                'alt': ','.join(variant.ALT) if variant.ALT else '.',
                'genotype': f"{gt[0]}/{gt[1]}",
                'phased': bool(gt[2]),
                'depth': variant.gt_depths[0] if len(variant.gt_depths) > 0 else 0,
                'quality': variant.gt_quals[0] if len(variant.gt_quals) > 0 else 0,
            }
            break  # Only take first variant at position

    vcf.close()
    return results


def filter_by_quality(
    vcf_path: str,
    output_path: str,
    min_qual: float = 30.0,
    min_depth: int = 10,
    max_depth: Optional[int] = None
) -> int:
    """
    Filter VCF file by quality metrics.

    Args:
        vcf_path: Input VCF file path
        output_path: Output VCF file path
        min_qual: Minimum variant quality score (QUAL field)
        min_depth: Minimum read depth (DP)
        max_depth: Maximum read depth (for filtering PCR duplicates)

    Returns:
        Number of variants passing filters

    Example:
        >>> count = filter_by_quality('raw.vcf.gz', 'filtered.vcf.gz', min_qual=30)
        >>> print(f"Retained {count} high-quality variants")
    """
    vcf = VCF(vcf_path)
    writer = Writer(output_path, vcf)

    passed = 0

    for variant in vcf:
        # Check QUAL
        if variant.QUAL is None or variant.QUAL < min_qual:
            continue

        # Check depth
        depth = variant.INFO.get('DP')
        if depth is None:
            continue

        if depth < min_depth:
            continue

        if max_depth is not None and depth > max_depth:
            continue

        writer.write_record(variant)
        passed += 1

    writer.close()
    vcf.close()

    return passed


def filter_by_gene_list(
    vcf_path: str,
    output_path: str,
    genes: Set[str],
    csq_field: str = 'CSQ'
) -> int:
    """
    Filter VCF to variants in specific genes (requires VEP/SnpEff annotation).

    Args:
        vcf_path: Input VCF file path (must have CSQ or ANN annotation)
        output_path: Output VCF file path
        genes: Set of gene symbols to extract
        csq_field: Annotation field name ('CSQ' for VEP, 'ANN' for SnpEff)

    Returns:
        Number of variants in target genes

    Example:
        >>> genes = {'APOE', 'FOXO3', 'TP53'}
        >>> count = filter_by_gene_list('annotated.vcf.gz', 'genes.vcf.gz', genes)
    """
    vcf = VCF(vcf_path)
    writer = Writer(output_path, vcf)

    passed = 0

    for variant in vcf:
        csq = variant.INFO.get(csq_field)
        if not csq:
            continue

        # Parse annotation field
        found = False
        for transcript in csq.split(','):
            fields = transcript.split('|')
            # Gene symbol is typically at index 3 for VEP
            if len(fields) > 3:
                gene_symbol = fields[3]
                if gene_symbol in genes:
                    found = True
                    break

        if found:
            writer.write_record(variant)
            passed += 1

    writer.close()
    vcf.close()

    return passed


def filter_by_region(
    vcf_path: str,
    output_path: str,
    regions: List[Tuple[str, int, int]]
) -> int:
    """
    Extract variants in specific genomic regions.

    Args:
        vcf_path: Input VCF file path (must be indexed)
        output_path: Output VCF file path
        regions: List of (chromosome, start, end) tuples

    Returns:
        Number of variants in regions

    Example:
        >>> # Extract APOE region (chr19: 44.9-45.0 Mb)
        >>> regions = [('chr19', 44900000, 45000000)]
        >>> count = filter_by_region('genome.vcf.gz', 'apoe.vcf.gz', regions)
    """
    vcf = VCF(vcf_path)
    writer = Writer(output_path, vcf)

    passed = 0

    for chrom, start, end in regions:
        for variant in vcf(f'{chrom}:{start}-{end}'):
            writer.write_record(variant)
            passed += 1

    writer.close()
    vcf.close()

    return passed


def count_variants(vcf_path: str, by_chromosome: bool = False) -> Dict:
    """
    Count variants in VCF file.

    Args:
        vcf_path: Input VCF file path
        by_chromosome: If True, return counts per chromosome

    Returns:
        Dictionary with variant counts

    Example:
        >>> stats = count_variants('genome.vcf.gz', by_chromosome=True)
        >>> print(f"Chr1 has {stats['chr1']} variants")
    """
    vcf = VCF(vcf_path)

    if by_chromosome:
        counts = {}
        for variant in vcf:
            chrom = variant.CHROM
            counts[chrom] = counts.get(chrom, 0) + 1
    else:
        total = sum(1 for _ in vcf)
        counts = {'total': total}

    vcf.close()
    return counts


def calculate_variant_statistics(vcf_path: str, sample_size: int = 10000) -> Dict:
    """
    Calculate comprehensive statistics from VCF file.

    Args:
        vcf_path: Input VCF file path
        sample_size: Number of variants to sample for stats

    Returns:
        Dictionary with statistics

    Example:
        >>> stats = calculate_variant_statistics('genome.vcf.gz')
        >>> print(f"Mean depth: {stats['mean_depth']:.1f}x")
    """
    vcf = VCF(vcf_path)

    stats = {
        'total': 0,
        'snps': 0,
        'indels': 0,
        'homozygous_ref': 0,
        'heterozygous': 0,
        'homozygous_alt': 0,
        'qualities': [],
        'depths': [],
    }

    for i, variant in enumerate(vcf):
        if i >= sample_size:
            break

        stats['total'] += 1

        # Classify variant type
        if len(variant.REF) == 1 and all(len(a) == 1 for a in variant.ALT):
            stats['snps'] += 1
        else:
            stats['indels'] += 1

        # Genotype counts (gt_types: 0=HOM_REF, 1=HET, 3=HOM_ALT)
        gt_type = variant.gt_types[0]
        if gt_type == 0:
            stats['homozygous_ref'] += 1
        elif gt_type == 1:
            stats['heterozygous'] += 1
        elif gt_type == 3:
            stats['homozygous_alt'] += 1

        # Quality metrics
        if variant.QUAL is not None:
            stats['qualities'].append(variant.QUAL)

        depths = variant.gt_depths[variant.gt_depths >= 0]
        if len(depths) > 0:
            stats['depths'].append(np.mean(depths))

    vcf.close()

    # Calculate summary statistics
    summary = {
        'total_sampled': stats['total'],
        'snp_count': stats['snps'],
        'indel_count': stats['indels'],
        'snp_ratio': stats['snps'] / stats['total'] if stats['total'] > 0 else 0,
        'het_ratio': stats['heterozygous'] / stats['total'] if stats['total'] > 0 else 0,
        'mean_quality': np.mean(stats['qualities']) if stats['qualities'] else 0,
        'median_quality': np.median(stats['qualities']) if stats['qualities'] else 0,
        'mean_depth': np.mean(stats['depths']) if stats['depths'] else 0,
        'median_depth': np.median(stats['depths']) if stats['depths'] else 0,
    }

    return summary


def get_apoe_genotype(vcf_path: str) -> Optional[str]:
    """
    Determine APOE ε2/ε3/ε4 genotype from rs7412 and rs429358.

    Args:
        vcf_path: Input VCF file path (must be indexed)

    Returns:
        APOE genotype string (e.g., 'ε3/ε3') or None if variants not found

    Example:
        >>> apoe = get_apoe_genotype('genome.vcf.gz')
        >>> print(f"APOE status: {apoe}")
    """
    # APOE SNP positions on chr19 (GRCh38)
    positions = {
        'rs7412': ('chr19', 44908684),
        'rs429358': ('chr19', 44908822),
    }

    variants = extract_variants_by_position(vcf_path, list(positions.values()))

    if len(variants) != 2:
        return None

    # Get genotypes
    gt_7412 = variants[positions['rs7412']]['genotype'].split('/')
    gt_429358 = variants[positions['rs429358']]['genotype'].split('/')

    # Decode APOE alleles
    # rs7412: T=ε2, C=ε3/ε4
    # rs429358: T=ε2/ε3, C=ε4
    alleles = []
    for a1, a2 in zip(gt_7412, gt_429358):
        a1, a2 = int(a1), int(a2)
        if a1 == 1 and a2 == 0:  # T/T
            alleles.append('ε2')
        elif a1 == 0 and a2 == 0:  # C/T
            alleles.append('ε3')
        elif a1 == 0 and a2 == 1:  # C/C
            alleles.append('ε4')
        else:
            alleles.append('?')

    return '/'.join(sorted(alleles))


def create_variant_bed(vcf_path: str, output_path: str) -> None:
    """
    Convert VCF to BED format for variant positions.

    Args:
        vcf_path: Input VCF file
        output_path: Output BED file path

    Example:
        >>> create_variant_bed('variants.vcf.gz', 'variants.bed')
    """
    vcf = VCF(vcf_path)

    with open(output_path, 'w') as bed:
        bed.write("# chrom\tstart\tend\tname\n")

        for variant in vcf:
            # BED is 0-based, VCF is 1-based
            start = variant.POS - 1
            end = variant.POS
            name = variant.ID if variant.ID else f"{variant.CHROM}:{variant.POS}"

            bed.write(f"{variant.CHROM}\t{start}\t{end}\t{name}\n")

    vcf.close()
