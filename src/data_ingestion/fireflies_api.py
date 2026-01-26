"""
Fireflies API integration for retrieving meeting data.
Uses GraphQL API to fetch transcripts and summaries.
"""

import requests
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

class FirefliesAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.graphql_url = "https://api.fireflies.ai/graphql"
        
    async def get_meetings(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch recent meetings from Fireflies using GraphQL.
        Returns list of meetings with transcripts and metadata.
        """
        query = """
        query Transcripts($limit: Int!) {
          transcripts(limit: $limit) {
            id
            title
            date
            duration
            transcript_url
            audio_url
            video_url
            organizer_email
            participants
            summary {
              overview
              action_items
              keywords
            }
            sentences {
              text
              speaker_name
              speaker_id
            }
          }
        }
        """
        
        variables = {"limit": limit}
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query,
            "variables": variables
        }
        
        try:
            response = requests.post(
                self.graphql_url, 
                json=payload, 
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "errors" in data:
                    error_msg = data["errors"][0].get("message", "Unknown error")
                    raise Exception(f"GraphQL error: {error_msg}")
                
                transcripts = data.get("data", {}).get("transcripts", [])
                meetings = []
                
                for transcript in transcripts:
                    # Build full transcript text from sentences
                    full_transcript = ""
                    if transcript.get("sentences"):
                        for sentence in transcript["sentences"]:
                            speaker = sentence.get("speaker_name", "Unknown")
                            text = sentence.get("text", "")
                            full_transcript += f"{speaker}: {text}\n"
                    
                    # Build summary text
                    summary_parts = []
                    if transcript.get("summary"):
                        if transcript["summary"].get("overview"):
                            summary_parts.append(f"Overview: {transcript['summary']['overview']}")
                        if transcript["summary"].get("action_items"):
                            summary_parts.append(f"Action Items: {', '.join(transcript['summary']['action_items'])}")
                        if transcript["summary"].get("keywords"):
                            summary_parts.append(f"Keywords: {', '.join(transcript['summary']['keywords'])}")
                    
                    summary_text = "\n".join(summary_parts) if summary_parts else ""
                    
                    meetings.append({
                        "id": transcript.get("id", ""),
                        "title": transcript.get("title", "Untitled Meeting"),
                        "transcript": full_transcript.strip(),
                        "summary": summary_text,
                        "date": transcript.get("date", ""),
                        "duration": transcript.get("duration", 0),
                        "participants": transcript.get("participants", []),
                        "organizer": transcript.get("organizer_email", "")
                    })
                
                logging.info(f"Successfully fetched {len(meetings)} meetings from Fireflies")
                return meetings
            else:
                raise Exception(f"Failed to fetch meetings: {response.status_code} - {response.text}")
                
        except requests.exceptions.Timeout:
            raise Exception("Fireflies API request timed out")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error connecting to Fireflies: {str(e)}")
    
    async def get_recent_meetings(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Fetch meetings from the last N days.
        Filters client-side since Fireflies GraphQL doesn't support date filtering.
        """
        # Fetch meetings (limit to 50 to avoid API restrictions)
        all_meetings = await self.get_meetings(limit=50)
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_meetings = []
        
        for meeting in all_meetings:
            try:
                # Parse date - Fireflies returns Unix timestamp in milliseconds
                date_value = meeting["date"]
                
                # Handle both Unix timestamp (milliseconds) and ISO format
                if isinstance(date_value, (int, float)):
                    # Convert milliseconds to seconds for datetime
                    meeting_date = datetime.fromtimestamp(date_value / 1000)
                elif isinstance(date_value, str):
                    # Try parsing as ISO format
                    meeting_date = datetime.fromisoformat(date_value.replace("Z", "+00:00"))
                else:
                    # Unknown format, include the meeting to be safe
                    recent_meetings.append(meeting)
                    continue
                
                if meeting_date >= cutoff_date:
                    recent_meetings.append(meeting)
                    
            except (ValueError, KeyError, TypeError) as e:
                logging.warning(f"Could not parse date for meeting {meeting.get('title', 'unknown')}: {str(e)}")
                # Include the meeting anyway to be safe
                recent_meetings.append(meeting)
        
        logging.info(f"Filtered to {len(recent_meetings)} meetings from last {days} days")
        return recent_meetings