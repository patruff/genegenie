#!/usr/bin/env python3
"""
Sync PDFs from Google Drive to File Search Store (Genome Papers)

Automatically checks a Google Drive 'genomepapers' folder for new PDFs and uploads them
to the Google File Search RAG system. Tracks uploaded files to avoid duplicates.

Separate from longevitypdf - uses different folder and store for genome-specific papers.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Set, Dict, List
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
from google import genai

# Configuration
DRIVE_FOLDER_NAME = "genomepapers"
STATE_FILE = Path.home() / ".genome_papers_mcp" / "synced_files.json"
STORE_DISPLAY_NAME = "genomepapers"
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


def get_client() -> genai.Client:
    """Get or create the Google GenAI client."""
    api_key = os.getenv("GOOGLE_GENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "GOOGLE_GENAI_API_KEY environment variable not set. "
            "Get your API key from https://aistudio.google.com/apikey"
        )
    client = genai.Client(api_key=api_key)
    print("✅ Initialized Google GenAI client")
    return client


def get_or_create_store(client: genai.Client) -> str:
    """Get or create the genome papers file search store."""
    config_path = Path.home() / ".genome_papers_mcp" / "store_config.json"

    # Try to load from config
    if config_path.exists():
        try:
            with open(config_path) as f:
                config = json.load(f)
                store_name = config.get("store_name")
                if store_name:
                    print(f"📦 Using existing store: {store_name}")
                    return store_name
        except Exception as e:
            print(f"⚠️  Could not load store config: {e}")

    # Search for existing store by display name
    print(f"🔍 Searching for existing store with display name '{STORE_DISPLAY_NAME}'...")
    try:
        stores = client.file_search_stores.list()
        for store in stores:
            if hasattr(store, 'display_name') and store.display_name == STORE_DISPLAY_NAME:
                store_name = store.name
                print(f"✅ Found existing store: {store_name}")

                # Save config
                config_path.parent.mkdir(parents=True, exist_ok=True)
                with open(config_path, 'w') as f:
                    json.dump({"store_name": store_name, "display_name": STORE_DISPLAY_NAME}, f)

                return store_name
    except Exception as e:
        print(f"⚠️  Could not list stores: {e}")

    # Create new store
    print(f"🆕 Creating new file search store: {STORE_DISPLAY_NAME}")
    store = client.file_search_stores.create(display_name=STORE_DISPLAY_NAME)
    store_name = store.name
    print(f"✅ Created store: {store_name}")

    # Save config
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump({"store_name": store_name, "display_name": STORE_DISPLAY_NAME}, f)

    return store_name


def upload_pdf(client: genai.Client, store_name: str, file_path: str):
    """Upload a PDF to the file search store."""
    print(f"  📤 Uploading to File Search store...")

    operation = client.file_search_stores.upload_to_file_search_store(
        file_search_store_name=store_name,
        file=file_path
    )

    # Wait for upload to complete
    max_wait = 300  # 5 minutes
    start_time = time.time()

    while not operation.done:
        if time.time() - start_time > max_wait:
            raise TimeoutError("Upload timed out after 5 minutes")
        time.sleep(5)
        operation = client.operations.get(operation)

    print(f"  ✅ Upload complete")
    time.sleep(10)  # Wait to ensure document is queryable


def get_drive_service():
    """Initialize Google Drive API service using service account credentials."""
    creds_json = os.getenv("GOOGLE_DRIVE_CREDENTIALS")

    if not creds_json:
        raise ValueError(
            "GOOGLE_DRIVE_CREDENTIALS environment variable not set. "
            "This should contain your service account JSON credentials."
        )

    # Parse credentials from JSON string
    try:
        creds_info = json.loads(creds_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in GOOGLE_DRIVE_CREDENTIALS: {e}")

    # Create credentials from service account info
    credentials = service_account.Credentials.from_service_account_info(
        creds_info,
        scopes=SCOPES
    )

    # Build Drive API service
    service = build('drive', 'v3', credentials=credentials)
    print("✅ Connected to Google Drive API")

    return service


def find_folder(service, folder_name: str) -> str:
    """Find a folder by name and return its ID."""
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"

    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name)'
    ).execute()

    files = results.get('files', [])

    if not files:
        raise ValueError(f"Folder '{folder_name}' not found in Google Drive")

    if len(files) > 1:
        print(f"⚠️  Warning: Multiple folders named '{folder_name}' found. Using the first one.")

    folder_id = files[0]['id']
    print(f"📁 Found folder: {folder_name} (ID: {folder_id})")

    return folder_id


def list_pdfs_in_folder(service, folder_id: str) -> List[Dict[str, str]]:
    """List all PDF files in a Google Drive folder."""
    query = f"'{folder_id}' in parents and mimeType='application/pdf' and trashed=false"

    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name, size, modifiedTime)',
        orderBy='modifiedTime desc'
    ).execute()

    files = results.get('files', [])

    print(f"📄 Found {len(files)} PDF(s) in Google Drive folder")

    return files


def download_file(service, file_id: str, file_name: str, temp_dir: Path) -> Path:
    """Download a file from Google Drive to a temporary directory."""
    request = service.files().get_media(fileId=file_id)

    temp_path = temp_dir / file_name

    with io.FileIO(str(temp_path), 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                print(f"  📥 Downloading: {progress}%", end='\r')

    print(f"  ✅ Downloaded: {file_name}")
    return temp_path


def load_synced_files() -> Dict[str, str]:
    """Load the record of already synced files."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Could not load synced files state: {e}")
            return {}
    return {}


def save_synced_files(synced_files: Dict[str, str]):
    """Save the record of synced files."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(synced_files, f, indent=2)
    print(f"💾 Saved sync state to {STATE_FILE}")


def sync_pdfs():
    """Main sync function - check Drive folder and upload new PDFs."""
    print("🔄 Starting Google Drive → File Search sync (GENOME PAPERS)...")
    print("=" * 80)

    # Initialize Google Drive service
    print("\n📡 Connecting to Google Drive...")
    drive_service = get_drive_service()

    # Find the genomepapers folder
    folder_id = find_folder(drive_service, DRIVE_FOLDER_NAME)

    # List PDFs in the folder
    drive_pdfs = list_pdfs_in_folder(drive_service, folder_id)

    if not drive_pdfs:
        print("\nℹ️  No PDFs found in Google Drive folder")
        return

    # Load previously synced files
    synced_files = load_synced_files()
    print(f"\n📋 Previously synced: {len(synced_files)} file(s)")

    # Identify new files
    new_files = []
    for pdf in drive_pdfs:
        file_id = pdf['id']
        if file_id not in synced_files:
            new_files.append(pdf)

    if not new_files:
        print("\n✅ All PDFs are already synced. Nothing to do!")
        return

    print(f"\n🆕 Found {len(new_files)} new PDF(s) to upload:")
    for pdf in new_files:
        size_mb = int(pdf.get('size', 0)) / (1024 * 1024)
        print(f"  - {pdf['name']} ({size_mb:.2f} MB)")

    # Initialize File Search client
    print("\n📦 Initializing File Search...")
    fs_client = get_client()
    store_name = get_or_create_store(fs_client)

    # Create temp directory for downloads
    temp_dir = Path("/tmp/genome_pdf_sync")
    temp_dir.mkdir(exist_ok=True)

    # Process each new file
    print(f"\n🚀 Uploading {len(new_files)} new PDF(s) to File Search...")
    print("=" * 80)

    success_count = 0
    for i, pdf in enumerate(new_files, 1):
        file_id = pdf['id']
        file_name = pdf['name']

        print(f"\n[{i}/{len(new_files)}] Processing: {file_name}")

        try:
            # Download from Drive
            temp_path = download_file(drive_service, file_id, file_name, temp_dir)

            # Upload to File Search
            upload_pdf(fs_client, store_name, str(temp_path))

            # Mark as synced
            synced_files[file_id] = {
                'name': file_name,
                'synced_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'size': pdf.get('size', 0)
            }

            # Clean up temp file
            temp_path.unlink()

            success_count += 1
            print(f"  ✅ Successfully synced: {file_name}")

        except Exception as e:
            print(f"  ❌ Error syncing {file_name}: {e}")
            continue

    # Save updated sync state
    save_synced_files(synced_files)

    # Summary
    print("\n" + "=" * 80)
    print("📊 SYNC SUMMARY (GENOME PAPERS)")
    print("=" * 80)
    print(f"✅ Successfully synced: {success_count}/{len(new_files)} PDF(s)")
    print(f"📦 File Search Store: {store_name}")
    print(f"   Display Name: {STORE_DISPLAY_NAME}")
    print(f"📁 Google Drive Folder: {DRIVE_FOLDER_NAME}")
    print(f"💾 Sync State File: {STATE_FILE}")
    print("=" * 80)

    if success_count > 0:
        print("\n🎉 New genome papers are now available for querying!")

    return success_count


def main():
    """Entry point for the sync script."""
    try:
        sync_pdfs()
    except Exception as e:
        print(f"\n❌ Sync failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
