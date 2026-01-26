"""Test Google Drive access"""
import asyncio
from dotenv import load_dotenv
from src.utils.config import Config
from src.data_ingestion.google_drive import GoogleDriveAPI

load_dotenv()

async def test_drive():
    config = Config()
    drive = GoogleDriveAPI(config.google_drive_credentials_path)
    folder_id = config.google_drive_folder_e_alex
    
    print(f"Testing access to folder: {folder_id}")
    print(f"Service account should be: ai-agent-service-account@sodium-atrium-484107-u0.iam.gserviceaccount.com")
    print("\n" + "="*80)
    
    try:
        # Test folder access
        folder_info = drive.service.files().get(fileId=folder_id, fields='name,id,mimeType').execute()
        print(f"✓ Folder found: {folder_info['name']}")
        print(f"  ID: {folder_info['id']}")
        print(f"  Type: {folder_info['mimeType']}")
        
        # Get files and folders recursively
        print(f"\n" + "="*80)
        print("Fetching files (with recursive=True)...")
        files = await drive.get_files(folder_id, recursive=True)
        print(f"✓ Found {len(files)} total files")
        
        if files:
            print("\nFiles found:")
            for i, file in enumerate(files[:10], 1):  # Show first 10
                print(f"  {i}. {file['name']} (Type: {file['mimeType']})")
            if len(files) > 10:
                print(f"  ... and {len(files) - 10} more files")
        else:
            print("\n⚠ No files found!")
            print("\nPossible reasons:")
            print("  1. The folder is empty")
            print("  2. The folder has subfolders but no files directly in them")
            print("  3. The service account doesn't have access to the folder")
            
            print("\n Checking direct folder contents...")
            query = f"'{folder_id}' in parents and trashed=false"
            results = drive.service.files().list(
                q=query,
                fields="files(id, name, mimeType)",
                pageSize=1000
            ).execute()
            items = results.get('files', [])
            print(f"  Direct items in folder: {len(items)}")
            for item in items:
                print(f"    - {item['name']} ({item['mimeType']})")
                
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        print("\nMake sure you:")
        print("  1. Shared the folder with: ai-agent-service-account@sodium-atrium-484107-u0.iam.gserviceaccount.com")
        print("  2. Gave at least 'Viewer' permissions")
        print("  3. Used the correct folder ID")

if __name__ == "__main__":
    asyncio.run(test_drive())
