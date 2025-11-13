#!/usr/bin/env python3
"""
Complete WGS Longevity Analysis Pipeline
Processes Sequencing.com 30x WGS data for longevity variants

This module provides a comprehensive pipeline for analyzing whole genome
sequencing data with a focus on longevity-associated genetic variants.
"""

from cyvcf2 import VCF, Writer
import pandas as pd
import numpy as np
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List, Tuple


class WGSLongevityAnalyzer:
    """
    Main class for analyzing WGS data for longevity-associated variants.

    This analyzer extracts validated longevity variants, calculates polygenic
    scores, determines APOE genotype, and generates comprehensive reports.
    """

    def __init__(self, vcf_path: str, output_dir: str = 'results'):
        """
        Initialize the longevity analyzer.

        Args:
            vcf_path: Path to bgzipped and indexed VCF file
            output_dir: Directory for output files (default: 'results')
        """
        self.vcf_path = vcf_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Configure logging
        log_file = self.output_dir / f'analysis_{datetime.now():%Y%m%d_%H%M%S}.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Define longevity variant panel
        self.longevity_panel = self._load_longevity_panel()
        self.variants = {}

    def _load_longevity_panel(self) -> Dict:
        """
        Define validated longevity variants with positions and effects.

        Returns:
            Dictionary mapping rsIDs to variant information
        """
        return {
            'rs7412': {
                'gene': 'APOE',
                'chrom': 'chr19',
                'pos': 44908684,
                'ref': 'C',
                'alt': 'T',
                'protective_allele': 'T',
                'effect_size': 0.15,
                'description': 'APOE ε2 allele - protective',
            },
            'rs429358': {
                'gene': 'APOE',
                'chrom': 'chr19',
                'pos': 44908822,
                'ref': 'T',
                'alt': 'C',
                'protective_allele': 'T',
                'effect_size': -0.20,
                'description': 'APOE ε4 allele - risk',
            },
            'rs2802292': {
                'gene': 'FOXO3',
                'chrom': 'chr6',
                'pos': 108878242,
                'ref': 'T',
                'alt': 'G',
                'protective_allele': 'G',
                'effect_size': 0.30,
                'description': 'FOXO3 longevity allele - 2.8x odds of reaching 95',
            },
            'rs2764264': {
                'gene': 'FOXO3',
                'chrom': 'chr6',
                'pos': 108882233,
                'ref': 'C',
                'alt': 'T',
                'protective_allele': 'T',
                'effect_size': 0.18,
                'description': 'FOXO3 secondary longevity variant',
            },
            'rs1063192': {
                'gene': 'CDKN2B',
                'chrom': 'chr9',
                'pos': 22124094,
                'ref': 'G',
                'alt': 'A',
                'protective_allele': 'A',
                'effect_size': 0.12,
                'description': 'CDKN2B/ANRIL longevity locus - 9p21.3',
            },
        }

    def quality_control(self) -> Dict:
        """
        Run quality control checks on VCF file.

        Samples 10,000 variants to assess overall quality metrics.

        Returns:
            Dictionary with QC summary statistics
        """
        self.logger.info("Running quality control checks...")

        vcf = VCF(self.vcf_path)

        stats = {
            'total_variants': 0,
            'snps': 0,
            'indels': 0,
            'mean_qual': [],
            'mean_depth': [],
        }

        # Sample 10,000 variants for QC
        for i, variant in enumerate(vcf):
            if i >= 10000:
                break

            stats['total_variants'] += 1

            # Classify variant type
            if len(variant.REF) == 1 and all(len(a) == 1 for a in variant.ALT):
                stats['snps'] += 1
            else:
                stats['indels'] += 1

            # Collect quality metrics
            stats['mean_qual'].append(variant.QUAL or 0)
            depths = variant.gt_depths[variant.gt_depths >= 0]
            if len(depths) > 0:
                stats['mean_depth'].append(np.mean(depths))

        vcf.close()

        # Calculate summary metrics
        summary = {
            'total_sampled': stats['total_variants'],
            'snp_rate': stats['snps'] / stats['total_variants'] if stats['total_variants'] > 0 else 0,
            'mean_quality': np.mean(stats['mean_qual']) if stats['mean_qual'] else 0,
            'mean_depth': np.mean(stats['mean_depth']) if stats['mean_depth'] else 0,
        }

        self.logger.info(f"QC Summary: {summary}")

        # Check for issues
        if summary['mean_depth'] < 20:
            self.logger.warning("Low coverage detected (mean depth < 20x)")
        if summary['mean_quality'] < 30:
            self.logger.warning("Low quality detected (mean QUAL < 30)")

        return summary

    def extract_longevity_variants(self) -> None:
        """
        Extract all panel variants from VCF file.

        Uses tabix indexing for efficient random access to specific positions.
        """
        self.logger.info("Extracting longevity variants...")

        vcf = VCF(self.vcf_path)

        for rsid, info in self.longevity_panel.items():
            chrom = info['chrom']
            pos = info['pos']

            found = False
            try:
                for variant in vcf(f'{chrom}:{pos}-{pos}'):
                    gt = variant.genotypes[0]

                    # Count alleles matching protective allele
                    ref_is_protective = (info['ref'] == info['protective_allele'])

                    protective_count = 0
                    for allele in [gt[0], gt[1]]:
                        if allele == 0 and ref_is_protective:
                            protective_count += 1
                        elif allele == 1 and not ref_is_protective:
                            protective_count += 1

                    self.variants[rsid] = {
                        'gene': info['gene'],
                        'position': f"{variant.CHROM}:{variant.POS}",
                        'ref': variant.REF,
                        'alt': ','.join(variant.ALT) if variant.ALT else '.',
                        'genotype': f"{gt[0]}/{gt[1]}",
                        'phased': bool(gt[2]),
                        'protective_alleles': protective_count,
                        'effect_size': info['effect_size'],
                        'depth': variant.gt_depths[0] if len(variant.gt_depths) > 0 else 0,
                        'quality': variant.gt_quals[0] if len(variant.gt_quals) > 0 else 0,
                        'description': info['description'],
                    }
                    found = True
                    break
            except Exception as e:
                self.logger.warning(f"Error querying {rsid} at {chrom}:{pos}: {e}")

            if not found:
                self.logger.warning(f"Variant {rsid} not found at {chrom}:{pos}")

        vcf.close()
        self.logger.info(f"Extracted {len(self.variants)} variants")

    def calculate_polygenic_score(self) -> float:
        """
        Calculate weighted polygenic longevity score.

        Combines effect sizes of protective and risk alleles across
        multiple validated longevity loci.

        Returns:
            Polygenic score (positive = protective, negative = risk)
        """
        score = 0.0
        for rsid, data in self.variants.items():
            weighted_contribution = data['effect_size'] * data['protective_alleles']
            score += weighted_contribution

        self.logger.info(f"Polygenic longevity score: {score:.3f}")
        return score

    def determine_apoe_status(self) -> Optional[str]:
        """
        Decode APOE ε2/ε3/ε4 genotype from rs7412 and rs429358.

        Returns:
            APOE genotype string (e.g., 'ε3/ε3') or None if variants missing
        """
        if 'rs7412' not in self.variants or 'rs429358' not in self.variants:
            self.logger.warning("APOE variants not found - cannot determine status")
            return None

        # Get genotypes (0=ref, 1=alt)
        gt_7412 = [int(x) for x in self.variants['rs7412']['genotype'].split('/')]
        gt_429358 = [int(x) for x in self.variants['rs429358']['genotype'].split('/')]

        # Decode alleles based on haplotype
        # rs7412: T=ε2(protective), C=ε3/ε4
        # rs429358: T=ε2/ε3, C=ε4(risk)
        alleles = []
        for a1, a2 in zip(gt_7412, gt_429358):
            if a1 == 1 and a2 == 0:  # T/T
                alleles.append('ε2')
            elif a1 == 0 and a2 == 0:  # C/T
                alleles.append('ε3')
            elif a1 == 0 and a2 == 1:  # C/C
                alleles.append('ε4')
            else:
                alleles.append('?')  # Unexpected combination

        return '/'.join(sorted(alleles))

    def generate_report(self) -> str:
        """
        Generate comprehensive longevity genetics report.

        Creates a markdown-formatted report with APOE status, variant
        summary, polygenic score, and clinical interpretations.

        Returns:
            Report text as string
        """
        self.logger.info("Generating report...")

        report = []

        # Header
        report.append("# Personal Longevity Genomics Report")
        report.append(f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}\n")
        report.append(f"Input: {self.vcf_path}\n")

        # APOE section
        report.append("## APOE Genotype")
        apoe_status = self.determine_apoe_status()
        if apoe_status:
            report.append(f"**Status:** {apoe_status}\n")

            interpretations = {
                'ε2/ε2': 'Strongest AD protection (~99% reduced risk), increased longevity',
                'ε2/ε3': 'Protective (~13% reduced AD risk), favorable lipid profile',
                'ε2/ε4': 'Mixed effects - requires individual assessment',
                'ε3/ε3': 'Most common genotype (~66% population), neutral reference',
                'ε3/ε4': 'Moderately increased AD risk (3-4x)',
                'ε4/ε4': 'Highest AD risk (12-61x depending on age), reduced longevity',
            }

            report.append(f"**Interpretation:** {interpretations.get(apoe_status, 'Unknown genotype')}\n")
        else:
            report.append("**Status:** Unable to determine (variants not found)\n")

        # Other longevity variants
        report.append("## Longevity Variant Summary")

        if self.variants:
            df = pd.DataFrame(self.variants).T
            df = df[['gene', 'position', 'genotype', 'protective_alleles', 'description']]
            report.append(df.to_markdown())
            report.append("")
        else:
            report.append("No variants extracted.\n")

        # Polygenic score
        report.append("## Polygenic Longevity Score")
        pgs = self.calculate_polygenic_score()
        report.append(f"**Score:** {pgs:.3f}")
        report.append("**Interpretation:** This weighted score combines protective and risk alleles")
        report.append("Positive scores indicate net protective genetic profile\n")

        # Caveats
        report.append("## Important Limitations")
        report.append("- Genetics explains only ~25% of longevity variance")
        report.append("- Lifestyle factors (diet, exercise, sleep) are more impactful")
        report.append("- Most studies conducted in European populations")
        report.append("- These results are informational only, not medical advice")
        report.append("- Consult genetic counselor for clinical interpretation\n")

        # Save report
        report_text = '\n'.join(report)
        report_file = self.output_dir / 'longevity_report.md'
        report_file.write_text(report_text)

        self.logger.info(f"Report saved to {report_file}")
        return report_text

    def run_analysis(self) -> str:
        """
        Execute complete analysis pipeline.

        Runs QC, extracts variants, calculates scores, and generates report.

        Returns:
            Final report text
        """
        self.logger.info("Starting longevity genomics analysis")
        self.logger.info(f"VCF file: {self.vcf_path}")

        # QC
        qc_results = self.quality_control()

        # Extract variants
        self.extract_longevity_variants()

        # Generate report
        report = self.generate_report()

        self.logger.info("Analysis complete!")

        return report


def main():
    """Command-line interface for longevity analysis."""
    import sys

    if len(sys.argv) != 2:
        print("Usage: python longevity_analyzer.py <input.vcf.gz>")
        print("\nAnalyzes whole genome sequencing data for longevity-associated variants")
        print("Input: 30x WGS VCF file from Sequencing.com (must be bgzipped and indexed)")
        sys.exit(1)

    vcf_path = sys.argv[1]

    # Verify file exists and is indexed
    if not Path(vcf_path).exists():
        print(f"Error: File not found: {vcf_path}")
        sys.exit(1)

    if not Path(f"{vcf_path}.tbi").exists():
        print(f"Error: Index file not found: {vcf_path}.tbi")
        print(f"Create index with: tabix -p vcf {vcf_path}")
        sys.exit(1)

    # Run analysis
    analyzer = WGSLongevityAnalyzer(vcf_path)
    report = analyzer.run_analysis()

    print("\n" + "="*60)
    print(report)


if __name__ == '__main__':
    main()
