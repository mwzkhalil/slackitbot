"""
Test script to verify Google Drive folder access for service account.
"""

import asyncio
import logging
from dotenv import load_dotenv
from src.utils.config import Config
from src.data_ingestion.google_drive import GoogleDriveAPI
import json
import os

load_dotenv()
logging.basicConfig(level=logging.INFO)

async def test_folder_access():
    config = Config()
    
    # Get service account email
    creds_path = config.google_drive_credentials_path
    with open(creds_path) as f:
        creds_data = json.load(f)
        service_email = creds_data.get('client_email')
        print("=" * 60)
        print("Google Drive Folder Access Test")
        print("=" * 60)
        print(f"\nService Account Email: {service_email}")
        print("\nThis is the email you need to share the folders with.\n")
    
    drive = GoogleDriveAPI(creds_path)
    
    # Test E. Lazar folder
    print("=" * 60)
    print("Testing E. Lazar Folder")
    print("=" * 60)
    folder_id = config.google_drive_folder_e_lazar
    print(f"Folder ID: {folder_id}")
    
    try:
        # Try to get folder info
        folder_info = drive.service.files().get(
            fileId=folder_id, 
            fields='id, name, mimeType'
        ).execute()
        print(f"✓ SUCCESS! Folder found: {folder_info.get('name')}")
        print(f"  Folder ID: {folder_info.get('id')}")
        
        # Try to list files
        files = await drive.get_files(folder_id, recursive=True)
        print(f"  Found {len(files)} files in folder")
        
        if files:
            print("\n  Sample files:")
            for file in files[:5]:
                print(f"    - {file.get('name')} ({file.get('mimeType')})")
        else:
            print("  ⚠️  Folder is empty or no files found")
            
    except Exception as e:
        error_str = str(e)
        print(f"✗ ERROR: {error_str}")
        if "404" in error_str or "notFound" in error_str:
            print("\n  ❌ The folder is NOT accessible to the service account!")
            print(f"\n  SOLUTION: Share the folder with this email:")
            print(f"  {service_email}")
            print("\n  Steps:")
            print("  1. Open the folder in Google Drive")
            print("  2. Click 'Share' button (top right)")
            print(f"  3. Add this email: {service_email}")
            print("  4. Set permission to 'Viewer'")
            print("  5. Click 'Share' or 'Done'")
            print("\n  After sharing, wait a few seconds and run this test again.")
        else:
            print(f"\n  Unexpected error: {e}")
    
    # Test E. Alex folder
    print("\n" + "=" * 60)
    print("Testing E. Alex Folder")
    print("=" * 60)
    folder_id = config.google_drive_folder_e_alex
    print(f"Folder ID: {folder_id}")
    
    try:
        folder_info = drive.service.files().get(
            fileId=folder_id, 
            fields='id, name, mimeType'
        ).execute()
        print(f"✓ SUCCESS! Folder found: {folder_info.get('name')}")
        
        files = await drive.get_files(folder_id, recursive=True)
        print(f"  Found {len(files)} files in folder")
        
    except Exception as e:
        error_str = str(e)
        print(f"✗ ERROR: {error_str}")
        if "404" in error_str or "notFound" in error_str:
            print(f"\n  ❌ Share this folder with: {service_email}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_folder_access())
