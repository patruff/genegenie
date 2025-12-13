#!/usr/bin/env python3
"""
Weekly NCBI Paper Fetcher
Searches PubMed for recent SNP genomics papers and uploads PDFs to Google Drive.
"""
import os
import time
import json
import requests
from Bio import Entrez
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- CONFIGURATION ---
# We now only need email and API key from env. Folder ID is found dynamically.
EMAIL = os.environ.get("NCBI_EMAIL", "")
API_KEY = os.environ.get("NCBI_API_KEY", "")
SA_KEY_FILE = "service_account.json"
TARGET_FOLDER_NAME = "genomepapers"

# NCBI Setup
Entrez.email = EMAIL
Entrez.api_key = API_KEY
SEARCH_TERM = '("Single Nucleotide Polymorphism"[Mesh] OR "SNP") AND "Human"[Mesh] AND ("PLoS Genetics"[Journal] OR "Genome Biology"[Journal] OR "Nature Communications"[Journal])'
DAYS_BACK = 7

def get_drive_service():
    """Authenticate and return the Drive service."""
    creds = service_account.Credentials.from_service_account_file(
        SA_KEY_FILE, scopes=['https://www.googleapis.com/auth/drive']
    )
    return build('drive', 'v3', credentials=creds)

def get_folder_id(service, folder_name):
    """Finds the ID of the folder by name."""
    # Search for non-trashed folders with the specific name
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    files = results.get('files', [])

    if not files:
        raise FileNotFoundError(
            f"Folder '{folder_name}' not found. Did you share it with the Service Account email?"
        )

    # If duplicates exist, we take the first one found
    print(f"Found folder '{folder_name}' with ID: {files[0]['id']}")
    return files[0]['id']

def file_exists_in_drive(service, folder_id, filename):
    """Check if file already exists in the target folder."""
    query = f"name = '{filename}' and '{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    return len(results.get('files', [])) > 0

def upload_to_drive(service, folder_id, filepath, filename):
    """Uploads the file to the specific Google Drive folder."""
    if file_exists_in_drive(service, folder_id, filename):
        print(f"File {filename} already exists in Drive. Skipping upload.")
        return

    print(f"Uploading {filename}...")
    file_metadata = {'name': filename, 'parents': [folder_id]}
    media = MediaFileUpload(filepath, resumable=True)
    service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print("Upload complete.")

def get_recent_pmcids(days):
    """Search PubMed for recent papers and return PMC IDs."""
    print(f"Searching PubMed for papers from the last {days} days...")
    try:
        handle = Entrez.esearch(
            db="pubmed", term=SEARCH_TERM, reldate=days, datetype="pdat", retmax=50, usehistory="y"
        )
        results = Entrez.read(handle)
        handle.close()
    except Exception as e:
        print(f"Error searching PubMed: {e}")
        return []

    if not results["IdList"]:
        print("No new papers found.")
        return []

    id_list = results["IdList"]
    handle = Entrez.efetch(db="pubmed", id=id_list, retmode="xml")
    papers = Entrez.read(handle)
    handle.close()

    pmc_ids = []
    for paper in papers['PubmedArticle']:
        article_ids = paper['PubmedData']['ArticleIdList']
        for aid in article_ids:
            if aid.attributes.get('IdType') == 'pmc':
                pmc_ids.append(aid)
                break
    return pmc_ids

def get_pdf_url(pmc_id):
    """Ask the PMC OA API for the PDF URL."""
    base_url = "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi"
    try:
        resp = requests.get(base_url, params={'id': pmc_id})
        if resp.status_code == 200 and 'format="pdf"' in resp.text:
            start = resp.text.find('href="', resp.text.find('format="pdf"')) + 6
            end = resp.text.find('"', start)
            return resp.text[start:end]
    except Exception:
        pass
    return None

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # 1. Setup Drive
    drive_service = get_drive_service()
    try:
        target_folder_id = get_folder_id(drive_service, TARGET_FOLDER_NAME)
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        exit(1)

    # 2. Get Papers
    pmcids = get_recent_pmcids(DAYS_BACK)

    if not os.path.exists("temp_pdfs"):
        os.makedirs("temp_pdfs")

    print(f"Found {len(pmcids)} potential OA papers.")

    for pmcid in pmcids:
        pdf_link = get_pdf_url(pmcid)
        if pdf_link:
            if pdf_link.startswith("ftp://"):
                pdf_link = pdf_link.replace("ftp://", "https://")

            filename = f"{pmcid}.pdf"
            local_path = os.path.join("temp_pdfs", filename)

            try:
                # Download locally
                print(f"Downloading {pmcid}...")
                r = requests.get(pdf_link, stream=True)
                with open(local_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk: f.write(chunk)

                # Upload to Drive using the dynamic folder ID
                upload_to_drive(drive_service, target_folder_id, local_path, filename)

                os.remove(local_path)
            except Exception as e:
                print(f"Failed to process {pmcid}: {e}")

            time.sleep(1)
        else:
            print(f"No PDF URL for {pmcid}")

    print("Job complete.")
