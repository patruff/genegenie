# Genome Papers RAG - MCP Server

🧬 **Query genomics research papers with AI-powered RAG (Retrieval Augmented Generation)**

An MCP (Model Context Protocol) server that provides intelligent search and question-answering capabilities over genomics research papers using Google's File Search Tool. Upload GWAS papers, SNP studies, trait genetics research, and get AI-generated answers with proper citations!

## 🌟 Features

- **📄 PDF Upload**: Upload genomics research papers to Google's File Search store
- **🔍 Intelligent Search**: Query papers using natural language questions
- **🧬 Genomics-Focused**: Optimized for GWAS, SNP, trait genetics, personality genetics
- **📚 Citation Support**: Get AI-generated answers with proper source citations
- **🔄 Google Drive Sync**: Automatically sync PDFs from `genomepapers` folder
- **📈 Usage Tracking**: Track indexed papers, total tokens, and estimated costs
- **💰 Cost Effective**: Storage FREE, Query embeddings FREE, Indexing $0.15 per 1M tokens
- **🔒 Separate Store**: Uses distinct "genomepapers" store (separate from longevitypdf)

## 📋 Prerequisites

- Python 3.10+
- Google GenAI API key ([Get one free here](https://aistudio.google.com/apikey))
- Claude Desktop (or any MCP-compatible client)

## 🛠️ Installation

### 1. Install Requirements

```bash
cd mcp_server
pip install -r requirements.txt
```

### 2. Get Google GenAI API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Click "Create API Key"
3. Copy your API key

### 3. Configure Claude Desktop

Add the MCP server to your Claude Desktop configuration:

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

**Important**: Replace `/absolute/path/to/genegenie/` with the actual absolute path!

### 4. Restart Claude Desktop

Close and reopen Claude Desktop. The server will now be available!

## 🎯 Available Tools

### 1. `upload_genome_paper`

Upload a genomics PDF research paper to the RAG system.

**Example:**
```
Upload ~/Documents/gwas_intelligence_2018.pdf to the system
```

### 2. `query_genome_papers`

Ask questions about the indexed papers in natural language.

**Example Questions:**
- "What SNPs are associated with intelligence in the latest GWAS?"
- "Which genes affect alcohol dependence?"
- "What are the APOE variants and their effects on Alzheimer's?"
- "Compare the genetics of extraversion vs neuroticism"
- "What are the top GWAS hits for educational attainment?"
- "Which SNPs affect caffeine metabolism?"

### 3. `list_indexed_genome_papers`

List all papers currently in the RAG system with statistics.

### 4. `get_genome_store_info`

Get information about the genome papers file search store.

### 5. `delete_genome_paper`

Delete a specific paper from the RAG system.

## 🔄 Google Drive Integration

Automatically sync PDFs from your Google Drive!

### Setup Google Drive Sync

1. **Create a Service Account** (see longevitypdf docs for details)
2. **Create `genomepapers` folder** in your Google Drive
3. **Share folder** with your service account email
4. **Add GitHub Secrets**:
   - `GOOGLE_DRIVE_CREDENTIALS`: Service account JSON
   - `GOOGLE_GENAI_API_KEY`: Your GenAI API key

### Usage

```bash
# Set environment variables
export GOOGLE_GENAI_API_KEY="your_key"
export GOOGLE_DRIVE_CREDENTIALS='{"type":"service_account",...}'

# Run sync
python mcp_server/sync_genome_drive_pdfs.py
```

PDFs in your `genomepapers` folder will be automatically uploaded to the RAG system!

## 💡 Usage Examples

### Upload Papers

```
Upload ~/papers/savage_2018_intelligence.pdf
Upload ~/papers/nagel_2018_neuroticism.pdf
Upload ~/papers/gelernter_2014_alcohol.pdf
```

### Query Papers

```
What SNPs are genome-wide significant for intelligence?
Which CHRNA5 variants affect nicotine dependence?
Compare FOXO3 variants for longevity across populations
What genes are in the MHC region for schizophrenia risk?
```

### Integration with GeneGenie

Once papers are indexed, you can:

1. **Extract SNPs**: Use GeneGenie's PDF parser to extract all rsIDs
2. **Query RAG**: Ask detailed questions about the papers
3. **Cross-Reference**: Match extracted SNPs with your genome
4. **Build Database**: Create custom trait SNP databases from papers

## 🏗️ Architecture

- **Separate Store**: Uses "genomepapers" store (distinct from "longevitypdf")
- **Config Path**: `~/.genome_papers_mcp/store_config.json`
- **Sync State**: `~/.genome_papers_mcp/synced_files.json`
- **Google File Search**: Automatic chunking, vector search, citations

## 📊 Pricing

| Operation | Cost |
|-----------|------|
| Storage | **FREE** |
| Query embeddings | **FREE** |
| Initial indexing | $0.15 per 1M tokens |

**Example**: A typical GWAS paper (30 pages) ≈ 15K tokens = **$0.00225 to index**

## 🔧 Integration with GeneGenie

The MCP server works seamlessly with GeneGenie's analysis tools:

```python
# After indexing papers via MCP, extract SNPs using GeneGenie
from genegenie.analysis.pdf_parser import extract_snps_from_pdf

# Extract SNPs from local PDF
data = extract_snps_from_pdf('paper.pdf')

# Then query the RAG system for detailed info
# (via Claude Desktop with MCP server)
```

## 📚 Recommended Papers

Upload these to build your genome RAG library:

### Intelligence & Cognition
- Savage et al. (2018) Nat Genet - Intelligence GWAS meta-analysis
- Hill et al. (2019) Mol Psychiatry - Cognitive function

### Personality
- Nagel et al. (2018) Nat Genet - Neuroticism (449k)
- van den Berg et al. (2016) Mol Psychiatry - Extraversion

### Addiction
- Gelernter et al. (2014) Mol Psychiatry - Alcohol dependence
- Tobacco Genetics Consortium (2010) Nat Genet - Nicotine

### Longevity
- Deelen et al. (2019) Nat Commun - Human longevity GWAS
- Timmers et al. (2019) eLife - Parental lifespan

## 🐛 Troubleshooting

### "GOOGLE_GENAI_API_KEY environment variable not set"
- Check your `claude_desktop_config.json`
- Restart Claude Desktop

### Papers not appearing in queries
- Wait 10-30 seconds after upload for indexing
- Use `list_indexed_genome_papers` to verify upload

### Separate from longevitypdf
- This uses a DIFFERENT store ("genomepapers" vs "longevitypdf")
- Papers uploaded here won't appear in longevitypdf queries
- This keeps genome papers separate for focused queries

## 📝 License

MIT License - See parent LICENSE file

---

**Built with ❤️ for genomics research**

*Part of the GeneGenie toolkit - Using Google's File Search Tool + MCP Protocol*
