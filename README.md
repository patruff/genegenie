# GeneGenie - Whole Genome Sequencing Analysis Toolkit

A comprehensive Python toolkit for analyzing 30x whole genome sequencing (WGS) data with focus on longevity, personality, cognition, behavior, and addiction genetics.

## Overview

GeneGenie provides optimized workflows for analyzing WGS data from Sequencing.com and other providers, leveraging high-performance libraries like cyvcf2, pysam, and BioPython to handle billions of genomic variants efficiently. Now includes comprehensive trait analysis and PDF parsing for extracting SNPs from research papers.

## Features

### Genomic Analysis
- **Longevity Variant Analysis**: Query and analyze validated longevity-associated variants (APOE, FOXO3, CDKN2B, etc.)
- **Comprehensive Trait Analysis**: 100+ SNPs across personality, cognition, behavior, addiction, and physical traits
- **Interactive Visual Reports**: Beautiful HTML trait cards with genetic score scales and visual indicators
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

### RAG System (MCP Server) 🚀 NEW!
- **Genome Papers RAG**: Query genomics papers with AI using Google's File Search
- **Google Drive Sync**: Automatically sync PDFs from `genomepapers` folder (every 6 hours)
- **Weekly Paper Fetching**: Automated NCBI PubMed search and PDF download (every Monday)
- **Natural Language Queries**: Ask questions about your paper library with AI-powered search
- **Citation Support**: Get AI-generated answers grounded in papers with source citations
- **Separate Store**: Independent from longevitypdf for genome-specific research
- **FREE Storage**: Zero cost for storage and query embeddings (only pay ~$0.002/paper for indexing)
- **Monthly SNP Updates**: Extract new SNPs from papers and update trait database

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

# Results saved to trait_results/ directory:
#   - trait_report.html (interactive visual grid - open in browser!)
#   - trait_genetics_report.md (detailed markdown report)
#   - trait_variants.csv (raw variant data)

# Or use the visual analysis example:
python examples/visual_trait_analysis.py data/my_genome.vcf.gz
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

### Query Papers with AI (RAG System)

```bash
# Setup MCP server in Claude Desktop (see MCP Server Setup below)
# Then in Claude Desktop:

"Upload ~/papers/savage_2018_intelligence.pdf"
"What SNPs are genome-wide significant for intelligence?"
"Which CHRNA5 variants affect nicotine dependence?"
"Compare FOXO3 variants across populations"
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

## 🔄 Monthly Workflow: Growing Your SNP Database

GeneGenie enables a powerful workflow for continuously expanding your trait SNP database:

```mermaid
graph LR
    A[New Papers] --> B[Google Drive genomepapers/]
    B --> C[Auto-sync every 6h]
    C --> D[RAG System]
    D --> E[Query with AI]
    E --> F[Extract SNPs]
    F --> G[Add to trait_db.py]
    G --> H[Re-analyze Genome]
    H --> I[Updated Reports]
```

### Step-by-Step Monthly Update Process

#### 1. **Add New Papers** (Continuous)
```bash
# Option A: Automated Weekly Fetching (Recommended!)
# GitHub Action automatically fetches new papers from NCBI every Monday
# Papers are auto-uploaded to Google Drive genomepapers/ folder
# See WEEKLY_PAPERS_SETUP.md for configuration

# Option B: Upload directly via MCP
# In Claude Desktop: "Upload ~/papers/new_gwas_2024.pdf"

# Option C: Add to Google Drive manually
# Just drop PDFs into your genomepapers/ folder
# Auto-syncs every 6 hours via GitHub Actions
```

#### 2. **Query Papers with AI** (Interactive)
```bash
# In Claude Desktop (via MCP server):
"What new SNPs are associated with intelligence in 2024 papers?"
"List all rs IDs mentioned with p < 5e-8"
"What genes are associated with alcohol dependence?"
```

#### 3. **Extract SNPs from Papers** (Monthly)
```bash
# Extract all SNPs from newly added papers
python examples/pdf_parser_example.py directory papers/

# Or extract from specific paper
python examples/pdf_parser_example.py basic papers/new_gwas.pdf

# Build consolidated database
python examples/pdf_parser_example.py database papers/
# → Outputs: custom_snp_database.json
```

#### 4. **Add SNPs to Trait Database** (Monthly)
```python
# Edit src/genegenie/utils/trait_db.py
# Add new SNPs to appropriate categories:

'rs12345678': {
    'gene': 'NEWGENE',
    'trait': 'Intelligence',
    'chrom': 'chr1',
    'pos': 12345678,
    'ref': 'A',
    'alt': 'G',
    'effect_allele': 'G',
    'effect_size': 0.025,
    'p_value': 3.2e-12,
    'description': 'New GWAS hit from 2024 study',
    'paper': 'Smith et al. (2024) Nat Genet',
    'category': 'cognition',
}
```

#### 5. **Re-analyze Your Genome** (Monthly)
```bash
# Run trait analysis with updated database
python src/genegenie/trait_analyzer.py data/my_genome.vcf.gz

# Compare with previous results to see new insights
diff trait_results/trait_genetics_report.md \
     previous_results/trait_genetics_report.md
```

#### 6. **Track Database Growth** (Monthly)
```python
from genegenie.utils.trait_db import ALL_TRAIT_SNPS, get_all_categories

print(f"Total SNPs: {len(ALL_TRAIT_SNPS)}")
for category in get_all_categories():
    snps = get_snps_by_category(category)
    print(f"{category}: {len(snps)} SNPs")
```

### Example Monthly Update

```bash
# January 2025: Start with 100 SNPs
# Add 5 new GWAS papers to genomepapers/ folder
# Wait for auto-sync or manually upload

# Query RAG system
# → "What are the newest intelligence SNPs from 2024?"
# → AI returns: rs999888, rs777666, rs555444

# Extract and add to trait_db.py
# Re-run analysis
python src/genegenie/trait_analyzer.py data/genome.vcf.gz

# Now have 105 SNPs, updated intelligence score!
```

## Project Structure

```
genegenie/
├── src/genegenie/
│   ├── analysis/             # Core analysis modules
│   │   ├── vcf_utils.py      # VCF file parsing and analysis
│   │   ├── bam_utils.py      # BAM/CRAM alignment analysis
│   │   ├── fastq_utils.py    # FASTQ quality control
│   │   ├── annotate.py       # Functional annotation integration
│   │   └── pdf_parser.py     # PDF SNP extraction
│   ├── visualization/        # Interactive visualizations
│   │   ├── trait_visualizer.py # HTML trait grid generator
│   │   └── __init__.py       # Visualization module
│   ├── utils/                # Utility functions
│   │   ├── longevity_db.py   # Longevity variant database
│   │   ├── trait_db.py       # Trait SNP database (100+ SNPs)
│   │   └── performance.py    # Performance optimization helpers
│   ├── longevity_analyzer.py # Main longevity analysis pipeline
│   └── trait_analyzer.py     # Comprehensive trait analysis
├── mcp_server/               # RAG system (MCP server)
│   ├── genome_papers_mcp.py  # MCP server for querying papers
│   ├── sync_genome_drive_pdfs.py # Google Drive sync script
│   ├── requirements.txt      # MCP dependencies
│   └── README.md             # MCP server documentation
├── examples/                 # Example usage scripts
│   ├── basic_vcf_analysis.py
│   ├── longevity_analysis_example.py
│   ├── trait_analysis_example.py
│   ├── visual_trait_analysis.py # Interactive HTML visualization
│   ├── pdf_parser_example.py
│   └── performance_example.py
├── tests/                    # Unit tests
├── data/                     # Data directory (add your VCF files here)
├── papers/                   # Research papers directory
├── .github/workflows/        # GitHub Actions
│   ├── sync_genome_drive_pdfs.yml # Auto-sync every 6 hours
│   └── fetch_weekly_papers.yml    # Fetch papers from NCBI weekly
├── fetch_weekly_papers.py    # Weekly NCBI paper fetcher script
├── WEEKLY_PAPERS_SETUP.md    # Setup guide for weekly fetching
├── requirements.txt          # Python dependencies
└── environment.yml           # Conda environment specification
```

## MCP Server Setup (RAG System)

The Genome Papers RAG system allows you to query your research papers using AI.

### 1. Install MCP Dependencies

```bash
pip install -r mcp_server/requirements.txt
```

### 2. Get Google GenAI API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Click "Create API Key" (free!)
3. Copy your API key

### 3. Configure Claude Desktop

Add to your Claude Desktop config:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "genome-papers": {
      "command": "python",
      "args": ["/absolute/path/to/genegenie/mcp_server/genome_papers_mcp.py"],
      "env": {
        "GOOGLE_GENAI_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### 4. Setup Google Drive Auto-Sync (Optional)

1. Create `genomepapers` folder in Google Drive
2. Get service account credentials (see [MCP README](mcp_server/README.md))
3. Share folder with service account
4. Add GitHub secrets:
   - `GOOGLE_GENAI_API_KEY`
   - `GOOGLE_DRIVE_CREDENTIALS`

Papers will auto-sync every 6 hours! 🎉

### 5. Start Querying

In Claude Desktop:
```
Upload ~/papers/gwas_intelligence.pdf
What SNPs are genome-wide significant for intelligence?
List all CHRNA5 variants mentioned
```

See [mcp_server/README.md](mcp_server/README.md) for full documentation.

## Data Requirements

This toolkit works with standard genomic file formats:

- **VCF files**: Must be bgzipped and tabix-indexed (.vcf.gz + .vcf.gz.tbi)
- **BAM files**: Must have corresponding .bai index files
- **Reference genome**: GRCh38 (default) or GRCh37
- **Coverage**: Optimized for 30x WGS data
- **Research Papers**: PDFs of GWAS studies, SNP papers, trait genetics research

### File Preparation

```bash
# Compress and index VCF file
bgzip -c variants.vcf > variants.vcf.gz
tabix -p vcf variants.vcf.gz

# Index BAM file
samtools index alignment.bam
```

## Key Variants Analyzed

### Longevity (50+ SNPs)
- **APOE** (rs7412, rs429358): ε2/ε3/ε4 alleles affecting Alzheimer's risk and lifespan
- **FOXO3** (rs2802292, rs2764264): Most replicated longevity association
- **CDKN2B/ANRIL** (rs1063192): 9p21.3 locus associated with centenarian status

### Cognition & IQ (4+ SNPs)
- **CADM2** (rs9320913): General cognitive ability
- **BDNF** (rs6265): Val66Met - memory and cognition

### Personality (4+ SNPs)
- **MAGI1** (rs2572431): Neuroticism
- **WSCD2** (rs8192510): Extraversion

### Addiction (7+ SNPs)
- **ADH1B** (rs1229984): Alcohol dependence (strong protective)
- **CHRNA5** (rs16969968): Nicotine dependence
- **CYP1A2** (rs2472297): Caffeine metabolism

### Physical Traits (3+ SNPs)
- **ACTN3** (rs1815739): "Gene for speed" (sprint vs endurance)
- **SCN9A** (rs6746030): Pain sensitivity

### Sensory (4+ SNPs)
- **TAS2R38** (rs713598): Bitter taste perception
- **OR6A2** (rs72921001): Cilantro aversion

**Total: 100+ validated SNPs** - Database growing monthly via paper RAG system!

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

## Workflow Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    GeneGenie Workflow                        │
└─────────────────────────────────────────────────────────────┘

1. 📚 Add Papers
   └─> AUTOMATED: GitHub Action fetches new papers weekly from NCBI
   └─> OR: Drop PDFs into Google Drive genomepapers/ folder
   └─> Auto-sync every 6 hours to RAG system

2. 🤖 Query with AI
   └─> Ask questions in Claude Desktop via MCP server
   └─> "What SNPs are significant for intelligence?"
   └─> Get AI answers with citations

3. 🧬 Extract SNPs
   └─> python examples/pdf_parser_example.py directory papers/
   └─> Get all rsIDs, genes, p-values from papers

4. 📝 Update Database
   └─> Add new SNPs to src/genegenie/utils/trait_db.py
   └─> Include effect sizes, descriptions, papers

5. 🔬 Analyze Genome
   └─> python src/genegenie/trait_analyzer.py data/genome.vcf.gz
   └─> Get updated trait scores with new SNPs

6. 📊 Compare Results
   └─> Track how your genetic understanding evolves
   └─> Monthly updates as new GWAS papers published

🔄 Repeat monthly for continuously growing insights!
```

## Acknowledgments

Built on the excellent work of:
- cyvcf2 (Brent Pedersen)
- pysam (Andreas Heger, et al.)
- BioPython community
- GWAS Catalog and dbSNP teams
- Google GenAI and File Search Tool
- MCP Protocol (Anthropic)
