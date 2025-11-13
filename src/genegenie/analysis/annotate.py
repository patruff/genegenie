"""
Functional Annotation Integration

Tools for integrating functional annotation from SnpEff, VEP, and ClinVar.
Provides Python interfaces for variant effect prediction and clinical significance.
"""

import subprocess
import requests
import time
from cyvcf2 import VCF
import pandas as pd
from typing import Dict, List, Optional, Tuple
from pathlib import Path


def annotate_with_snpeff(
    input_vcf: str,
    output_vcf: str,
    reference: str = 'GRCh38.86',
    snpeff_jar: str = 'snpEff.jar',
    java_mem: str = '8g'
) -> bool:
    """
    Annotate VCF file using SnpEff for effect prediction.

    Args:
        input_vcf: Input VCF file path
        output_vcf: Output annotated VCF file path
        reference: Reference genome version (e.g., 'GRCh38.86')
        snpeff_jar: Path to SnpEff JAR file
        java_mem: Java memory allocation (e.g., '8g')

    Returns:
        True if successful

    Example:
        >>> success = annotate_with_snpeff('variants.vcf.gz', 'annotated.vcf')
    """
    cmd = [
        'java', f'-Xmx{java_mem}', '-jar', snpeff_jar,
        reference,
        input_vcf,
        '-v',  # Verbose
        '-stats', 'snpeff_stats.html',
    ]

    try:
        with open(output_vcf, 'w') as outfile:
            result = subprocess.run(
                cmd,
                stdout=outfile,
                stderr=subprocess.PIPE,
                text=True
            )

        if result.returncode != 0:
            print(f"SnpEff error: {result.stderr}")
            return False

        return True

    except Exception as e:
        print(f"Error running SnpEff: {e}")
        return False


def parse_snpeff_annotations(vcf_path: str) -> pd.DataFrame:
    """
    Parse SnpEff annotations from VCF file.

    Args:
        vcf_path: Path to SnpEff-annotated VCF file

    Returns:
        DataFrame with variant annotations

    Example:
        >>> df = parse_snpeff_annotations('annotated.vcf.gz')
        >>> high_impact = df[df['impact'] == 'HIGH']
    """
    vcf = VCF(vcf_path)

    annotations = []

    for variant in vcf:
        ann = variant.INFO.get('ANN')
        if not ann:
            continue

        # SnpEff ANN field: Allele|Annotation|Impact|Gene|...
        for annotation in ann.split(','):
            fields = annotation.split('|')

            if len(fields) >= 4:
                annotations.append({
                    'chrom': variant.CHROM,
                    'pos': variant.POS,
                    'ref': variant.REF,
                    'alt': variant.ALT[0] if variant.ALT else '.',
                    'allele': fields[0],
                    'annotation': fields[1],
                    'impact': fields[2],
                    'gene': fields[3],
                    'gene_id': fields[4] if len(fields) > 4 else '',
                    'feature_type': fields[5] if len(fields) > 5 else '',
                    'feature_id': fields[6] if len(fields) > 6 else '',
                })

    vcf.close()

    return pd.DataFrame(annotations)


def query_vep_api(
    variants: List[Dict[str, any]],
    species: str = 'human',
    assembly: str = 'GRCh38',
    rate_limit_delay: float = 0.1
) -> List[Dict]:
    """
    Query Ensembl VEP REST API for variant annotations.

    Args:
        variants: List of dicts with 'chrom', 'pos', 'ref', 'alt' keys
        species: Species name (default: 'human')
        assembly: Genome assembly (default: 'GRCh38')
        rate_limit_delay: Delay between requests in seconds

    Returns:
        List of annotation dictionaries

    Example:
        >>> variants = [{'chrom': '19', 'pos': 44908684, 'ref': 'C', 'alt': 'T'}]
        >>> results = query_vep_api(variants)
    """
    server = "https://rest.ensembl.org"
    endpoint = f"/vep/{species}/region"

    # Format variants for API
    variant_strings = []
    for v in variants:
        # Format: "chrom start end alleles strand"
        var_str = f"{v['chrom']} {v['pos']} {v['pos']} {v['ref']}/{v['alt']} +"
        variant_strings.append(var_str)

    headers = {"Content-Type": "application/json"}
    data = {"variants": variant_strings}

    try:
        response = requests.post(
            f"{server}{endpoint}",
            headers=headers,
            json=data
        )

        time.sleep(rate_limit_delay)  # Rate limiting

        if response.ok:
            return response.json()
        else:
            print(f"VEP API error: {response.status_code}")
            return []

    except Exception as e:
        print(f"Error querying VEP API: {e}")
        return []


def run_vep_local(
    input_vcf: str,
    output_vcf: str,
    assembly: str = 'GRCh38',
    cache_dir: Optional[str] = None
) -> bool:
    """
    Run VEP locally (requires VEP installation).

    Args:
        input_vcf: Input VCF file path
        output_vcf: Output VCF file path
        assembly: Genome assembly
        cache_dir: Path to VEP cache directory

    Returns:
        True if successful

    Example:
        >>> run_vep_local('variants.vcf.gz', 'annotated.vcf', assembly='GRCh38')
    """
    cmd = [
        'vep',
        '--input_file', input_vcf,
        '--output_file', output_vcf,
        '--format', 'vcf',
        '--vcf',
        '--force_overwrite',
        '--assembly', assembly,
        '--cache',
        '--merged',
        '--everything',
    ]

    if cache_dir:
        cmd.extend(['--dir_cache', cache_dir])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"VEP error: {result.stderr}")
            return False

        return True

    except Exception as e:
        print(f"Error running VEP: {e}")
        return False


def load_clinvar_database(clinvar_vcf: str) -> Dict:
    """
    Load ClinVar variants into searchable structure.

    Args:
        clinvar_vcf: Path to ClinVar VCF file

    Returns:
        Dictionary mapping (chrom, pos, ref) to clinical information

    Example:
        >>> clinvar_db = load_clinvar_database('clinvar.vcf.gz')
        >>> variant_key = ('chr19', 44908684, 'C')
        >>> if variant_key in clinvar_db:
        >>>     print(clinvar_db[variant_key]['significance'])
    """
    vcf = VCF(clinvar_vcf)
    clinvar_db = {}

    for variant in vcf:
        key = (variant.CHROM, variant.POS, variant.REF)

        # Extract clinical significance
        clnsig = variant.INFO.get('CLNSIG')
        clndn = variant.INFO.get('CLNDN')  # Disease name
        clnrevstat = variant.INFO.get('CLNREVSTAT')  # Review status

        clinvar_db[key] = {
            'significance': clnsig,
            'disease': clndn,
            'review_status': clnrevstat,
            'alts': variant.ALT,
        }

    vcf.close()

    return clinvar_db


def annotate_with_clinvar(
    sample_vcf: str,
    clinvar_db: Dict
) -> pd.DataFrame:
    """
    Annotate personal variants with ClinVar data.

    Args:
        sample_vcf: Path to personal VCF file
        clinvar_db: ClinVar database from load_clinvar_database()

    Returns:
        DataFrame with pathogenic/likely pathogenic variants

    Example:
        >>> clinvar_db = load_clinvar_database('clinvar.vcf.gz')
        >>> pathogenic = annotate_with_clinvar('my_genome.vcf.gz', clinvar_db)
        >>> print(pathogenic[pathogenic['significance'].str.contains('Pathogenic')])
    """
    vcf = VCF(sample_vcf)

    pathogenic_variants = []

    for variant in vcf:
        key = (variant.CHROM, variant.POS, variant.REF)

        if key in clinvar_db:
            clinvar_data = clinvar_db[key]

            # Check if genotype has alt allele
            gt = variant.genotypes[0]
            if gt[0] > 0 or gt[1] > 0:  # Has alt allele
                pathogenic_variants.append({
                    'chrom': variant.CHROM,
                    'position': variant.POS,
                    'ref': variant.REF,
                    'alt': ','.join(variant.ALT) if variant.ALT else '.',
                    'genotype': f"{gt[0]}/{gt[1]}",
                    'significance': clinvar_data['significance'],
                    'disease': clinvar_data['disease'],
                    'review_status': clinvar_data['review_status'],
                })

    vcf.close()

    return pd.DataFrame(pathogenic_variants)


def filter_high_impact_variants(annotated_vcf: str) -> pd.DataFrame:
    """
    Extract high-impact variants from SnpEff-annotated VCF.

    Args:
        annotated_vcf: Path to SnpEff-annotated VCF file

    Returns:
        DataFrame with high-impact variants

    Example:
        >>> high_impact = filter_high_impact_variants('annotated.vcf.gz')
        >>> print(f"Found {len(high_impact)} high-impact variants")
    """
    df = parse_snpeff_annotations(annotated_vcf)

    # Filter for high impact
    high_impact = df[df['impact'].isin(['HIGH', 'MODERATE'])]

    # Sort by impact
    impact_order = {'HIGH': 0, 'MODERATE': 1}
    high_impact['impact_rank'] = high_impact['impact'].map(impact_order)
    high_impact = high_impact.sort_values('impact_rank')

    return high_impact


def get_gene_annotations(
    vcf_path: str,
    gene_list: List[str]
) -> pd.DataFrame:
    """
    Extract all annotations for specific genes.

    Args:
        vcf_path: Path to annotated VCF file
        gene_list: List of gene symbols

    Returns:
        DataFrame with variants in specified genes

    Example:
        >>> genes = ['APOE', 'FOXO3', 'TP53']
        >>> annotations = get_gene_annotations('annotated.vcf.gz', genes)
    """
    df = parse_snpeff_annotations(vcf_path)

    # Filter for target genes
    gene_set = set(gene_list)
    gene_variants = df[df['gene'].isin(gene_set)]

    return gene_variants


def calculate_annotation_summary(vcf_path: str) -> Dict:
    """
    Calculate summary statistics from annotated VCF.

    Args:
        vcf_path: Path to SnpEff-annotated VCF file

    Returns:
        Dictionary with annotation summary

    Example:
        >>> summary = calculate_annotation_summary('annotated.vcf.gz')
        >>> print(f"High impact variants: {summary['high_impact_count']}")
    """
    df = parse_snpeff_annotations(vcf_path)

    summary = {
        'total_annotations': len(df),
        'unique_variants': df.groupby(['chrom', 'pos']).ngroups,
        'high_impact_count': len(df[df['impact'] == 'HIGH']),
        'moderate_impact_count': len(df[df['impact'] == 'MODERATE']),
        'low_impact_count': len(df[df['impact'] == 'LOW']),
        'modifier_impact_count': len(df[df['impact'] == 'MODIFIER']),
        'affected_genes': df['gene'].nunique(),
        'top_consequences': df['annotation'].value_counts().head(10).to_dict(),
    }

    return summary
