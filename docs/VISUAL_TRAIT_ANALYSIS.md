# Visual Trait Analysis

Interactive HTML visualization system for genetic trait analysis results.

## Overview

The visual trait analysis system generates beautiful, interactive HTML reports displaying your genetic predisposition across multiple trait categories. Each category is shown as a card with:

- **Category Icon**: Visual emoji identifier for quick recognition
- **Genetic Score**: Your genetic predisposition score (0-100, 50 = average)
- **Visual Scale**: SVG-based slider showing where you fall on the trait spectrum
- **Top Variants**: Key genetic variants contributing to your score
- **Interpretation**: Plain-language interpretation of your score

## Features

### Visual Elements

- **Grid Layout**: Responsive grid that adapts to screen size
- **Color-Coded Categories**: Each trait category has a unique color scheme
- **SVG Scales**: Interactive scales with tick marks and score indicators
- **Hover Effects**: Cards lift on hover for better interactivity
- **Mobile-Friendly**: Responsive design works on all devices

### Categories Visualized

1. **🧠 Cognition** (Indigo)
   - Intelligence, Memory, Processing Speed

2. **🎭 Personality** (Purple)
   - Big Five traits (Neuroticism, Extraversion, Openness, Conscientiousness, Agreeableness)

3. **🚬 Addiction** (Red)
   - Alcohol, Nicotine, Cannabis, Caffeine

4. **⚡ Behavior** (Amber)
   - Risk-taking, Sleep, Chronotype, Aggression

5. **💭 Mental Health** (Emerald)
   - Depression, Anxiety, ADHD, Bipolar, Schizophrenia

6. **💪 Physical** (Cyan)
   - Athletic Performance, Muscle Strength, Pain Sensitivity

7. **👃 Sensory** (Pink)
   - Taste, Smell, Hearing

## Usage

### Basic Usage

```python
from genegenie.trait_analyzer import TraitAnalyzer

# Run analysis with HTML visualization
analyzer = TraitAnalyzer('data/genome.vcf.gz')
report = analyzer.run_analysis(generate_html=True)

# Opens: trait_results/trait_report.html
```

### Command Line

```bash
# Standard analysis (auto-generates HTML)
python src/genegenie/trait_analyzer.py data/genome.vcf.gz

# Or use the example script
python examples/visual_trait_analysis.py data/genome.vcf.gz

# Then open the report
open trait_results/trait_report.html  # macOS
xdg-open trait_results/trait_report.html  # Linux
start trait_results/trait_report.html  # Windows
```

### Generate Only HTML (Skip Markdown)

```python
analyzer = TraitAnalyzer('data/genome.vcf.gz')
analyzer.extract_all_trait_snps()
analyzer.calculate_category_scores()

# Generate only the visual report
html_path = analyzer.generate_visual_report()
print(f"Report: {html_path}")
```

### Programmatic Access

```python
from genegenie.visualization import generate_html_report

# Generate custom HTML report
html = generate_html_report(
    scores=analyzer.trait_scores,
    extracted_variants=analyzer.extracted_variants,
    vcf_path='genome.vcf.gz',
    output_path=Path('custom_report.html')
)
```

## Understanding Your Scores

### Score Interpretation

- **60-100**: Above average genetic predisposition
- **55-60**: Slightly above average
- **45-55**: Average (typical population distribution)
- **40-45**: Slightly below average
- **0-40**: Below average genetic predisposition

### Important Caveats

1. **Polygenic Traits**: Most traits are influenced by hundreds to thousands of genetic variants. This analysis captures only known, validated variants.

2. **Small Effect Sizes**: Individual SNPs typically have small effects. Your score is a weighted aggregate.

3. **Environment Matters**: Genetics is only part of the story. Environment, lifestyle, and gene-environment interactions are critical.

4. **Ancestry Considerations**: Most GWAS studies were conducted in European populations. Results may not apply equally to all ancestries.

5. **Not Diagnostic**: This is for research and educational purposes only. Do not make medical decisions based on these results.

6. **Incomplete Coverage**: New genetic discoveries are published regularly. This database represents current knowledge but is not exhaustive.

## Customization

### Modify Category Colors

Edit `src/genegenie/visualization/trait_visualizer.py`:

```python
CATEGORY_INFO = {
    'cognition': {
        'emoji': '🧠',
        'color': '#6366f1',  # Change this hex color
        'light_color': '#e0e7ff',  # And the light variant
    },
    # ... other categories
}
```

### Adjust Scale Appearance

Modify the `create_scale_svg()` function to change:
- Scale width/height
- Tick mark positions
- Color thresholds
- Label text

### Custom Styling

The HTML report uses inline CSS. To customize:

1. Open `src/genegenie/visualization/trait_visualizer.py`
2. Find the `<style>` section in `generate_html_report()`
3. Modify CSS properties as desired

Example customizations:
```css
/* Make cards larger */
.trait-card {
    min-height: 400px;
}

/* Change grid columns */
.traits-grid {
    grid-template-columns: repeat(2, 1fr); /* Force 2 columns */
}

/* Adjust colors */
body {
    background: linear-gradient(135deg, #your-color-1 0%, #your-color-2 100%);
}
```

## Output Files

When you run trait analysis, you get:

1. **trait_report.html** - Interactive visual report (this feature!)
2. **trait_genetics_report.md** - Detailed markdown report with full variant information
3. **trait_variants.csv** - Raw variant data for further analysis
4. **trait_analysis_YYYYMMDD_HHMMSS.log** - Analysis log file

## Examples

### Example Output Structure

```
trait_results/
├── trait_report.html              # ← Open this in browser!
├── trait_genetics_report.md
├── trait_variants.csv
└── trait_analysis_20250126_143022.log
```

### Example Workflow

```bash
# 1. Run analysis
python examples/visual_trait_analysis.py data/genome.vcf.gz

# 2. Open HTML report in browser
open trait_results/trait_report.html

# 3. Explore your genetic traits visually!
#    - See scores at a glance
#    - Compare across categories
#    - Review top contributing variants

# 4. Dig deeper with markdown report
cat trait_results/trait_genetics_report.md

# 5. Analyze raw data
python
>>> import pandas as pd
>>> df = pd.read_csv('trait_results/trait_variants.csv')
>>> df[df['category'] == 'cognition']
```

## Technical Details

### SVG Scale Generation

The scale indicator is generated as inline SVG with:
- Background track (light gray)
- Center line at 50 (population average)
- Tick marks at 0 and 100
- Color-coded position marker
- Numeric score display

### Responsive Grid

The grid uses CSS Grid with `auto-fit` and `minmax()`:
```css
grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
```

This automatically adjusts to screen width while maintaining readable card sizes.

### Color Palette

Colors are chosen from the Tailwind CSS color palette for consistency and accessibility:
- Indigo: #6366f1
- Purple: #8b5cf6
- Red: #ef4444
- Amber: #f59e0b
- Emerald: #10b981
- Cyan: #06b6d4
- Pink: #ec4899

## Browser Compatibility

The HTML report works in all modern browsers:
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Opera 76+

No JavaScript required - pure HTML/CSS!

## Future Enhancements

Potential future additions:
- [ ] Interactive filtering by category
- [ ] Export to PDF
- [ ] Comparison mode (multiple genomes)
- [ ] Ancestry-adjusted scoring
- [ ] Integration with polygenic risk scores
- [ ] Downloadable variant report cards
- [ ] Dark mode toggle

## Troubleshooting

### "No module named 'visualization'"

Make sure you're importing from the correct path:
```python
from genegenie.visualization import create_visualization_from_analyzer
```

### HTML file is blank

Check that you ran the full analysis pipeline:
```python
analyzer.extract_all_trait_snps()
analyzer.calculate_category_scores()
analyzer.generate_visual_report()
```

### Scores all show 50

This means either:
1. No variants were extracted (check VCF file and index)
2. No effect size data in trait database
3. Variants weren't found in your genome

### Style not rendering

The CSS is inline, so it should always work. If not:
1. Check browser console for errors
2. Verify HTML file is complete (not truncated)
3. Try a different browser

## Questions?

For issues or questions about visual trait analysis:
1. Check the example scripts in `examples/`
2. Review the source code in `src/genegenie/visualization/`
3. Open an issue on GitHub

## See Also

- [Trait Database](../src/genegenie/utils/trait_db.py) - SNP database structure
- [Trait Analyzer](../src/genegenie/trait_analyzer.py) - Core analysis engine
- [Example Script](../examples/visual_trait_analysis.py) - Usage examples
