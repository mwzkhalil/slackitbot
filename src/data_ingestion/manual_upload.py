"""
Manual upload handling for admin uploads.
"""

import os
import shutil
from typing import Optional
from src.utils.config import Config
from src.utils.database import get_vector_db

UPLOAD_DIR = "uploads"

async def handle_manual_upload(agent: str, file, client_id: Optional[str], config: Config) -> str:
    """
    Handle manual file upload, save to disk, and index in DB.
    """
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Read content (assume text for simplicity)
    with open(file_path, "r") as f:
        content = f.read()

    db = get_vector_db(config.chroma_db_path)
    metadata = {"agent": agent, "source": "manual", "file_name": file.filename}
    if agent == "client_success" and client_id:
        metadata["client_id"] = client_id

    doc_id = f"manual_{agent}_{file.filename}"
    db.add_documents([content], [metadata], [doc_id])

    return f"File {file.filename} uploaded and indexed for {agent}."