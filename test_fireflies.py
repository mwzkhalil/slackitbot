"""
Test script to verify Fireflies API connection.
Run this after adding FIREFLIES_API_KEY to .env
"""

import asyncio
import logging
from dotenv import load_dotenv
from src.utils.config import Config
from src.data_ingestion.fireflies_api import FirefliesAPI

# Load environment variables
load_dotenv()
logging.basicConfig(level=logging.INFO)

async def test_fireflies():
    print("=" * 60)
    print("Testing Fireflies API Connection")
    print("=" * 60)
    
    try:
        # Load config
        config = Config()
        
        if not config.fireflies_api_key:
            print("\n❌ ERROR: FIREFLIES_API_KEY not found in .env file")
            print("Please add your Fireflies API key to .env:")
            print("FIREFLIES_API_KEY=your-api-key-here")
            return
        
        print(f"\n✓ API Key found: {config.fireflies_api_key[:8]}...")
        
        # Initialize Fireflies API
        fireflies = FirefliesAPI(config.fireflies_api_key)
        print("✓ Fireflies API initialized")
        
        # Test fetching meetings
        print("\n[Testing] Fetching recent meetings (limit: 5)...")
        meetings = await fireflies.get_meetings(limit=5)
        
        print(f"\n✓ Successfully fetched {len(meetings)} meetings!")
        
        if meetings:
            print("\n" + "=" * 60)
            print("Sample Meeting Data:")
            print("=" * 60)
            
            for i, meeting in enumerate(meetings[:3], 1):  # Show first 3
                print(f"\n[Meeting {i}]")
                print(f"  Title: {meeting['title']}")
                print(f"  Date: {meeting['date']}")
                print(f"  Duration: {meeting.get('duration', 0)} minutes")
                print(f"  Participants: {', '.join(meeting.get('participants', []))}")
                print(f"  Transcript length: {len(meeting.get('transcript', ''))} chars")
                print(f"  Summary available: {'Yes' if meeting.get('summary') else 'No'}")
        else:
            print("\nℹ️  No meetings found. This could mean:")
            print("   - You haven't recorded any meetings yet")
            print("   - Your Fireflies bot hasn't joined any meetings")
            print("   - The API key doesn't have access to meetings")
        
        # Test recent meetings filter
        print("\n[Testing] Fetching meetings from last 7 days...")
        recent = await fireflies.get_recent_meetings(days=7)
        print(f"✓ Found {len(recent)} meetings from last 7 days")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nYour Fireflies integration is working correctly.")
        print("You can now run: python -m src.ingest")
        
    except ValueError as e:
        print(f"\n❌ Configuration Error: {str(e)}")
        print("Please check your .env file has all required variables.")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nPossible issues:")
        print("  1. Invalid API key")
        print("  2. Network connectivity problem")
        print("  3. Fireflies API is down")
        print("\nCheck your API key at: https://fireflies.ai/")

if __name__ == "__main__":
    asyncio.run(test_fireflies())
