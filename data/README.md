# Data Directory

This directory is for storing genomic data files.

## File Types

Place your genomic data files here:

- **VCF files**: `*.vcf.gz` (must be bgzipped and indexed with tabix)
- **BAM files**: `*.bam` (must have corresponding `.bam.bai` index)
- **FASTQ files**: `*.fastq.gz` (can be gzipped)
- **Reference genomes**: `*.fa`, `*.fasta`

## Important Notes

⚠️ **DO NOT commit actual genomic data to git!** ⚠️

- Genomic data files are excluded via `.gitignore`
- These files can be very large (100-200GB for 30x WGS)
- Personal genomic data is sensitive and should be kept private

## Example Data

To test GeneGenie with example data:

1. Download test VCF from 1000 Genomes Project
2. Or use Genome in a Bottle (GIAB) reference samples
3. Or request test data from Sequencing.com

## Data Preparation

Before using your data with GeneGenie:

```bash
# Compress and index VCF
bgzip -c variants.vcf > variants.vcf.gz
tabix -p vcf variants.vcf.gz

# Index BAM file
samtools index alignment.bam
```

## Recommended Data Structure

```
data/
├── sample1/
│   ├── sample1.vcf.gz
│   ├── sample1.vcf.gz.tbi
│   ├── sample1.bam
│   └── sample1.bam.bai
├── sample2/
│   └── ...
└── reference/
    └── GRCh38.fa
```
