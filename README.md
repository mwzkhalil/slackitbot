# Slackitbot - E. Alex AI Agent

A simplified RAG (Retrieval Augmented Generation) system that provides one AI agent (E. Alex) responding to Slack mentions using Google Drive documents.

## Overview

**E. Alex** answers questions from documents stored in your Google Drive folder: `My Drive/AI/e-ALex`

### Data Sources
- **Google Drive**: Documents from `My Drive/AI/e-ALex` including all subfolders:
  - Internal Meetings (Final)
  - Linkedin Videos Transcripts
  - Monthly 1-2-1 (Final)
  - Sale (Final)
- **Fireflies** (Optional): Meeting transcripts automatically synced from your Fireflies account
- **Supported File Types**: Google Docs, Google Slides, Google Sheets, .docx, .pptx, .pdf, text files
- **LLM**: GPT-4 for response generation
- **Vector Database**: ChromaDB for document indexing and semantic search

## Quick Start

### Prerequisites
- Python 3.8+
- Google Cloud account with Drive API enabled
- Slack workspace with bot permissions
- OpenAI API key

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/mwzkhalil/slackitbot/
cd slackitbot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials
```

Required variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `SLACK_BOT_TOKEN`: Slack bot OAuth token (starts with `xoxb-`)
- `SLACK_SIGNING_SECRET`: Slack app signing secret
- `GOOGLE_DRIVE_CREDENTIALS_PATH`: Path to service account JSON file
- `GOOGLE_DRIVE_FOLDER_E_ALEX`: Google Drive folder ID

Optional variables:
- `FIREFLIES_API_KEY`: Fireflies API key for meeting transcript sync (see [FIREFLIES_SETUP.md](FIREFLIES_SETUP.md))

### Google Drive Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable the **Google Drive API**
4. Create credentials:
   - Type: **Service Account**
   - Role: **Viewer** or **Editor** (for read access)
   - Create and download JSON key file
5. Save the JSON file to your project directory
6. Update `GOOGLE_DRIVE_CREDENTIALS_PATH` in `.env`
7. **Share your Google Drive folder** with the service account email (found in the JSON file)
8. Get the folder ID from the Drive URL: `https://drive.google.com/drive/folders/FOLDER_ID`
9. Update `GOOGLE_DRIVE_FOLDER_E_ALEX` in `.env`

### Slack Setup

1. Go to [Slack API](https://api.slack.com/apps) and create a new app
2. Choose "From scratch"
3. Add **Bot Token Scopes**:
   - `app_mentions:read`
   - `channels:history`
   - `chat:write`
4. Enable **Event Subscriptions**:
   - Subscribe to `app_mention` event
   - Request URL: `https://your-domain.com/slack/events` (use ngrok for local testing)
5. Install app to workspace
6. Copy **Bot User OAuth Token** → `SLACK_BOT_TOKEN` in `.env`
7. Copy **Signing Secret** → `SLACK_SIGNING_SECRET` in `.env`
8. Create a Slack channel (e.g., `#e-alex`) and invite the bot
9. GFireflies Setup (Optional)

To enTest Fireflies connection (if using Fireflies)**
```bash
python test_fireflies.py
```

2. **Ingest data from Google Drive and Fireflies**
```bash
python -m src.ingest
```

3. Test connection: `python test_fireflies.py`
5. Meetings will be automatically synced during data ingestion
4
### et channel ID from URL: `https://slack.com/archives/CHANNEL_ID`
10. Update channel ID in [src/slack/slack_integration.py](src/slack/slack_integration.py#L77)

### Running the System

1. **Ingest data from Google Drive**
```bash
python -m src.ingest
```
5
2. **Start the server**
```bash
python -m src.main
# Or with auto-reload:
uvicorn src.main:app --reload --host 0.0.0.0 --port 5001
```

3. **For local development with Slack (using ngrok)**
```bash
# In another terminal:
ngrok http 5001
# Update Slack Event Subscriptions URL to: https://your-ngrok-url.ngrok.io/slack/events
```

4. **Test in Slack**
```
@YourBotName what meetings did we have last week?
@YourBotName summarize the sales dFireflies meeting transcripts
@YourBotName what was discussed in the monthly 1-2-1?
```


## Maintenance

### Daily Data Ingestion
Run ingestion daily to keep data fresh:
```bash
# Add to crontab for daily execution at 2 AM:
0 2 * * * cd /path/to/slackitbot && python -m src.ingest
```

### Monitoring
Check logs for errors:
```bash
# Server logs show query routing and responses
tail -f server.log  # If you redirect output to a file
```

### Clearing the Database
To re-index everything from scratch:
```bash
rm -rf chroma_db/
python -m src.ingest
```

## Security

- **Data Isolation**: E. Alex only accesses documents tagged with `{"agent": "e_alex"}`
- **No Data Mixing**: ChromaDB metadata filters ensure separation
- **Environment Variables**: All secrets stored in `.env` (never committed)
- **Service Account**: Google Drive access is read-only

## Usage Examples

```
# Ask about meetings
@EAlexBot what meetings did we have this week?

# Search specific topics
@EAlexBot find information about the Q4 sales strategy

# Get summaries
@EAlexBot summarize the latest monthly 1-2-1 notes

# Query transcripts
@EAlexBot what was discussed about AI in the LinkedIn videos?
```

## Additional Resources

- [Google Drive API Documentation](https://developers.google.com/drive/api/v3/about-sdk)
- [Slack API Documentation](https://api.slack.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
