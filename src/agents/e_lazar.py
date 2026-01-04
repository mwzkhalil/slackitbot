"""
E. Lazar Agent: Handles internal questions on SOPs, onboarding, policies, workflows.
"""

from typing import Optional
from src.utils.config import Config
from src.utils.database import get_vector_db
from src.utils.security import check_data_isolation
from src.llm.gpt_integration import GPTIntegration
from src.data_ingestion.google_drive import GoogleDriveAPI

class ELazarAgent:
    def __init__(self, config: Config):
        self.config = config
        self.db = get_vector_db(config.chroma_db_path)
        self.llm = GPTIntegration(config.openai_api_key)
        self.drive = GoogleDriveAPI(config.google_drive_credentials_path)

    async def respond(self, query: str, client_id: Optional[str] = None) -> str:
        filters = check_data_isolation("e_lazar")
        results = self.db.query(query, filters)
        context_docs = results.get("documents", [[]])[0] if results.get("documents") else []

        if not context_docs:
            return "I don't have information on that."

        purpose = "Answer internal questions related to SOPs, onboarding material, policies, and internal workflows."
        return self.llm.generate_response(query, context_docs, purpose)

    async def ingest_data(self):
        folder_id = self.config.google_drive_folder_e_lazar
        files = await self.drive.get_files(folder_id)
        for file in files:
            content = await self.drive.get_file_content(file["id"])
            metadata = {"agent": "e_lazar", "source": "drive", "file_id": file["id"], "name": file["name"]}
            self.db.add_documents([content], [metadata], [f"drive_{file['id']}"])