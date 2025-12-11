#!/usr/bin/env python3
"""
PDF Parser Examples

Demonstrates extraction of SNPs and genomic data from research papers.
"""

import sys
sys.path.insert(0, '../src')

from genegenie.analysis.pdf_parser import (
    SNPExtractor,
    extract_snps_from_pdf,
    extract_snps_from_directory
)
from pathlib import Path
import json


def example_basic_extraction(pdf_path: str):
    """Basic SNP extraction from a single PDF."""

    print("=" * 70)
    print(" Basic SNP Extraction")
    print("=" * 70)
    print(f"\nProcessing: {pdf_path}\n")

    # Extract using convenience function
    data = extract_snps_from_pdf(pdf_path)

    print(f"Found {data['snp_count']} SNPs")
    print(f"Found {data['gene_count']} genes")
    print(f"Found {len(data['positions'])} genomic positions\n")

    # Show first 20 SNPs
    print("SNPs found:")
    for rsid in data['rsids'][:20]:
        print(f"  {rsid}")

    if len(data['rsids']) > 20:
        print(f"  ... and {len(data['rsids']) - 20} more")

    # Show genes
    print(f"\nGenes mentioned (appearing 2+ times):")
    for gene in data['genes'][:20]:
        print(f"  {gene}")

    if len(data['genes']) > 20:
        print(f"  ... and {len(data['genes']) - 20} more")


def example_detailed_extraction(pdf_path: str):
    """Detailed extraction with context and tables."""

    print("\n" + "=" * 70)
    print(" Detailed Extraction with Context")
    print("=" * 70)
    print(f"\nProcessing: {pdf_path}\n")

    extractor = SNPExtractor()

    # Extract text
    print("Extracting text...")
    text = extractor.extract_text(pdf_path)
    print(f"Extracted {len(text)} characters\n")

    # Extract SNPs
    rsids = extractor.extract_rsids(text)
    print(f"Found {len(rsids)} unique SNPs\n")

    # Get context for top SNPs
    print("SNP contexts (first 3):\n")
    for rsid in rsids[:3]:
        contexts = extractor.extract_snp_context(text, rsid, context_chars=150)
        if contexts:
            print(f"{rsid}:")
            print(f"  ...{contexts[0]}...")
            print()

    # Try to extract tables
    try:
        print("Extracting tables...")
        tables = extractor.extract_tables_pdfplumber(pdf_path)
        print(f"Found {len(tables)} tables\n")

        if tables:
            print("Parsing GWAS tables...")
            for i, table in enumerate(tables[:3]):  # First 3 tables
                snps = extractor.parse_gwas_table(table)
                if snps:
                    print(f"\nTable {i+1}: {len(snps)} SNPs")
                    for snp in snps[:5]:  # Show first 5
                        print(f"  {snp}")

    except Exception as e:
        print(f"Table extraction not available: {e}")


def example_directory_extraction(directory: str):
    """Extract SNPs from all PDFs in a directory."""

    print("\n" + "=" * 70)
    print(" Batch PDF Processing")
    print("=" * 70)
    print(f"\nProcessing directory: {directory}\n")

    # Extract from all PDFs
    results = extract_snps_from_directory(
        directory,
        output_json='pdf_extraction_results.json'
    )

    print(f"Processed {len(results)} PDF files\n")

    # Summary
    total_snps = set()
    total_genes = set()

    for pdf_name, data in results.items():
        print(f"{pdf_name}:")
        print(f"  SNPs: {data['snp_count']}")
        print(f"  Genes: {data['gene_count']}")

        total_snps.update(data['rsids'])
        total_genes.update(data['genes'])

    print(f"\nCombined across all PDFs:")
    print(f"  Unique SNPs: {len(total_snps)}")
    print(f"  Unique genes: {len(total_genes)}")
    print(f"\nResults saved to: pdf_extraction_results.json")


def example_build_custom_database(directory: str):
    """Build custom SNP database from papers."""

    print("\n" + "=" * 70)
    print(" Building Custom SNP Database from Papers")
    print("=" * 70)
    print(f"\nProcessing papers in: {directory}\n")

    # Extract from all PDFs
    results = extract_snps_from_directory(directory)

    # Build database
    custom_db = {}

    for pdf_name, data in results.items():
        for rsid in data['rsids']:
            if rsid not in custom_db:
                custom_db[rsid] = {
                    'rsid': rsid,
                    'papers': [],
                    'contexts': []
                }

            custom_db[rsid]['papers'].append(pdf_name)

            # Add context if available
            if rsid in data.get('snp_contexts', {}):
                custom_db[rsid]['contexts'].append(data['snp_contexts'][rsid])

    print(f"Built database with {len(custom_db)} unique SNPs\n")

    # Show SNPs mentioned in multiple papers
    multi_paper_snps = {
        rsid: info for rsid, info in custom_db.items()
        if len(info['papers']) > 1
    }

    print(f"SNPs mentioned in multiple papers: {len(multi_paper_snps)}\n")

    # Show top replicated SNPs
    sorted_snps = sorted(
        multi_paper_snps.items(),
        key=lambda x: len(x[1]['papers']),
        reverse=True
    )

    print("Most replicated SNPs:")
    for rsid, info in sorted_snps[:10]:
        print(f"  {rsid}: {len(info['papers'])} papers")

    # Save database
    output_file = 'custom_snp_database.json'
    with open(output_file, 'w') as f:
        json.dump(custom_db, f, indent=2)

    print(f"\nCustom database saved to: {output_file}")


def example_match_with_genome(pdf_path: str, vcf_path: str):
    """Extract SNPs from paper and check which are in genome."""

    print("\n" + "=" * 70)
    print(" Match Paper SNPs with Genome")
    print("=" * 70)
    print(f"\nPaper: {pdf_path}")
    print(f"Genome: {vcf_path}\n")

    # Extract SNPs from paper
    data = extract_snps_from_pdf(pdf_path)
    paper_snps = data['rsids']

    print(f"Paper contains {len(paper_snps)} SNPs\n")

    # Check which are in genome (would need actual implementation)
    print("To check presence in genome, use:")
    print("  from genegenie.analysis.vcf_utils import extract_variants_by_rsid")
    print(f"  variants = extract_variants_by_rsid('{vcf_path}', paper_snps)")
    print()
    print("Then you can see which SNPs from the paper are in your genome")
    print("and what your genotypes are for those variants.")


def main():
    if len(sys.argv) < 2:
        print("Usage: python pdf_parser_example.py <command> [options]")
        print("\nCommands:")
        print("  basic <pdf>              - Basic SNP extraction")
        print("  detailed <pdf>           - Detailed extraction with context")
        print("  directory <dir>          - Process all PDFs in directory")
        print("  database <dir>           - Build custom SNP database")
        print("  match <pdf> <vcf>        - Match paper SNPs with genome")
        print()
        print("Examples:")
        print("  python pdf_parser_example.py basic gwas_paper.pdf")
        print("  python pdf_parser_example.py directory papers/")
        print("  python pdf_parser_example.py match paper.pdf genome.vcf.gz")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'basic':
        if len(sys.argv) < 3:
            print("Usage: python pdf_parser_example.py basic <pdf>")
            sys.exit(1)
        example_basic_extraction(sys.argv[2])

    elif command == 'detailed':
        if len(sys.argv) < 3:
            print("Usage: python pdf_parser_example.py detailed <pdf>")
            sys.exit(1)
        example_detailed_extraction(sys.argv[2])

    elif command == 'directory':
        if len(sys.argv) < 3:
            print("Usage: python pdf_parser_example.py directory <dir>")
            sys.exit(1)
        example_directory_extraction(sys.argv[2])

    elif command == 'database':
        if len(sys.argv) < 3:
            print("Usage: python pdf_parser_example.py database <dir>")
            sys.exit(1)
        example_build_custom_database(sys.argv[2])

    elif command == 'match':
        if len(sys.argv) < 4:
            print("Usage: python pdf_parser_example.py match <pdf> <vcf>")
            sys.exit(1)
        example_match_with_genome(sys.argv[2], sys.argv[3])

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

    print("\n" + "=" * 70)
    print(" Example Complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()
