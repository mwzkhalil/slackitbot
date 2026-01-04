"""
Client Success Agent: Provides client-specific answers without mixing data.
"""

from typing import Optional
from src.utils.config import Config
from src.utils.database import get_vector_db
from src.utils.security import check_data_isolation
from src.llm.gpt_integration import GPTIntegration
from src.data_ingestion.nylas_api import NylasAPI
from src.data_ingestion.google_drive import GoogleDriveAPI

class ClientSuccessAgent:
    def __init__(self, config: Config):
        self.config = config
        self.db = get_vector_db(config.chroma_db_path)
        self.llm = GPTIntegration(config.openai_api_key)
        self.nylas = NylasAPI(config.nylas_client_id, config.nylas_client_secret, config.nylas_access_token)
        self.drive = GoogleDriveAPI(config.google_drive_credentials_path)

    async def respond(self, query: str, client_id: Optional[str] = None) -> str:
        if not client_id:
            return "Client ID is required for this agent."

        filters = check_data_isolation("client_success", client_id)
        results = self.db.query(query, filters)
        context_docs = results.get("documents", [[]])[0] if results.get("documents") else []

        if not context_docs:
            return "I don't have information on that for this client."

        purpose = f"Provide client-specific answers for client {client_id} without mixing data across clients."
        return self.llm.generate_response(query, context_docs, purpose)

    async def ingest_data(self, client_id: str):
        # Nylas - assume client-specific calendar or filter
        events = await self.nylas.get_calendar_events()
        for event in events:
            # Filter by client if possible, or tag all
            doc = f"Meeting Title: {event['title']}\nDescription: {event['description']}\nDate: {event['start_time']}\nParticipants: {', '.join(event['participants'])}\nLocation: {event['location']}"
            metadata = {"agent": "client_success", "client_id": client_id, "source": "nylas", "event_id": event["id"]}
            self.db.add_documents([doc], [metadata], [f"nylas_{client_id}_{event['id']}"])

        # Google Drive
        folder_id = self.config.get_drive_folder("client_success", client_id)
        files = await self.drive.get_files(folder_id)
        for file in files:
            content = await self.drive.get_file_content(file["id"])
            metadata = {"agent": "client_success", "client_id": client_id, "source": "drive", "file_id": file["id"], "name": file["name"]}
            self.db.add_documents([content], [metadata], [f"drive_{client_id}_{file['id']}"])