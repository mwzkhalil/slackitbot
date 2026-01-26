"""
Configuration management for the AI Agent System.
Loads environment variables and provides centralized config.
"""

import os
from typing import Optional

class Config:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.slack_bot_token = os.getenv("SLACK_BOT_TOKEN")
        self.slack_signing_secret = os.getenv("SLACK_SIGNING_SECRET")
        self.fireflies_api_key = os.getenv("FIREFLIES_API_KEY")  # ENABLED for meeting transcripts
        # self.assemblyai_api_key = os.getenv("ASSEMBLYAI_API_KEY")  # COMMENTED OUT - Not used
        self.google_drive_credentials_path = os.getenv("GOOGLE_DRIVE_CREDENTIALS_PATH")
        # Google Custom Search API (optional - for Amazon queries)
        self.google_search_api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.google_search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        self.google_drive_folder_e_alex = os.getenv("GOOGLE_DRIVE_FOLDER_E_ALEX")
        self.google_drive_folder_e_lazar = os.getenv("GOOGLE_DRIVE_FOLDER_E_LAZAR")  # ENABLED for E-Lazar
        self.google_drive_folder_client_success = os.getenv("GOOGLE_DRIVE_FOLDER_CLIENT_SUCCESS")  # ENABLED for Client Success
        self.chroma_db_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
        # self.admin_password = os.getenv("ADMIN_PASSWORD")  # COMMENTED OUT - Not used

        # Validate required configs (E. Alex with Google Drive + Fireflies)
        # Note: E-Lazar and Client Success folders are optional
        required = [
            self.openai_api_key, self.slack_bot_token, self.slack_signing_secret,
            self.google_drive_credentials_path, self.google_drive_folder_e_alex
        ]
        if not all(required):
            raise ValueError("Missing required environment variables. Check .env file.")

    def get_drive_folder(self, agent: str, client_id: Optional[str] = None) -> str:
        if agent == "e_alex":
            return self.google_drive_folder_e_alex
        elif agent == "e_lazar":
            return self.google_drive_folder_e_lazar
        elif agent == "client_success":
            if not client_id:
                raise ValueError("Client ID required for client success agent")
            # Assume folder is per client, perhaps append client_id
            return f"{self.google_drive_folder_client_success}_{client_id}"
        else:
            raise ValueError("Unknown agent")