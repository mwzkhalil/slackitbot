"""
Fireflies API integration for retrieving meeting data.
"""

import requests
from typing import List, Dict, Any, Optional

class FirefliesAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.fireflies.ai/v1"  # Assuming endpoint

    async def get_meetings(self, client_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch meetings from Fireflies.
        If client_id, filter by client.
        """
        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {}
        if client_id:
            params["client_id"] = client_id

        response = requests.get(f"{self.base_url}/meetings", headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            meetings = []
            for meeting in data.get("meetings", []):
                # Assuming structure
                meetings.append({
                    "id": meeting["id"],
                    "transcript": meeting.get("transcript", ""),
                    "summary": meeting.get("summary", ""),
                    "date": meeting.get("date", ""),
                    "participants": meeting.get("participants", [])
                })
            return meetings
        else:
            raise Exception(f"Failed to fetch meetings: {response.text}")

    # For incremental sync, perhaps get since last sync
    async def get_recent_meetings(self, since: str) -> List[Dict[str, Any]]:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {"since": since}
        response = requests.get(f"{self.base_url}/meetings", headers=headers, params=params)
        # Similar to above