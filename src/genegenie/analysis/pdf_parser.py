"""
PDF Parser for SNP Extraction

Tools for extracting SNPs and genomic information from research papers (PDFs).
Uses PyMuPDF (fitz), pdfplumber, and regex for robust extraction.
"""

import re
import json
from typing import List, Dict, Set, Tuple, Optional
from pathlib import Path
import warnings

# PDF parsing libraries
try:
    import fitz  # PyMuPDF - fastest
    HAS_FITZ = True
except ImportError:
    HAS_FITZ = False
    warnings.warn("PyMuPDF not installed - install with: pip install PyMuPDF")

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False
    warnings.warn("pdfplumber not installed - install with: pip install pdfplumber")

try:
    from PyPDF2 import PdfReader
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False


class SNPExtractor:
    """Extract SNPs and genomic positions from PDF research papers."""

    def __init__(self):
        """Initialize SNP extractor with regex patterns."""

        # Regex patterns for SNP identification
        self.rsid_pattern = re.compile(r'\brs\d+\b', re.IGNORECASE)

        # Chromosome positions (e.g., chr1:12345678, 1:12345678)
        self.position_pattern = re.compile(
            r'\b(?:chr)?([0-9]{1,2}|X|Y|MT?):([0-9,]+)\b',
            re.IGNORECASE
        )

        # Gene names (all caps, 2-10 letters)
        self.gene_pattern = re.compile(r'\b([A-Z][A-Z0-9]{1,9})\b')

        # P-values
        self.pvalue_pattern = re.compile(
            r'[Pp]\s*[=<>]\s*([0-9.]+(?:e-?[0-9]+)?)',
            re.IGNORECASE
        )

        # Odds ratios / effect sizes
        self.or_pattern = re.compile(
            r'(?:OR|odds ratio)\s*[=:]\s*([0-9.]+)',
            re.IGNORECASE
        )

    def extract_text_fitz(self, pdf_path: str) -> str:
        """
        Extract text using PyMuPDF (fastest method).

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text
        """
        if not HAS_FITZ:
            raise ImportError("PyMuPDF not installed")

        doc = fitz.open(pdf_path)
        text = ""

        for page in doc:
            text += page.get_text()

        doc.close()
        return text

    def extract_text_pdfplumber(self, pdf_path: str) -> str:
        """
        Extract text using pdfplumber (good for tables).

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text
        """
        if not HAS_PDFPLUMBER:
            raise ImportError("pdfplumber not installed")

        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        return text

    def extract_text_pypdf2(self, pdf_path: str) -> str:
        """
        Extract text using PyPDF2 (fallback method).

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text
        """
        if not HAS_PYPDF2:
            raise ImportError("PyPDF2 not installed")

        reader = PdfReader(pdf_path)
        text = ""

        for page in reader.pages:
            text += page.extract_text()

        return text

    def extract_text(self, pdf_path: str, method: str = 'auto') -> str:
        """
        Extract text from PDF using available library.

        Args:
            pdf_path: Path to PDF file
            method: 'auto', 'fitz', 'pdfplumber', or 'pypdf2'

        Returns:
            Extracted text

        Example:
            >>> extractor = SNPExtractor()
            >>> text = extractor.extract_text('gwas_paper.pdf')
        """
        if method == 'auto':
            # Try methods in order of speed/quality
            if HAS_FITZ:
                return self.extract_text_fitz(pdf_path)
            elif HAS_PDFPLUMBER:
                return self.extract_text_pdfplumber(pdf_path)
            elif HAS_PYPDF2:
                return self.extract_text_pypdf2(pdf_path)
            else:
                raise ImportError("No PDF library available")

        elif method == 'fitz':
            return self.extract_text_fitz(pdf_path)
        elif method == 'pdfplumber':
            return self.extract_text_pdfplumber(pdf_path)
        elif method == 'pypdf2':
            return self.extract_text_pypdf2(pdf_path)
        else:
            raise ValueError(f"Unknown method: {method}")

    def extract_rsids(self, text: str) -> List[str]:
        """
        Extract all rsIDs from text.

        Args:
            text: Text to search

        Returns:
            List of unique rsIDs

        Example:
            >>> rsids = extractor.extract_rsids(pdf_text)
            >>> print(f"Found {len(rsids)} SNPs")
        """
        matches = self.rsid_pattern.findall(text)
        # Normalize to lowercase and deduplicate
        return sorted(list(set([m.lower() for m in matches])))

    def extract_positions(self, text: str) -> List[Tuple[str, int]]:
        """
        Extract genomic positions from text.

        Args:
            text: Text to search

        Returns:
            List of (chromosome, position) tuples

        Example:
            >>> positions = extractor.extract_positions(pdf_text)
        """
        matches = self.position_pattern.findall(text)
        positions = []

        for chrom, pos in matches:
            # Remove commas from position
            pos_clean = pos.replace(',', '')
            try:
                positions.append((chrom, int(pos_clean)))
            except ValueError:
                continue

        return list(set(positions))

    def extract_genes(self, text: str, min_occurrences: int = 2) -> List[str]:
        """
        Extract gene names from text.

        Args:
            text: Text to search
            min_occurrences: Minimum number of times gene must appear

        Returns:
            List of likely gene names

        Example:
            >>> genes = extractor.extract_genes(pdf_text)
        """
        matches = self.gene_pattern.findall(text)

        # Count occurrences
        gene_counts = {}
        for gene in matches:
            # Filter common words that aren't genes
            if gene in ['AND', 'OR', 'NOT', 'THE', 'FOR', 'ARE', 'WAS', 'WITH']:
                continue
            gene_counts[gene] = gene_counts.get(gene, 0) + 1

        # Filter by minimum occurrences
        genes = [
            gene for gene, count in gene_counts.items()
            if count >= min_occurrences
        ]

        return sorted(genes)

    def extract_snp_context(
        self,
        text: str,
        rsid: str,
        context_chars: int = 200
    ) -> List[str]:
        """
        Extract surrounding text context for a specific SNP.

        Args:
            text: Full text
            rsid: rsID to find
            context_chars: Characters before/after to include

        Returns:
            List of context snippets

        Example:
            >>> contexts = extractor.extract_snp_context(text, 'rs6265')
            >>> for ctx in contexts:
            >>>     print(ctx)
        """
        contexts = []
        pattern = re.compile(rf'\b{rsid}\b', re.IGNORECASE)

        for match in pattern.finditer(text):
            start = max(0, match.start() - context_chars)
            end = min(len(text), match.end() + context_chars)
            contexts.append(text[start:end])

        return contexts

    def extract_comprehensive_snp_data(
        self,
        pdf_path: str
    ) -> Dict:
        """
        Extract comprehensive SNP information from PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with extracted data

        Example:
            >>> data = extractor.extract_comprehensive_snp_data('paper.pdf')
            >>> print(f"Found {len(data['rsids'])} SNPs")
            >>> print(f"Found {len(data['genes'])} genes")
        """
        # Extract text
        text = self.extract_text(pdf_path)

        # Extract all components
        rsids = self.extract_rsids(text)
        positions = self.extract_positions(text)
        genes = self.extract_genes(text)

        # Get context for each SNP
        snp_contexts = {}
        for rsid in rsids[:20]:  # Limit to first 20 to avoid too much data
            contexts = self.extract_snp_context(text, rsid)
            if contexts:
                snp_contexts[rsid] = contexts[0]  # First occurrence

        return {
            'pdf_path': str(pdf_path),
            'rsids': rsids,
            'positions': positions,
            'genes': genes,
            'snp_count': len(rsids),
            'gene_count': len(genes),
            'snp_contexts': snp_contexts,
        }

    def extract_tables_pdfplumber(
        self,
        pdf_path: str
    ) -> List[List[List[str]]]:
        """
        Extract tables from PDF (useful for GWAS result tables).

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of tables (each table is list of rows)

        Example:
            >>> tables = extractor.extract_tables_pdfplumber('paper.pdf')
            >>> for table in tables:
            >>>     # Process table rows
            >>>     for row in table:
            >>>         print(row)
        """
        if not HAS_PDFPLUMBER:
            raise ImportError("pdfplumber not installed")

        all_tables = []

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                if tables:
                    all_tables.extend(tables)

        return all_tables

    def parse_gwas_table(
        self,
        table: List[List[str]]
    ) -> List[Dict]:
        """
        Parse GWAS results table into structured data.

        Args:
            table: Table rows from PDF

        Returns:
            List of dictionaries with SNP information

        Example:
            >>> tables = extractor.extract_tables_pdfplumber('paper.pdf')
            >>> for table in tables:
            >>>     snps = extractor.parse_gwas_table(table)
            >>>     print(snps)
        """
        if not table or len(table) < 2:
            return []

        # Try to identify header row
        header = table[0]

        # Common column names
        rsid_cols = ['snp', 'rsid', 'variant', 'rs']
        gene_cols = ['gene', 'nearest gene', 'locus']
        pval_cols = ['p-value', 'p', 'pval', 'p value']
        or_cols = ['or', 'odds ratio', 'effect', 'beta']

        # Find column indices
        rsid_idx = None
        gene_idx = None
        pval_idx = None
        or_idx = None

        for i, col in enumerate(header):
            col_lower = col.lower() if col else ''
            if any(c in col_lower for c in rsid_cols):
                rsid_idx = i
            if any(c in col_lower for c in gene_cols):
                gene_idx = i
            if any(c in col_lower for c in pval_cols):
                pval_idx = i
            if any(c in col_lower for c in or_cols):
                or_idx = i

        # Parse data rows
        snps = []
        for row in table[1:]:
            if not row or len(row) <= max(filter(None, [rsid_idx, gene_idx])):
                continue

            snp_data = {}

            if rsid_idx is not None and rsid_idx < len(row):
                rsid_text = row[rsid_idx]
                if rsid_text:
                    # Extract rsID if present
                    rsid_match = self.rsid_pattern.search(rsid_text)
                    if rsid_match:
                        snp_data['rsid'] = rsid_match.group()

            if gene_idx is not None and gene_idx < len(row):
                snp_data['gene'] = row[gene_idx]

            if pval_idx is not None and pval_idx < len(row):
                pval_text = row[pval_idx]
                if pval_text:
                    try:
                        # Try to parse scientific notation
                        snp_data['p_value'] = float(pval_text.replace('×', 'e').replace('^', 'e'))
                    except:
                        snp_data['p_value'] = pval_text

            if or_idx is not None and or_idx < len(row):
                or_text = row[or_idx]
                if or_text:
                    try:
                        snp_data['effect_size'] = float(or_text)
                    except:
                        snp_data['effect_size'] = or_text

            if snp_data:
                snps.append(snp_data)

        return snps


def extract_snps_from_pdf(pdf_path: str) -> Dict:
    """
    Convenience function to extract SNPs from PDF.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Dictionary with extracted SNP information

    Example:
        >>> data = extract_snps_from_pdf('gwas_paper.pdf')
        >>> print(data['rsids'])
    """
    extractor = SNPExtractor()
    return extractor.extract_comprehensive_snp_data(pdf_path)


def extract_snps_from_directory(
    directory: str,
    output_json: Optional[str] = None
) -> Dict[str, Dict]:
    """
    Extract SNPs from all PDFs in a directory.

    Args:
        directory: Directory containing PDF files
        output_json: Optional path to save results as JSON

    Returns:
        Dictionary mapping PDF filename to extracted data

    Example:
        >>> results = extract_snps_from_directory('papers/')
        >>> for pdf, data in results.items():
        >>>     print(f"{pdf}: {len(data['rsids'])} SNPs")
    """
    extractor = SNPExtractor()
    results = {}

    pdf_dir = Path(directory)
    for pdf_file in pdf_dir.glob('*.pdf'):
        try:
            data = extractor.extract_comprehensive_snp_data(str(pdf_file))
            results[pdf_file.name] = data
        except Exception as e:
            print(f"Error processing {pdf_file}: {e}")

    # Save to JSON if requested
    if output_json:
        with open(output_json, 'w') as f:
            json.dump(results, f, indent=2)

    return results
