"""
Client Success Agent: Provides client-specific answers without mixing data.
Data sources: Google Drive + Fireflies meeting transcripts
"""

import logging
from typing import Optional
from src.utils.config import Config
from src.utils.database import get_vector_db
from src.utils.security import check_data_isolation
from src.llm.gpt_integration import GPTIntegration
from src.data_ingestion.google_drive import GoogleDriveAPI
from src.data_ingestion.fireflies_api import FirefliesAPI

class ClientSuccessAgent:
    def __init__(self, config: Config):
        self.config = config
        self.db = get_vector_db(config.chroma_db_path)
        self.llm = GPTIntegration(config.openai_api_key)
        self.drive = GoogleDriveAPI(config.google_drive_credentials_path)
        
        # Initialize Fireflies API if key is provided
        self.fireflies = None
        if config.fireflies_api_key:
            self.fireflies = FirefliesAPI(config.fireflies_api_key)
            logging.info("Client Success: Fireflies API initialized")
        else:
            logging.warning("Client Success: No Fireflies API key - meeting transcripts will not be synced")

    async def respond(self, query: str, client_id: Optional[str] = None) -> str:
        if not client_id:
            return "Client ID is required for this agent."
        
        filters = check_data_isolation("client_success", client_id)
        logging.info(f"Client Success querying with filters: {filters}")
        
        results = self.db.query(query, filters)
        context_docs = results.get("documents", [[]])[0] if results.get("documents") else []
        
        logging.info(f"Found {len(context_docs)} documents for query: {query}")
        
        # If no client-specific docs match, still answer from general best practices
        if not context_docs:
            logging.warning(
                f"No client-specific documents matched query '{query}' – "
                "answering from general client-success best practices."
            )
            context_docs = [
                "No client-specific documents matched this question. Answer using general "
                "client-success and account-management best practices, without exposing "
                "or inferring any other client's data."
            ]
        
        purpose = (
            "Answer questions related to client-specific documents and Fireflies meeting "
            "transcripts without mixing data across clients. When internal context is "
            "missing, answer using general client-success and account-management best "
            "practices while preserving data isolation."
        )
        return self.llm.generate_response(query, context_docs, purpose)

    async def ingest_data(self, client_id: str):
        """
        Ingest data from:
        1. Google Drive (client-specific folder)
        2. Fireflies (meeting transcripts if API key is configured)
        """
        logging.info("=" * 60)
        logging.info(f"Starting Client Success data ingestion for client: {client_id}")
        logging.info("=" * 60)
        
        total_ingested = 0
        
        # 1. Ingest from Google Drive
        logging.info("\n[1/2] Google Drive ingestion...")
        folder_id = self.config.get_drive_folder("client_success", client_id)
        logging.info(f"Google Drive folder ID: {folder_id}")
        
        try:
            files = await self.drive.get_files(folder_id, recursive=True)
            logging.info(f"Found {len(files)} files in Google Drive")
            
            drive_ingested = 0
            for file in files:
                try:
                    logging.info(f"Processing file: {file['name']} (ID: {file['id']})")
                    content = await self.drive.get_file_content(file["id"])
                    
                    if content and len(content.strip()) > 0:
                        metadata = {
                            "agent": "client_success",
                            "client_id": client_id,
                            "source": "drive",
                            "file_id": file["id"],
                            "name": file["name"]
                        }
                        doc_id = f"drive_{client_id}_{file['id']}"
                        self.db.add_documents([content], [metadata], [doc_id])
                        drive_ingested += 1
                        logging.info(f"✓ Ingested: {file['name']} ({len(content)} chars)")
                    else:
                        logging.warning(f"✗ Skipped (empty): {file['name']}")
                except Exception as e:
                    logging.error(f"✗ Error processing {file.get('name', 'unknown')}: {str(e)}")
            
            total_ingested += drive_ingested
            logging.info(f"Google Drive complete: {drive_ingested}/{len(files)} files ingested")
        except Exception as e:
            logging.error(f"Error during Google Drive ingestion: {str(e)}")
        
        # 2. Ingest from Fireflies
        if self.fireflies:
            logging.info("\n[2/2] Fireflies meeting transcripts ingestion...")
            try:
                meetings = await self.fireflies.get_recent_meetings(days=30)
                logging.info(f"Found {len(meetings)} meetings from Fireflies")
                
                fireflies_ingested = 0
                for meeting in meetings:
                    try:
                        content_parts = []
                        content_parts.append(f"Meeting Title: {meeting['title']}")
                        content_parts.append(f"Date: {meeting['date']}")
                        if meeting.get('participants'):
                            content_parts.append(f"Participants: {', '.join(meeting['participants'])}")
                        content_parts.append(f"Duration: {meeting.get('duration', 0)} minutes")
                        content_parts.append("")
                        
                        if meeting.get('summary'):
                            content_parts.append("=== Summary ===")
                            content_parts.append(meeting['summary'])
                            content_parts.append("")
                        
                        if meeting.get('transcript'):
                            content_parts.append("=== Transcript ===")
                            content_parts.append(meeting['transcript'])
                        
                        content = "\n".join(content_parts)
                        
                        if content and len(content.strip()) > 0:
                            metadata = {
                                "agent": "client_success",
                                "client_id": client_id,
                                "source": "fireflies",
                                "meeting_id": meeting["id"],
                                "title": meeting["title"],
                                "date": meeting["date"]
                            }
                            doc_id = f"fireflies_client_{client_id}_{meeting['id']}"
                            self.db.add_documents([content], [metadata], [doc_id])
                            fireflies_ingested += 1
                            logging.info(f"✓ Ingested meeting: {meeting['title']} ({len(content)} chars)")
                        else:
                            logging.warning(f"✗ Skipped (empty): {meeting['title']}")
                    except Exception as e:
                        logging.error(f"✗ Error processing meeting {meeting.get('title', 'unknown')}: {str(e)}")
                
                total_ingested += fireflies_ingested
                logging.info(f"Fireflies complete: {fireflies_ingested}/{len(meetings)} meetings ingested")
            except Exception as e:
                logging.error(f"Error during Fireflies ingestion: {str(e)}")
        else:
            logging.info("\n[2/2] Fireflies skipped (no API key configured)")
        
        logging.info("\n" + "=" * 60)
        logging.info(f"Client Success ({client_id}) INGESTION COMPLETE! Total: {total_ingested}")
        logging.info("=" * 60)