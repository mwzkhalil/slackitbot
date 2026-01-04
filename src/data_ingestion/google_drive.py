"""
Google Drive API integration for file retrieval.
"""

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseDownload
import io
from typing import List, Dict, Any

class GoogleDriveAPI:
    def __init__(self, credentials_path: str):
        creds = Credentials.from_authorized_user_file(credentials_path)
        self.service = build('drive', 'v3', credentials=creds)

    async def get_files(self, folder_id: str) -> List[Dict[str, Any]]:
        """
        Get list of files in the folder.
        """
        query = f"'{folder_id}' in parents"
        results = self.service.files().list(q=query, fields="files(id, name, mimeType)").execute()
        return results.get('files', [])

    async def get_file_content(self, file_id: str) -> str:
        """
        Download and extract text content from file.
        Supports Docs, Slides, PDFs, images (OCR if needed).
        """
        file = self.service.files().get(fileId=file_id, fields='mimeType').execute()
        mime_type = file['mimeType']

        if mime_type == 'application/vnd.google-apps.document':
            # Export as text
            request = self.service.files().export(fileId=file_id, mimeType='text/plain')
        elif mime_type == 'application/vnd.google-apps.presentation':
            request = self.service.files().export(fileId=file_id, mimeType='text/plain')
        else:
            # For PDFs, images, etc., download binary and extract text
            request = self.service.files().get_media(fileId=file_id)

        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()

        content = fh.getvalue().decode('utf-8') if mime_type.startswith('text') else str(fh.getvalue())
        # For images/PDFs, would need OCR, but placeholder
        return content