"""
Longevity Variant Database

Curated database of validated longevity-associated genetic variants.
Based on published GWAS, LongevityMap, and meta-analyses.
"""

from typing import Dict, List, Set


# Comprehensive longevity variant panel
LONGEVITY_PANEL = {
    # APOE - Strongest longevity association
    'rs7412': {
        'gene': 'APOE',
        'chrom': 'chr19',
        'pos': 44908684,  # GRCh38
        'ref': 'C',
        'alt': 'T',
        'protective_allele': 'T',
        'risk_allele': 'C',
        'effect_size': 0.15,
        'description': 'APOE ε2 allele (rs7412 position 112) - protective against AD',
        'evidence': 'Meta-analysis of 100+ studies',
        'population': 'Multi-ethnic',
    },
    'rs429358': {
        'gene': 'APOE',
        'chrom': 'chr19',
        'pos': 44908822,  # GRCh38
        'ref': 'T',
        'alt': 'C',
        'protective_allele': 'T',
        'risk_allele': 'C',
        'effect_size': -0.20,
        'description': 'APOE ε4 allele (rs429358 position 158) - AD risk',
        'evidence': 'Meta-analysis of 100+ studies',
        'population': 'Multi-ethnic',
    },

    # FOXO3 - Most replicated longevity gene
    'rs2802292': {
        'gene': 'FOXO3',
        'chrom': 'chr6',
        'pos': 108878242,  # GRCh38
        'ref': 'T',
        'alt': 'G',
        'protective_allele': 'G',
        'risk_allele': 'T',
        'effect_size': 0.30,
        'description': 'FOXO3 primary longevity variant - 2.8x odds reaching 95',
        'evidence': 'Replicated in 15+ populations including Japanese, European',
        'population': 'Multi-ethnic',
    },
    'rs2764264': {
        'gene': 'FOXO3',
        'chrom': 'chr6',
        'pos': 108882233,  # GRCh38
        'ref': 'C',
        'alt': 'T',
        'protective_allele': 'T',
        'risk_allele': 'C',
        'effect_size': 0.18,
        'description': 'FOXO3 secondary longevity variant in haplotype block',
        'evidence': 'Multiple GWAS',
        'population': 'European',
    },
    'rs13217795': {
        'gene': 'FOXO3',
        'chrom': 'chr6',
        'pos': 108885078,  # GRCh38
        'ref': 'C',
        'alt': 'T',
        'protective_allele': 'T',
        'risk_allele': 'C',
        'effect_size': 0.16,
        'description': 'FOXO3 additional longevity variant',
        'evidence': 'LongevityMap',
        'population': 'European',
    },

    # CDKN2B/ANRIL - 9p21.3 locus
    'rs1063192': {
        'gene': 'CDKN2B',
        'chrom': 'chr9',
        'pos': 22124094,  # GRCh38
        'ref': 'G',
        'alt': 'A',
        'protective_allele': 'A',
        'risk_allele': 'G',
        'effect_size': 0.12,
        'description': 'CDKN2B/ANRIL locus - centenarian association',
        'evidence': 'Multiple GWAS',
        'population': 'European',
    },

    # Additional validated longevity loci
    'rs4420638': {
        'gene': 'APOC1',
        'chrom': 'chr19',
        'pos': 44907832,  # GRCh38
        'ref': 'A',
        'alt': 'G',
        'protective_allele': 'A',
        'risk_allele': 'G',
        'effect_size': 0.10,
        'description': 'APOC1 - associated with longevity, near APOE',
        'evidence': 'GWAS',
        'population': 'European',
    },

    'rs2542052': {
        'gene': 'PHOX2B',
        'chrom': 'chr4',
        'pos': 41745086,  # GRCh38
        'ref': 'T',
        'alt': 'C',
        'protective_allele': 'C',
        'risk_allele': 'T',
        'effect_size': 0.08,
        'description': 'PHOX2B region - parental lifespan GWAS',
        'evidence': 'UK Biobank GWAS',
        'population': 'European',
    },

    # Add more variants as needed
}


# Gene-level information
LONGEVITY_GENES = {
    'APOE': {
        'full_name': 'Apolipoprotein E',
        'function': 'Lipid metabolism, neuronal repair',
        'pathway': 'Cholesterol homeostasis',
        'evidence_level': 'Very strong',
        'key_variants': ['rs7412', 'rs429358', 'rs4420638'],
    },
    'FOXO3': {
        'full_name': 'Forkhead box O3',
        'function': 'Transcription factor regulating stress resistance',
        'pathway': 'Insulin/IGF-1 signaling, oxidative stress response',
        'evidence_level': 'Very strong',
        'key_variants': ['rs2802292', 'rs2764264', 'rs13217795'],
    },
    'CDKN2B': {
        'full_name': 'Cyclin-dependent kinase inhibitor 2B',
        'function': 'Cell cycle regulation, senescence',
        'pathway': 'Cell cycle control, p16/p15 pathway',
        'evidence_level': 'Strong',
        'key_variants': ['rs1063192'],
    },
    'TP53': {
        'full_name': 'Tumor protein p53',
        'function': 'Tumor suppressor, DNA damage response',
        'pathway': 'Apoptosis, cell cycle arrest',
        'evidence_level': 'Moderate',
        'key_variants': [],
    },
    'IGF1R': {
        'full_name': 'Insulin-like growth factor 1 receptor',
        'function': 'Growth and metabolism regulation',
        'pathway': 'Insulin/IGF-1 signaling',
        'evidence_level': 'Moderate',
        'key_variants': [],
    },
    'SIRT1': {
        'full_name': 'Sirtuin 1',
        'function': 'NAD-dependent deacetylase',
        'pathway': 'Caloric restriction mimetics, metabolism',
        'evidence_level': 'Moderate',
        'key_variants': [],
    },
    'KLOTHO': {
        'full_name': 'Klotho',
        'function': 'Aging suppressor, mineral homeostasis',
        'pathway': 'FGF23 signaling, calcium/phosphate regulation',
        'evidence_level': 'Moderate',
        'key_variants': [],
    },
}


def get_longevity_variants(genes: List[str] = None) -> Dict:
    """
    Get longevity variants, optionally filtered by gene.

    Args:
        genes: List of gene symbols to filter (None = all variants)

    Returns:
        Dictionary of variants

    Example:
        >>> apoe_variants = get_longevity_variants(['APOE'])
        >>> all_variants = get_longevity_variants()
    """
    if genes is None:
        return LONGEVITY_PANEL

    gene_set = set(genes)
    return {
        rsid: info
        for rsid, info in LONGEVITY_PANEL.items()
        if info['gene'] in gene_set
    }


def get_gene_info(gene: str) -> Dict:
    """
    Get detailed information about a longevity gene.

    Args:
        gene: Gene symbol

    Returns:
        Dictionary with gene information

    Example:
        >>> info = get_gene_info('FOXO3')
        >>> print(info['function'])
    """
    return LONGEVITY_GENES.get(gene, {})


def get_all_longevity_genes() -> Set[str]:
    """
    Get set of all known longevity-associated genes.

    Returns:
        Set of gene symbols

    Example:
        >>> genes = get_all_longevity_genes()
        >>> print(f"Tracking {len(genes)} longevity genes")
    """
    # Combine genes from variant panel and gene database
    panel_genes = {info['gene'] for info in LONGEVITY_PANEL.values()}
    db_genes = set(LONGEVITY_GENES.keys())
    return panel_genes | db_genes


def interpret_apoe_genotype(genotype: str) -> Dict:
    """
    Provide detailed interpretation of APOE genotype.

    Args:
        genotype: APOE genotype string (e.g., 'ε3/ε4')

    Returns:
        Dictionary with interpretation

    Example:
        >>> info = interpret_apoe_genotype('ε3/ε4')
        >>> print(info['ad_risk'])
    """
    interpretations = {
        'ε2/ε2': {
            'ad_risk': 'Very low (~99% reduced risk)',
            'cvd_risk': 'Increased (higher triglycerides)',
            'longevity': 'Favorable (increased lifespan)',
            'frequency': 'Rare (~1%)',
        },
        'ε2/ε3': {
            'ad_risk': 'Reduced (~13% lower)',
            'cvd_risk': 'Low',
            'longevity': 'Slightly favorable',
            'frequency': 'Common (~12%)',
        },
        'ε2/ε4': {
            'ad_risk': 'Mixed effects',
            'cvd_risk': 'Variable',
            'longevity': 'Neutral',
            'frequency': 'Uncommon (~2%)',
        },
        'ε3/ε3': {
            'ad_risk': 'Baseline (reference)',
            'cvd_risk': 'Baseline',
            'longevity': 'Neutral',
            'frequency': 'Very common (~66%)',
        },
        'ε3/ε4': {
            'ad_risk': 'Moderately increased (3-4x)',
            'cvd_risk': 'Slightly increased',
            'longevity': 'Slightly reduced',
            'frequency': 'Common (~24%)',
        },
        'ε4/ε4': {
            'ad_risk': 'Highly increased (12-61x depending on age)',
            'cvd_risk': 'Increased',
            'longevity': 'Reduced',
            'frequency': 'Rare (~2%)',
        },
    }

    return interpretations.get(genotype, {'error': 'Unknown genotype'})


def get_variant_references(rsid: str) -> List[str]:
    """
    Get literature references for a specific variant.

    Args:
        rsid: Variant rsID

    Returns:
        List of reference descriptions

    Example:
        >>> refs = get_variant_references('rs2802292')
        >>> for ref in refs:
        >>>     print(ref)
    """
    references = {
        'rs2802292': [
            'Willcox et al. (2008) PNAS - Original FOXO3 longevity discovery',
            'Flachsbart et al. (2009) PNAS - Replication in German centenarians',
            'Soerensen et al. (2015) Aging Cell - Meta-analysis across populations',
        ],
        'rs7412': [
            'Schachter et al. (1994) Nat Genet - APOE and longevity',
            'Deelen et al. (2014) Aging Cell - Meta-analysis of APOE in longevity',
        ],
        'rs429358': [
            'Corder et al. (1993) Science - APOE ε4 and AD risk',
            'Farrer et al. (1997) JAMA - APOE ε4 dose-response in AD',
        ],
    }

    return references.get(rsid, ['No specific references available'])
