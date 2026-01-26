# Fireflies API Setup Guide

## Getting Your Fireflies API Key

### Step 1: Sign Up for Fireflies
1. Go to [Fireflies.ai](https://fireflies.ai/)
2. Sign up for an account or log in if you already have one
3. Fireflies offers a free tier with limited transcription hours

### Step 2: Get Your API Key
1. Log in to your Fireflies account
2. Click on your profile icon in the top right
3. Go to **Settings** → **Integrations** → **API**
4. Click on **Generate New API Key** or copy your existing key
5. Save this key securely - you'll need it for configuration

### Step 3: GraphQL API Endpoint
Fireflies uses GraphQL API. The endpoint is:
```
https://api.fireflies.ai/graphql
```

## Fireflies API Capabilities

Fireflies can:
- **Auto-join meetings**: Automatically join and record Zoom, Google Meet, Microsoft Teams meetings
- **Transcribe meetings**: Convert audio to text with speaker identification
- **Generate summaries**: AI-powered meeting summaries and action items
- **Search transcripts**: Search across all your meeting transcripts
- **Extract insights**: Identify key topics, questions, and action items

## What Data You Can Access

The Fireflies API provides:
- Meeting transcripts with speaker labels
- Meeting summaries
- Action items and key topics
- Meeting metadata (date, duration, participants)
- Audio recordings (if enabled)

## Integration Flow for Slackitbot

1. **Scheduled Sync**: Your bot will periodically fetch new meeting transcripts
2. **Ingestion**: Transcripts are added to ChromaDB with `{"agent": "e_alex", "source": "fireflies"}`
3. **Query**: E. Alex can answer questions based on meeting content
4. **Examples**:
   - "What was discussed in yesterday's meeting?"
   - "What action items came from the sales call?"
   - "Summarize meetings from last week"

## Rate Limits

Check the current Fireflies API documentation for rate limits. Typical limits:
- Free tier: ~5-10 hours of transcription/month
- API calls: Usually generous (e.g., 1000 requests/day)

## Next Steps

After getting your API key:
1. Add `FIREFLIES_API_KEY` to your `.env` file
2. Run the code updates (already prepared for you)
3. Test the integration: `python test_fireflies.py` (we'll create this)
4. Run ingestion: `python -m src.ingest`
5. Ask E. Alex about meeting content in Slack!
