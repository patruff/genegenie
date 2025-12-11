# GeneGenie - Whole Genome Sequencing Analysis Toolkit

A comprehensive Python toolkit for analyzing 30x whole genome sequencing (WGS) data with focus on longevity, personality, cognition, behavior, and addiction genetics.

## Overview

GeneGenie provides optimized workflows for analyzing WGS data from Sequencing.com and other providers, leveraging high-performance libraries like cyvcf2, pysam, and BioPython to handle billions of genomic variants efficiently. Now includes comprehensive trait analysis and PDF parsing for extracting SNPs from research papers.

## Features

### Genomic Analysis
- **Longevity Variant Analysis**: Query and analyze validated longevity-associated variants (APOE, FOXO3, CDKN2B, etc.)
- **Comprehensive Trait Analysis**: 100+ SNPs across personality, cognition, behavior, addiction, and physical traits
- **APOE Genotyping**: Determine ε2/ε3/ε4 alleles and associated Alzheimer's risk
- **Polygenic Scoring**: Calculate weighted scores from multiple genetic markers
- **High-Performance Processing**: Leverages cyvcf2 (168x faster than PyVCF) for VCF analysis

### Trait Categories Analyzed
- **Cognition**: Intelligence, memory, processing speed
- **Personality**: Big Five traits (neuroticism, extraversion, openness, conscientiousness, agreeableness)
- **Addiction**: Alcohol, nicotine, cannabis, caffeine dependence
- **Behavior**: Risk-taking, sleep patterns, chronotype, aggression
- **Mental Health**: Depression, anxiety, ADHD, schizophrenia risk
- **Physical**: Athletic performance, muscle strength, pain sensitivity
- **Sensory**: Taste perception, smell sensitivity, perfect pitch

### PDF Paper Analysis
- **SNP Extraction**: Automatically extract rsIDs, genes, and positions from research papers
- **Build Custom Databases**: Create SNP libraries from your collection of papers
- **Table Parsing**: Extract GWAS result tables from PDFs
- **Context Extraction**: Get surrounding text for each SNP mention
- **Batch Processing**: Process entire directories of papers

### Technical Features
- **File Format Support**: VCF, BAM, CRAM, FASTQ formats
- **Functional Annotation**: SnpEff, VEP, and ClinVar integration
- **Reproducible Workflows**: Complete environment specifications and logging
- **Memory Efficient**: Stream billions of variants in constant memory

## Installation

### Using Conda (Recommended)

```bash
# Create environment from file
conda env create -f environment.yml
conda activate genegenie

# Or create manually
conda create -n genegenie python=3.11 -c bioconda -c conda-forge \
    pysam cyvcf2 biopython numpy pandas scikit-allel \
    samtools bcftools tabix
```

### Using pip

```bash
pip install -r requirements.txt
```

## Quick Start

### Analyze Longevity Variants

```bash
# Run complete longevity analysis pipeline
python src/genegenie/longevity_analyzer.py data/my_genome.vcf.gz

# Results will be saved to results/ directory
```

### Analyze All Personality & Behavior Traits

```bash
# Run comprehensive trait analysis (100+ SNPs)
python src/genegenie/trait_analyzer.py data/my_genome.vcf.gz

# Results saved to trait_results/ directory
```

### Extract SNPs from Research Papers

```bash
# Extract SNPs from a single paper
python examples/pdf_parser_example.py basic paper.pdf

# Process entire directory of papers
python examples/pdf_parser_example.py directory papers/

# Build custom SNP database from papers
python examples/pdf_parser_example.py database papers/
```

### Extract Specific Variants

```python
from genegenie.analysis.vcf_utils import extract_variants_by_rsid

# Extract APOE variants
variants = extract_variants_by_rsid(
    'data/genome.vcf.gz',
    ['rs7412', 'rs429358']
)

print(f"APOE genotype: {variants}")
```

## Project Structure

```
genegenie/
├── src/genegenie/
│   ├── analysis/          # Core analysis modules
│   │   ├── vcf_utils.py   # VCF file parsing and analysis
│   │   ├── bam_utils.py   # BAM/CRAM alignment analysis
│   │   ├── fastq_utils.py # FASTQ quality control
│   │   └── annotate.py    # Functional annotation integration
│   ├── utils/             # Utility functions
│   │   ├── longevity_db.py # Longevity variant database
│   │   └── performance.py  # Performance optimization helpers
│   └── longevity_analyzer.py # Main analysis pipeline
├── examples/              # Example usage scripts
├── tests/                 # Unit tests
├── data/                  # Data directory (add your VCF files here)
├── requirements.txt       # Python dependencies
└── environment.yml        # Conda environment specification
```

## Data Requirements

This toolkit works with standard genomic file formats:

- **VCF files**: Must be bgzipped and tabix-indexed (.vcf.gz + .vcf.gz.tbi)
- **BAM files**: Must have corresponding .bai index files
- **Reference genome**: GRCh38 (default) or GRCh37
- **Coverage**: Optimized for 30x WGS data

### File Preparation

```bash
# Compress and index VCF file
bgzip -c variants.vcf > variants.vcf.gz
tabix -p vcf variants.vcf.gz

# Index BAM file
samtools index alignment.bam
```

## Key Longevity Variants Analyzed

- **APOE** (rs7412, rs429358): ε2/ε3/ε4 alleles affecting Alzheimer's risk and lifespan
- **FOXO3** (rs2802292, rs2764264): Most replicated longevity association
- **CDKN2B/ANRIL** (rs1063192): 9p21.3 locus associated with centenarian status
- **Additional variants**: 50+ validated longevity-associated SNPs

## Performance

- **VCF Processing**: 168x faster than PyVCF, 6.9x faster than pysam (using cyvcf2)
- **Memory Efficient**: Streaming architecture handles 3 billion variants in constant memory
- **Parallel Processing**: Multi-core support for chromosome-level parallelization
- **Optimized I/O**: Tabix indexing enables millisecond random access

## Requirements

- Python 3.11+
- 8GB+ RAM (64GB+ recommended for full WGS analysis)
- Storage: 100-200GB for 30x WGS data

## Documentation

Detailed documentation is available in the `docs/` directory (coming soon).

## Testing

```bash
# Run unit tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=genegenie tests/
```

## Citation

If you use GeneGenie in your research, please cite:

- cyvcf2: Pedersen BS, Quinlan AR. (2017) PeerJ 5:e4027
- Sequencing.com data format documentation

## License

MIT License - See LICENSE file for details

## Disclaimer

**Important**: This software is for research and informational purposes only. Results should not be used for clinical decision-making without consultation with a qualified genetic counselor or healthcare provider. Genetics accounts for only ~25% of longevity variance - lifestyle factors remain dominant.

## Contributing

Contributions welcome! Please see CONTRIBUTING.md for guidelines.

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/genegenie/issues
- Documentation: See docs/

## Acknowledgments

Built on the excellent work of:
- cyvcf2 (Brent Pedersen)
- pysam (Andreas Heger, et al.)
- BioPython community
- GWAS Catalog and dbSNP teams
