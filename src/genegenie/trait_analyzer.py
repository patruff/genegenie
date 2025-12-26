#!/usr/bin/env python3
"""
Comprehensive Trait Analyzer

Analyzes genome for personality, cognition, behavior, addiction and other
interesting traits using curated SNP database and research papers.
"""

from cyvcf2 import VCF
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Set
from pathlib import Path
import logging
from datetime import datetime

from .utils.trait_db import (
    ALL_TRAIT_SNPS,
    get_snps_by_category,
    get_snps_by_trait,
    get_all_categories,
    get_all_traits,
    get_snp_info
)
from .analysis.vcf_utils import extract_variants_by_position


class TraitAnalyzer:
    """
    Comprehensive analyzer for personality, cognition, behavior, and other traits.

    Analyzes genome for 100+ interesting SNPs across multiple categories.
    """

    def __init__(self, vcf_path: str, output_dir: str = 'trait_results'):
        """
        Initialize trait analyzer.

        Args:
            vcf_path: Path to bgzipped and indexed VCF file
            output_dir: Directory for output files
        """
        self.vcf_path = vcf_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Configure logging
        log_file = self.output_dir / f'trait_analysis_{datetime.now():%Y%m%d_%H%M%S}.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Results storage
        self.extracted_variants = {}
        self.trait_scores = {}

    def extract_all_trait_snps(self) -> None:
        """
        Extract all trait-associated SNPs from VCF.

        Uses efficient position-based querying with tabix index.
        """
        self.logger.info(f"Extracting {len(ALL_TRAIT_SNPS)} trait SNPs...")

        # Build position lookup
        positions = [
            (info['chrom'], info['pos'])
            for rsid, info in ALL_TRAIT_SNPS.items()
        ]

        # Extract using position-based query
        vcf = VCF(self.vcf_path)

        for rsid, info in ALL_TRAIT_SNPS.items():
            chrom = info['chrom']
            pos = info['pos']

            try:
                for variant in vcf(f'{chrom}:{pos}-{pos}'):
                    gt = variant.genotypes[0]

                    # Determine effect allele count
                    ref_is_effect = (info['ref'] == info.get('effect_allele'))

                    effect_count = 0
                    for allele in [gt[0], gt[1]]:
                        if allele == 0 and ref_is_effect:
                            effect_count += 1
                        elif allele == 1 and not ref_is_effect:
                            effect_count += 1

                    self.extracted_variants[rsid] = {
                        'rsid': rsid,
                        'gene': info['gene'],
                        'trait': info['trait'],
                        'category': info['category'],
                        'position': f"{variant.CHROM}:{variant.POS}",
                        'ref': variant.REF,
                        'alt': ','.join(variant.ALT) if variant.ALT else '.',
                        'genotype': f"{gt[0]}/{gt[1]}",
                        'effect_allele': info.get('effect_allele', ''),
                        'effect_count': effect_count,
                        'effect_size': info.get('effect_size', 0),
                        'p_value': info.get('p_value', ''),
                        'description': info['description'],
                        'paper': info.get('paper', ''),
                        'depth': variant.gt_depths[0] if len(variant.gt_depths) > 0 else 0,
                        'quality': variant.gt_quals[0] if len(variant.gt_quals) > 0 else 0,
                    }
                    break
            except Exception as e:
                self.logger.warning(f"Error querying {rsid} at {chrom}:{pos}: {e}")

        vcf.close()
        self.logger.info(f"Extracted {len(self.extracted_variants)} variants")

    def calculate_category_scores(self) -> Dict:
        """
        Calculate aggregate scores for each trait category.

        Returns:
            Dictionary with category scores
        """
        self.logger.info("Calculating category scores...")

        scores = {}

        for category in get_all_categories():
            category_variants = [
                v for v in self.extracted_variants.values()
                if v['category'] == category
            ]

            if not category_variants:
                continue

            # Calculate weighted score
            total_score = 0
            max_possible = 0

            for variant in category_variants:
                effect_size = variant['effect_size']
                effect_count = variant['effect_count']

                # Normalize effect sizes (handle both OR and beta)
                if abs(effect_size) > 10:  # Likely odds ratio
                    effect_norm = np.log(effect_size)
                else:  # Beta coefficient
                    effect_norm = effect_size

                total_score += effect_norm * effect_count
                max_possible += abs(effect_norm) * 2  # Max = 2 copies

            # Normalize to 0-100 scale
            if max_possible > 0:
                normalized_score = (total_score / max_possible) * 50 + 50
            else:
                normalized_score = 50

            scores[category] = {
                'score': normalized_score,
                'variant_count': len(category_variants),
                'raw_score': total_score,
            }

        self.trait_scores = scores
        return scores

    def generate_visual_report(self) -> Path:
        """
        Generate interactive HTML visualization report.

        Returns:
            Path to generated HTML file
        """
        self.logger.info("Generating interactive visual report...")

        from .visualization import create_visualization_from_analyzer

        html_path = create_visualization_from_analyzer(
            analyzer=self,
            output_filename='trait_report.html'
        )

        self.logger.info(f"Visual report saved to {html_path}")
        return html_path

    def generate_trait_report(self) -> str:
        """
        Generate comprehensive trait genetics report.

        Returns:
            Markdown-formatted report text
        """
        self.logger.info("Generating trait report...")

        report = []

        # Header
        report.append("# Comprehensive Trait Genetics Report")
        report.append(f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}\n")
        report.append(f"Input: {self.vcf_path}\n")
        report.append(f"Total SNPs analyzed: {len(self.extracted_variants)}\n")

        # Category summaries
        report.append("## Category Scores\n")
        report.append("Scores range from 0-100 (50 = population average)\n")

        for category, data in sorted(self.trait_scores.items()):
            score = data['score']
            count = data['variant_count']

            # Interpret score
            if score >= 60:
                interpretation = "Above average"
            elif score >= 55:
                interpretation = "Slightly above average"
            elif score >= 45:
                interpretation = "Average"
            elif score >= 40:
                interpretation = "Slightly below average"
            else:
                interpretation = "Below average"

            report.append(f"### {category.replace('_', ' ').title()}")
            report.append(f"**Score:** {score:.1f} ({interpretation})")
            report.append(f"**SNPs analyzed:** {count}\n")

        # Detailed variant information by category
        for category in sorted(get_all_categories()):
            variants = [
                v for v in self.extracted_variants.values()
                if v['category'] == category
            ]

            if not variants:
                continue

            report.append(f"## {category.replace('_', ' ').title()} Variants\n")

            # Group by trait
            traits = set(v['trait'] for v in variants)

            for trait in sorted(traits):
                trait_variants = [v for v in variants if v['trait'] == trait]

                report.append(f"### {trait}\n")

                for variant in trait_variants:
                    report.append(f"**{variant['rsid']}** ({variant['gene']})")
                    report.append(f"- Genotype: {variant['genotype']}")
                    report.append(f"- Effect alleles: {variant['effect_count']}/2")
                    report.append(f"- {variant['description']}")
                    report.append(f"- Source: {variant['paper']}")
                    report.append("")

        # Interesting highlights
        report.append("## Notable Findings\n")

        # Find interesting variants
        interesting = []

        for variant in self.extracted_variants.values():
            # High effect variants
            if variant['effect_count'] == 2 and abs(variant['effect_size']) > 0.2:
                interesting.append({
                    'variant': variant,
                    'reason': 'Homozygous for high-effect allele'
                })

            # Rare genotypes
            if variant['rsid'] in ['rs1815739', 'rs1229984', 'rs16969968']:
                interesting.append({
                    'variant': variant,
                    'reason': 'Clinically significant variant'
                })

        if interesting:
            for item in interesting[:10]:  # Top 10
                v = item['variant']
                report.append(f"- **{v['rsid']}** ({v['gene']}): {item['reason']}")
                report.append(f"  {v['trait']} - {v['genotype']}")
                report.append("")

        # Caveats
        report.append("\n## Important Caveats\n")
        report.append("- Most traits are highly polygenic (100s-1000s of variants)")
        report.append("- Individual SNP effects are generally small")
        report.append("- Environment and gene-environment interactions are critical")
        report.append("- These results are for research/educational purposes only")
        report.append("- Ancestry matters - most GWAS conducted in European populations")
        report.append("- Consult genetic counselor for clinical interpretation\n")

        # Save report
        report_text = '\n'.join(report)
        report_file = self.output_dir / 'trait_genetics_report.md'
        report_file.write_text(report_text)

        self.logger.info(f"Report saved to {report_file}")
        return report_text

    def export_to_csv(self) -> None:
        """Export variant data to CSV file."""
        if not self.extracted_variants:
            self.logger.warning("No variants to export")
            return

        df = pd.DataFrame(self.extracted_variants).T
        csv_file = self.output_dir / 'trait_variants.csv'
        df.to_csv(csv_file, index=False)

        self.logger.info(f"Variants exported to {csv_file}")

    def get_category_report(self, category: str) -> Dict:
        """
        Get detailed report for specific category.

        Args:
            category: Category name (e.g., 'addiction', 'cognition')

        Returns:
            Dictionary with category analysis
        """
        variants = [
            v for v in self.extracted_variants.values()
            if v['category'] == category
        ]

        if not variants:
            return {'error': f'No variants found for category: {category}'}

        # Calculate statistics
        effect_alleles = [v['effect_count'] for v in variants]
        avg_effect_alleles = np.mean(effect_alleles)

        return {
            'category': category,
            'variant_count': len(variants),
            'avg_effect_alleles': avg_effect_alleles,
            'score': self.trait_scores.get(category, {}).get('score', 50),
            'variants': variants,
        }

    def run_analysis(self, generate_html: bool = True) -> str:
        """
        Execute complete trait analysis pipeline.

        Args:
            generate_html: Whether to generate interactive HTML visualization (default: True)

        Returns:
            Final report text
        """
        self.logger.info("Starting comprehensive trait analysis")

        # Extract variants
        self.extract_all_trait_snps()

        # Calculate scores
        self.calculate_category_scores()

        # Export data
        self.export_to_csv()

        # Generate markdown report
        report = self.generate_trait_report()

        # Generate HTML visualization
        if generate_html:
            html_path = self.generate_visual_report()
            self.logger.info(f"📊 Open in browser: {html_path.absolute()}")

        self.logger.info("Analysis complete!")

        return report


def main():
    """Command-line interface for trait analysis."""
    import sys

    if len(sys.argv) != 2:
        print("Usage: python trait_analyzer.py <input.vcf.gz>")
        print("\nAnalyzes genome for personality, cognition, behavior, addiction traits")
        print("Input: VCF file (must be bgzipped and tabix-indexed)")
        print()
        print("Categories analyzed:")
        print("  - Cognition (intelligence, memory, processing speed)")
        print("  - Personality (Big Five traits)")
        print("  - Addiction (alcohol, nicotine, cannabis, caffeine)")
        print("  - Behavior (risk-taking, sleep, chronotype)")
        print("  - Mental health (depression, anxiety, ADHD)")
        print("  - Physical traits (athletic performance, pain sensitivity)")
        print("  - Sensory (taste, smell, hearing)")
        sys.exit(1)

    vcf_path = sys.argv[1]

    # Verify file
    if not Path(vcf_path).exists():
        print(f"Error: File not found: {vcf_path}")
        sys.exit(1)

    if not Path(f"{vcf_path}.tbi").exists():
        print(f"Error: Index file not found: {vcf_path}.tbi")
        print(f"Create index with: tabix -p vcf {vcf_path}")
        sys.exit(1)

    # Run analysis
    analyzer = TraitAnalyzer(vcf_path)
    report = analyzer.run_analysis()

    print("\n" + "="*70)
    print(report)


if __name__ == '__main__':
    main()
