# Research Papers Directory

This directory is for storing genomics research papers (PDFs) for SNP extraction.

## Purpose

GeneGenie can automatically extract SNPs, genes, and genomic positions from research papers. Place your PDFs here to:

1. **Extract SNPs**: Automatically identify all rs IDs mentioned in papers
2. **Build Custom Databases**: Create your own SNP libraries from papers
3. **Parse GWAS Tables**: Extract result tables with p-values and effect sizes
4. **Cross-reference**: Match paper SNPs with your genome

## Usage

### Extract from Single Paper

```bash
python examples/pdf_parser_example.py basic papers/gwas_intelligence.pdf
```

### Process All Papers

```bash
python examples/pdf_parser_example.py directory papers/
```

### Build Custom Database

```bash
python examples/pdf_parser_example.py database papers/
```

This will create a JSON database with all SNPs found across your papers.

## Recommended Papers

### Intelligence & Cognition
- Savage et al. (2018) Nat Genet - Intelligence GWAS meta-analysis
- Hill et al. (2019) Mol Psychiatry - Cognitive function

### Personality
- Nagel et al. (2018) Nat Genet - Neuroticism (449k participants)
- van den Berg et al. (2016) Mol Psychiatry - Extraversion
- Lo et al. (2017) Nat Genet - Openness, conscientiousness

### Addiction
- Gelernter et al. (2014) Mol Psychiatry - Alcohol dependence
- Tobacco Genetics Consortium (2010) Nat Genet - Nicotine
- Pasman et al. (2018) Nat Neurosci - Cannabis

### Behavior
- Karlsson Linnér et al. (2019) Nat Genet - Risk-taking (1.2M)
- Dashti et al. (2019) Nat Commun - Sleep duration
- Jones et al. (2019) Nat Commun - Chronotype

### Mental Health
- Howard et al. (2019) Nat Neurosci - Depression (807k)
- Demontis et al. (2019) Nat Genet - ADHD
- Schizophrenia Working Group (2014) Nature

## File Organization

Organize papers by category:

```
papers/
├── cognition/
│   ├── intelligence_savage2018.pdf
│   └── memory_studies.pdf
├── personality/
│   ├── neuroticism_nagel2018.pdf
│   └── big_five_overview.pdf
├── addiction/
│   ├── alcohol_gelernter2014.pdf
│   └── nicotine_tobacco_consortium.pdf
└── behavior/
    ├── risk_taking_karlsson2019.pdf
    └── sleep_dashti2019.pdf
```

## Important Notes

⚠️ **Copyright Considerations**
- Only include papers you have legal access to
- Many journals allow personal use of PDFs
- Check publisher policies before sharing

⚠️ **File Exclusion**
- PDF files are excluded from git via `.gitignore`
- This directory structure is tracked, but PDFs are not
- Share paper lists, not the PDFs themselves

## Extraction Quality

PDF extraction works best with:
- ✅ Text-based PDFs (not scanned images)
- ✅ Well-formatted tables
- ✅ Standard GWAS result formats
- ❌ Image-only PDFs may require OCR

## Output Examples

After processing, you'll get:

1. **SNP Lists**: All rsIDs mentioned in each paper
2. **Gene Lists**: Genes mentioned multiple times (likely key genes)
3. **GWAS Tables**: Structured data with p-values, effect sizes
4. **Contexts**: Surrounding text for each SNP mention
5. **Custom Database**: JSON file with all extracted data

## Next Steps

After extracting SNPs from papers:

```bash
# Match paper SNPs with your genome
python examples/pdf_parser_example.py match papers/paper.pdf data/genome.vcf.gz

# Add extracted SNPs to trait database
# (Edit src/genegenie/utils/trait_db.py)
```

Happy paper mining! 📄🧬
