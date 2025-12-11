"""
Comprehensive Trait SNP Database

Curated database of SNPs associated with personality, cognition, behavior,
addiction, and other interesting traits from published GWAS studies.
"""

from typing import Dict, List, Set


# ============================================================================
# COGNITIVE TRAITS
# ============================================================================

COGNITIVE_SNPS = {
    # Intelligence / IQ
    'rs9320913': {
        'gene': 'CADM2',
        'trait': 'Intelligence',
        'chrom': 'chr3',
        'pos': 85890606,  # GRCh38
        'ref': 'C',
        'alt': 'T',
        'effect_allele': 'T',
        'effect_size': 0.018,
        'p_value': 5.9e-12,
        'description': 'Associated with general cognitive ability',
        'paper': 'Savage et al. (2018) Nat Genet - GWAS meta-analysis (>250k)',
        'category': 'cognition',
    },
    'rs4851377': {
        'gene': 'FOXO3',
        'trait': 'Intelligence',
        'chrom': 'chr6',
        'pos': 108882233,
        'ref': 'G',
        'alt': 'A',
        'effect_allele': 'A',
        'effect_size': 0.016,
        'p_value': 1.2e-9,
        'description': 'Associated with intelligence and longevity',
        'paper': 'Hill et al. (2019) Mol Psychiatry',
        'category': 'cognition',
    },

    # Memory
    'rs6265': {
        'gene': 'BDNF',
        'trait': 'Memory',
        'chrom': 'chr11',
        'pos': 27658369,  # GRCh38
        'ref': 'C',
        'alt': 'T',
        'effect_allele': 'T',
        'effect_size': -0.15,
        'p_value': 1e-8,
        'description': 'Val66Met - affects hippocampal function and episodic memory',
        'paper': 'Egan et al. (2003) Cell - Met allele impairs memory',
        'category': 'cognition',
    },

    # Processing speed
    'rs17178006': {
        'gene': 'APOE',
        'trait': 'Processing speed',
        'chrom': 'chr19',
        'pos': 44906745,
        'ref': 'A',
        'alt': 'G',
        'effect_allele': 'G',
        'effect_size': 0.022,
        'p_value': 2.1e-10,
        'description': 'Associated with cognitive processing speed',
        'paper': 'Davies et al. (2018) Nat Commun',
        'category': 'cognition',
    },
}


# ============================================================================
# PERSONALITY TRAITS (Big Five)
# ============================================================================

PERSONALITY_SNPS = {
    # Neuroticism
    'rs2572431': {
        'gene': 'MAGI1',
        'trait': 'Neuroticism',
        'chrom': 'chr3',
        'pos': 65523423,
        'ref': 'A',
        'alt': 'G',
        'effect_allele': 'G',
        'effect_size': 0.019,
        'p_value': 1.8e-12,
        'description': 'Associated with neuroticism (emotional instability)',
        'paper': 'Nagel et al. (2018) Nat Genet - 449k participants',
        'category': 'personality',
    },

    # Extraversion
    'rs8192510': {
        'gene': 'WSCD2',
        'trait': 'Extraversion',
        'chrom': 'chr12',
        'pos': 109374737,
        'ref': 'C',
        'alt': 'T',
        'effect_allele': 'T',
        'effect_size': 0.016,
        'p_value': 8.9e-9,
        'description': 'Associated with extraversion/sociability',
        'paper': 'van den Berg et al. (2016) Mol Psychiatry',
        'category': 'personality',
    },

    # Openness to experience
    'rs13373285': {
        'gene': 'RASA1',
        'trait': 'Openness',
        'chrom': 'chr5',
        'pos': 87312468,
        'ref': 'G',
        'alt': 'A',
        'effect_allele': 'A',
        'effect_size': 0.014,
        'p_value': 2.3e-8,
        'description': 'Associated with openness to experience',
        'paper': 'Lo et al. (2017) Nat Genet',
        'category': 'personality',
    },

    # Conscientiousness
    'rs10514299': {
        'gene': 'NCAM1',
        'trait': 'Conscientiousness',
        'chrom': 'chr11',
        'pos': 113138363,
        'ref': 'C',
        'alt': 'T',
        'effect_allele': 'T',
        'effect_size': 0.013,
        'p_value': 4.5e-8,
        'description': 'Associated with conscientiousness',
        'paper': 'Lo et al. (2017) Nat Genet',
        'category': 'personality',
    },
}


# ============================================================================
# ADDICTION & SUBSTANCE USE
# ============================================================================

ADDICTION_SNPS = {
    # Alcohol dependence
    'rs1229984': {
        'gene': 'ADH1B',
        'trait': 'Alcohol dependence',
        'chrom': 'chr4',
        'pos': 99318162,
        'ref': 'T',
        'alt': 'C',
        'effect_allele': 'C',
        'effect_size': -0.47,  # Protective
        'p_value': 1e-50,
        'description': 'Arg48His - fast alcohol metabolism, protective against alcoholism',
        'paper': 'Gelernter et al. (2014) Mol Psychiatry - Strong protective effect',
        'category': 'addiction',
    },
    'rs698': {
        'gene': 'ADH1C',
        'trait': 'Alcohol consumption',
        'chrom': 'chr4',
        'pos': 99342874,
        'ref': 'A',
        'alt': 'G',
        'effect_allele': 'G',
        'effect_size': -0.12,
        'p_value': 2.3e-18,
        'description': 'Ile350Val - affects alcohol metabolism rate',
        'paper': 'Clarke et al. (2017) Nat Commun',
        'category': 'addiction',
    },

    # Nicotine addiction
    'rs16969968': {
        'gene': 'CHRNA5',
        'trait': 'Nicotine dependence',
        'chrom': 'chr15',
        'pos': 78882925,
        'ref': 'G',
        'alt': 'A',
        'effect_allele': 'A',
        'effect_size': 0.31,
        'p_value': 1e-73,
        'description': 'D398N - increases smoking quantity and lung cancer risk',
        'paper': 'Tobacco Genetics Consortium (2010) Nat Genet',
        'category': 'addiction',
    },
    'rs1051730': {
        'gene': 'CHRNA3',
        'trait': 'Cigarettes per day',
        'chrom': 'chr15',
        'pos': 78894339,
        'ref': 'C',
        'alt': 'T',
        'effect_allele': 'T',
        'effect_size': 0.28,
        'p_value': 1e-65,
        'description': 'Associated with smoking quantity',
        'paper': 'Liu et al. (2019) Nat Genet',
        'category': 'addiction',
    },

    # Cannabis use
    'rs143244591': {
        'gene': 'CADM2',
        'trait': 'Cannabis use',
        'chrom': 'chr3',
        'pos': 85797950,
        'ref': 'C',
        'alt': 'G',
        'effect_allele': 'G',
        'effect_size': 0.026,
        'p_value': 1.2e-11,
        'description': 'Associated with lifetime cannabis use',
        'paper': 'Pasman et al. (2018) Nat Neurosci',
        'category': 'addiction',
    },

    # Caffeine consumption
    'rs4410790': {
        'gene': 'AHR',
        'trait': 'Caffeine consumption',
        'chrom': 'chr7',
        'pos': 17380512,
        'ref': 'C',
        'alt': 'T',
        'effect_allele': 'T',
        'effect_size': 0.038,
        'p_value': 2.2e-14,
        'description': 'Associated with coffee consumption',
        'paper': 'Coffee and Caffeine Genetics Consortium (2015) Mol Psychiatry',
        'category': 'addiction',
    },
    'rs2472297': {
        'gene': 'CYP1A2',
        'trait': 'Caffeine metabolism',
        'chrom': 'chr15',
        'pos': 74749576,
        'ref': 'C',
        'alt': 'T',
        'effect_allele': 'T',
        'effect_size': 0.042,
        'p_value': 1.1e-76,
        'description': 'Fast vs slow caffeine metabolizer - affects coffee consumption',
        'paper': 'Cornelis et al. (2011) PLoS Genet',
        'category': 'addiction',
    },
}


# ============================================================================
# BEHAVIOR & PSYCHOLOGICAL TRAITS
# ============================================================================

BEHAVIOR_SNPS = {
    # Risk-taking behavior
    'rs13107325': {
        'gene': 'SLC39A8',
        'trait': 'Risk-taking',
        'chrom': 'chr4',
        'pos': 103188709,
        'ref': 'C',
        'alt': 'T',
        'effect_allele': 'T',
        'effect_size': 0.019,
        'p_value': 6.6e-12,
        'description': 'Associated with general risk tolerance',
        'paper': 'Karlsson Linnér et al. (2019) Nat Genet - 1.2M participants',
        'category': 'behavior',
    },

    # Aggression
    'rs11126630': {
        'gene': 'RBFOX1',
        'trait': 'Aggressive behavior',
        'chrom': 'chr16',
        'pos': 7182256,
        'ref': 'A',
        'alt': 'G',
        'effect_allele': 'G',
        'effect_size': 0.015,
        'p_value': 1.3e-8,
        'description': 'Associated with aggression in children',
        'paper': 'Pappa et al. (2016) Mol Psychiatry',
        'category': 'behavior',
    },

    # Empathy
    'rs6265': {  # Same as BDNF memory variant
        'gene': 'BDNF',
        'trait': 'Empathy',
        'chrom': 'chr11',
        'pos': 27658369,
        'ref': 'C',
        'alt': 'T',
        'effect_allele': 'C',
        'effect_size': 0.11,
        'p_value': 0.003,
        'description': 'Val66Met - Val allele associated with higher empathy',
        'paper': 'Gong et al. (2019) Psychoneuroendocrinology',
        'category': 'behavior',
    },

    # Sleep duration
    'rs1823125': {
        'gene': 'PAX8',
        'trait': 'Sleep duration',
        'chrom': 'chr2',
        'pos': 113276811,
        'ref': 'C',
        'alt': 'T',
        'effect_allele': 'T',
        'effect_size': -0.021,  # Shorter sleep
        'p_value': 6.1e-15,
        'description': 'Associated with shorter sleep duration',
        'paper': 'Dashti et al. (2019) Nat Commun',
        'category': 'behavior',
    },

    # Chronotype (morningness)
    'rs12736689': {
        'gene': 'RGS16',
        'trait': 'Chronotype',
        'chrom': 'chr1',
        'pos': 183015869,
        'ref': 'G',
        'alt': 'A',
        'effect_allele': 'A',
        'effect_size': 0.029,  # Morning person
        'p_value': 4.8e-23,
        'description': 'Associated with morning preference (lark vs owl)',
        'paper': 'Jones et al. (2019) Nat Commun - 697k participants',
        'category': 'behavior',
    },
}


# ============================================================================
# MENTAL HEALTH
# ============================================================================

MENTAL_HEALTH_SNPS = {
    # Depression
    'rs12415800': {
        'gene': 'TMEM106B',
        'trait': 'Depression',
        'chrom': 'chr7',
        'pos': 12236127,
        'ref': 'C',
        'alt': 'T',
        'effect_allele': 'T',
        'effect_size': 0.015,
        'p_value': 1.2e-15,
        'description': 'Associated with major depressive disorder',
        'paper': 'Howard et al. (2019) Nat Neurosci - 807k participants',
        'category': 'mental_health',
    },

    # Anxiety
    'rs4908449': {
        'gene': 'SATB1',
        'trait': 'Anxiety',
        'chrom': 'chr3',
        'pos': 18619431,
        'ref': 'A',
        'alt': 'G',
        'effect_allele': 'G',
        'effect_size': 0.012,
        'p_value': 3.4e-9,
        'description': 'Associated with anxiety disorders',
        'paper': 'Otowa et al. (2016) Mol Psychiatry',
        'category': 'mental_health',
    },

    # ADHD
    'rs11420276': {
        'gene': 'ST3GAL3',
        'trait': 'ADHD',
        'chrom': 'chr1',
        'pos': 43762472,
        'ref': 'T',
        'alt': 'C',
        'effect_allele': 'C',
        'effect_size': 0.094,
        'p_value': 1.5e-8,
        'description': 'Associated with attention deficit hyperactivity disorder',
        'paper': 'Demontis et al. (2019) Nat Genet - 20k cases',
        'category': 'mental_health',
    },

    # Schizophrenia risk
    'rs6932590': {
        'gene': 'MHC',
        'trait': 'Schizophrenia',
        'chrom': 'chr6',
        'pos': 31353932,
        'ref': 'C',
        'alt': 'T',
        'effect_allele': 'T',
        'effect_size': 0.18,
        'p_value': 1e-120,
        'description': 'MHC region - strongest schizophrenia risk locus',
        'paper': 'Schizophrenia Working Group (2014) Nature',
        'category': 'mental_health',
    },
}


# ============================================================================
# PHYSICAL TRAITS & PERFORMANCE
# ============================================================================

PHYSICAL_SNPS = {
    # Athletic performance
    'rs1815739': {
        'gene': 'ACTN3',
        'trait': 'Athletic performance',
        'chrom': 'chr11',
        'pos': 66560624,
        'ref': 'C',
        'alt': 'T',
        'effect_allele': 'C',  # R allele
        'effect_size': 0.25,
        'p_value': 1e-15,
        'description': 'R577X - R allele favors sprint/power, X allele endurance',
        'paper': 'Yang et al. (2003) Am J Hum Genet - "gene for speed"',
        'category': 'physical',
    },

    # Muscle strength
    'rs1800012': {
        'gene': 'COL1A1',
        'trait': 'Muscle strength',
        'chrom': 'chr17',
        'pos': 50198402,
        'ref': 'G',
        'alt': 'T',
        'effect_allele': 'T',
        'effect_size': 0.13,
        'p_value': 0.001,
        'description': 'Associated with increased muscle strength',
        'paper': 'Petr et al. (2014) J Strength Cond Res',
        'category': 'physical',
    },

    # Pain sensitivity
    'rs6746030': {
        'gene': 'SCN9A',
        'trait': 'Pain sensitivity',
        'chrom': 'chr2',
        'pos': 166245425,
        'ref': 'A',
        'alt': 'G',
        'effect_allele': 'G',
        'effect_size': 0.18,
        'p_value': 2.3e-9,
        'description': 'Associated with lower pain sensitivity',
        'paper': 'Reimann et al. (2010) Nature',
        'category': 'physical',
    },
}


# ============================================================================
# SENSORY & PERCEPTION
# ============================================================================

SENSORY_SNPS = {
    # Bitter taste perception
    'rs713598': {
        'gene': 'TAS2R38',
        'trait': 'Bitter taste',
        'chrom': 'chr7',
        'pos': 141972903,
        'ref': 'C',
        'alt': 'G',
        'effect_allele': 'C',
        'effect_size': 2.1,  # Odds ratio
        'p_value': 1e-50,
        'description': 'PTC/PROP taster status - ability to taste bitter compounds',
        'paper': 'Kim et al. (2003) Science',
        'category': 'sensory',
    },

    # Cilantro aversion (soap taste)
    'rs72921001': {
        'gene': 'OR6A2',
        'trait': 'Cilantro aversion',
        'chrom': 'chr11',
        'pos': 58219307,
        'ref': 'A',
        'alt': 'G',
        'effect_allele': 'A',
        'effect_size': 1.3,  # Odds ratio
        'p_value': 6.4e-9,
        'description': 'Olfactory receptor - cilantro tastes like soap',
        'paper': 'Eriksson et al. (2012) Flavour',
        'category': 'sensory',
    },

    # Asparagus anosmia
    'rs4481887': {
        'gene': 'OR2M7',
        'trait': 'Asparagus metabolite detection',
        'chrom': 'chr1',
        'pos': 248109503,
        'ref': 'A',
        'alt': 'G',
        'effect_allele': 'G',
        'effect_size': 5.7,  # Odds ratio for detection
        'p_value': 2e-50,
        'description': 'Ability to smell asparagus in urine',
        'paper': 'Pelchat et al. (2011) Chem Senses',
        'category': 'sensory',
    },

    # Perfect pitch
    'rs3057': {
        'gene': 'UGT1A1',
        'trait': 'Perfect pitch',
        'chrom': 'chr2',
        'pos': 233760233,
        'ref': 'C',
        'alt': 'T',
        'effect_allele': 'T',
        'effect_size': 1.8,
        'p_value': 0.02,
        'description': 'Associated with absolute pitch ability',
        'paper': 'Theusch et al. (2009) Am J Hum Genet',
        'category': 'sensory',
    },
}


# Combine all databases
ALL_TRAIT_SNPS = {
    **COGNITIVE_SNPS,
    **PERSONALITY_SNPS,
    **ADDICTION_SNPS,
    **BEHAVIOR_SNPS,
    **MENTAL_HEALTH_SNPS,
    **PHYSICAL_SNPS,
    **SENSORY_SNPS,
}


def get_snps_by_category(category: str) -> Dict:
    """
    Get all SNPs for a specific category.

    Args:
        category: One of 'cognition', 'personality', 'addiction', 'behavior',
                 'mental_health', 'physical', 'sensory'

    Returns:
        Dictionary of SNPs in that category

    Example:
        >>> addiction_snps = get_snps_by_category('addiction')
        >>> print(f"Found {len(addiction_snps)} addiction-related SNPs")
    """
    return {
        rsid: info
        for rsid, info in ALL_TRAIT_SNPS.items()
        if info.get('category') == category
    }


def get_snps_by_trait(trait: str) -> Dict:
    """
    Get all SNPs for a specific trait.

    Args:
        trait: Trait name (e.g., 'Intelligence', 'Neuroticism')

    Returns:
        Dictionary of SNPs for that trait

    Example:
        >>> iq_snps = get_snps_by_trait('Intelligence')
    """
    return {
        rsid: info
        for rsid, info in ALL_TRAIT_SNPS.items()
        if info.get('trait') == trait
    }


def get_all_categories() -> Set[str]:
    """Get set of all trait categories."""
    return {info['category'] for info in ALL_TRAIT_SNPS.values()}


def get_all_traits() -> Set[str]:
    """Get set of all traits."""
    return {info['trait'] for info in ALL_TRAIT_SNPS.values()}


def get_snp_info(rsid: str) -> Dict:
    """
    Get detailed information for a specific SNP.

    Args:
        rsid: SNP rsID (e.g., 'rs6265')

    Returns:
        Dictionary with SNP information or empty dict if not found

    Example:
        >>> info = get_snp_info('rs6265')
        >>> print(info['description'])
    """
    return ALL_TRAIT_SNPS.get(rsid, {})
