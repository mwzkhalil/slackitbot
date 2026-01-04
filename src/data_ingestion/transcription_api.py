"""
Transcription API using AssemblyAI (free tier available).
For transcribing audio files uploaded manually.
"""

import assemblyai as aai
from typing import Optional

class TranscriptionAPI:
    def __init__(self, api_key: str):
        aai.settings.api_key = api_key
        self.transcriber = aai.Transcriber()

    async def transcribe_audio(self, audio_file_path: str) -> Optional[str]:
        """
        Transcribe an audio file and return the transcript.
        """
        try:
            transcript = self.transcriber.transcribe(audio_file_path)
            if transcript.status == aai.TranscriptStatus.error:
                raise Exception(f"Transcription error: {transcript.error}")
            return transcript.text
        except Exception as e:
            print(f"Transcription failed: {str(e)}")
            return None