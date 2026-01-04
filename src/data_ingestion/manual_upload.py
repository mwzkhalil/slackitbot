"""
Manual upload handling for admin uploads.
Supports text files and audio files (transcribed via AssemblyAI).
"""

import os
import shutil
from typing import Optional
from src.utils.config import Config
from src.utils.database import get_vector_db
from src.data_ingestion.transcription_api import TranscriptionAPI

UPLOAD_DIR = "uploads"

async def handle_manual_upload(agent: str, file, client_id: Optional[str], config: Config) -> str:
    """
    Handle manual file upload, save to disk, transcribe if audio, and index in DB.
    """
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    content = ""
    mime_type = file.content_type or ""

    if mime_type.startswith("audio/") or file.filename.lower().endswith(('.mp3', '.wav', '.m4a', '.flac')):
        # Transcribe audio
        transcriber = TranscriptionAPI(config.assemblyai_api_key)
        transcript = await transcriber.transcribe_audio(file_path)
        if transcript:
            content = transcript
        else:
            return f"Failed to transcribe {file.filename}."
    else:
        # Assume text file
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            return f"File {file.filename} is not a readable text or audio file."

    db = get_vector_db(config.chroma_db_path)
    metadata = {"agent": agent, "source": "manual", "file_name": file.filename}
    if agent == "client_success" and client_id:
        metadata["client_id"] = client_id

    doc_id = f"manual_{agent}_{file.filename}"
    db.add_documents([content], [metadata], [doc_id])

    return f"File {file.filename} uploaded and indexed for {agent}."