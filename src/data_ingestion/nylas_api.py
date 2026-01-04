"""
Nylas API integration for calendar events (meetings metadata).
Free tier available.
"""

from nylas import APIClient
from typing import List, Dict, Any, Optional

class NylasAPI:
    def __init__(self, access_token: str, client_id: str = None, client_secret: str = None):
        if client_id and client_secret:
            self.client = APIClient(
                client_id=client_id,
                client_secret=client_secret,
                access_token=access_token
            )
        else:
            # For Nylas v3, can initialize with just access_token
            self.client = APIClient(access_token=access_token)

    async def get_calendar_events(self, calendar_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch recent calendar events (meetings).
        """
        try:
            if calendar_id:
                events = self.client.events.where(calendar_id=calendar_id).get(limit=limit)
            else:
                # Get from primary calendar
                calendars = self.client.calendars.all()
                if calendars:
                    primary_cal = calendars[0]
                    events = self.client.events.where(calendar_id=primary_cal.id).get(limit=limit)
                else:
                    return []

            meeting_events = []
            for event in events:
                if event.when and hasattr(event.when, 'start_time'):  # Assuming it's a meeting
                    meeting_events.append({
                        "id": event.id,
                        "title": event.title,
                        "description": event.description or "",
                        "start_time": event.when.start_time,
                        "participants": [p['email'] for p in event.participants] if event.participants else [],
                        "location": event.location or ""
                    })
            return meeting_events
        except Exception as e:
            print(f"Nylas API error: {str(e)}")
            return []