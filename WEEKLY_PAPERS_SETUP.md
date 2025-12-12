# Weekly Papers Fetcher - Setup Guide

This guide explains how to set up the automated weekly paper fetching system that downloads SNP genomics papers from NCBI PubMed and uploads them to Google Drive.

## Overview

The `fetch_weekly_papers.py` script automatically:
1. Searches PubMed for recent papers about SNPs in humans from top genomics journals
2. Downloads available open-access PDFs from PubMed Central
3. Uploads them to your Google Drive folder named "genomepapers"

The GitHub Action runs every Monday at 9 AM UTC, but can also be triggered manually.

## Prerequisites

1. **NCBI Account and API Key**
   - You need an NCBI account with an API key
   - The API key is already added to the repository secrets

2. **Google Service Account**
   - A Google Cloud service account with access to Google Drive
   - Service account JSON credentials

3. **Google Drive Folder**
   - A folder named "genomepapers" in Google Drive
   - The folder must be shared with the service account email

## GitHub Secrets Configuration

You need to set up the following secrets in your GitHub repository:

### 1. NCBI_EMAIL
Your email address registered with NCBI.

**How to add:**
- Go to: Settings → Secrets and variables → Actions → New repository secret
- Name: `NCBI_EMAIL`
- Value: Your NCBI email (e.g., `your.email@example.com`)

### 2. NCBI_API_KEY
Your NCBI API key for increased rate limits.

**How to get an API key:**
1. Log in to your NCBI account at https://www.ncbi.nlm.nih.gov/
2. Go to Settings → API Key Management
3. Create a new API key

**How to add to GitHub:**
- Go to: Settings → Secrets and variables → Actions → New repository secret
- Name: `NCBI_API_KEY`
- Value: Your API key (e.g., `abc123def456...`)

### 3. GOOGLE_DRIVE_CREDENTIALS
Your Google Cloud service account credentials in JSON format.

**How to create a service account:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Drive API:
   - Navigate to "APIs & Services" → "Library"
   - Search for "Google Drive API"
   - Click "Enable"
4. Create a service account:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "Service Account"
   - Fill in the details and click "Create"
   - Skip role assignment (optional for this use case)
   - Click "Done"
5. Generate a JSON key:
   - Click on the created service account
   - Go to "Keys" tab
   - Click "Add Key" → "Create new key"
   - Choose "JSON" format
   - Download the JSON file

**How to add to GitHub:**
- Go to: Settings → Secrets and variables → Actions → New repository secret
- Name: `GOOGLE_DRIVE_CREDENTIALS`
- Value: Paste the entire contents of the downloaded JSON file

### 4. Share Google Drive Folder with Service Account

After creating the service account, you need to share your Google Drive folder with it:

1. Open the JSON credentials file you downloaded
2. Find the `client_email` field (looks like `your-service@project-name.iam.gserviceaccount.com`)
3. In Google Drive, create a folder named `genomepapers` (if it doesn't exist)
4. Right-click the folder → Share
5. Add the service account email as an editor
6. Click "Send"

## Testing the Workflow

### Manual Trigger
You can manually trigger the workflow to test it:
1. Go to your repository on GitHub
2. Click on "Actions" tab
3. Select "Fetch Weekly Genomics Papers" from the left sidebar
4. Click "Run workflow" → "Run workflow"

### Check the Logs
1. After the workflow runs, click on the workflow run
2. Click on the "fetch-papers" job
3. Review the logs to see which papers were found and uploaded

## Customization

### Change the Schedule
Edit `.github/workflows/fetch_weekly_papers.yml`:
```yaml
schedule:
  # Current: Every Monday at 9 AM UTC
  - cron: '0 9 * * 1'

  # Examples:
  # Every day at midnight: '0 0 * * *'
  # Every Friday at 5 PM UTC: '0 17 * * 5'
  # Twice a week (Mon & Thu at 9 AM): '0 9 * * 1,4'
```

### Change the Search Query
Edit `fetch_weekly_papers.py`:
```python
SEARCH_TERM = '("Single Nucleotide Polymorphism"[Mesh] OR "SNP") AND "Human"[Mesh] AND ("PLoS Genetics"[Journal] OR "Genome Biology"[Journal] OR "Nature Communications"[Journal])'
```

### Change the Time Window
Edit `fetch_weekly_papers.py`:
```python
DAYS_BACK = 7  # Change to 14 for two weeks, 30 for a month, etc.
```

### Change the Target Folder
Edit `fetch_weekly_papers.py`:
```python
TARGET_FOLDER_NAME = "genomepapers"  # Change to your folder name
```

## Troubleshooting

### "Folder 'genomepapers' not found"
- Make sure the folder exists in Google Drive
- Verify it's shared with the service account email
- Check that the folder name matches exactly (case-sensitive)

### "No new papers found"
- This is normal if there are no matching papers in the time window
- Try increasing `DAYS_BACK` or broadening the search query

### "Failed to process PMC123456"
- Some papers may not have open-access PDFs available
- The script will skip these and continue with others

### Rate Limiting
- Using the NCBI API key allows up to 10 requests/second
- The script includes 1-second delays to be respectful
- If you hit rate limits, consider reducing `retmax` in the search

## Running Locally

You can also run the script locally for testing:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export NCBI_EMAIL="your.email@example.com"
export NCBI_API_KEY="your_api_key"

# Create service_account.json in the repo root with your credentials

# Run the script
python fetch_weekly_papers.py
```

## Security Notes

- Never commit `service_account.json` to the repository (it's in .gitignore)
- Keep your API keys secure in GitHub Secrets
- The workflow automatically cleans up the service account file after running
- Review the Google Cloud Console regularly to monitor API usage

## Support

For issues or questions:
1. Check the workflow logs in the Actions tab
2. Review the error messages in the output
3. Consult the NCBI E-utilities documentation: https://www.ncbi.nlm.nih.gov/books/NBK25501/
4. Check Google Drive API documentation: https://developers.google.com/drive/api/guides/about-sdk
