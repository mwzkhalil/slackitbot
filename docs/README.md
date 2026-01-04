# AI Agent System

A professional system consisting of three AI agents that integrate with Slack, Fireflies API, Google Drive, and support manual uploads. Each agent maintains strict data isolation and responds using GPT-4.

## Overview

The system includes:
- **E. Alex**: Answers questions about client meetings, internal meetings, and shared project documents.
- **E. Lazar**: Answers internal questions on SOPs, onboarding, policies, and workflows.
- **Client Success Agent**: Provides client-specific answers without data contamination.

## Data Sources
- **Nylas API** (free tier available): Calendar events (meeting metadata like titles, descriptions, participants).
- **AssemblyAI** (free tier: 5 hours/month): For transcribing uploaded audio files of meetings.
- **Google Drive**: Documents, presentations, images.
- **Manual Uploads**: Text files or audio files (auto-transcribed).
- **Slack Integration**: Dedicated channels per agent, plain text responses.
- **Security**: Strict dataset separation, read-only access, OAuth for APIs.
- **LLM**: Uses GPT-4 for response generation.
- **Vector Search**: ChromaDB for indexing and querying data.

## Setup

1. **Clone or Download** the repository.

2. **Install Dependencies**:
   ```
   pip install -r requirements.txt
   ```

3. **Environment Configuration**:
   - Copy `.env.example` to `.env`.
   - Fill in the required API keys and configurations:
     - OpenAI API Key
     - Slack Bot Token and Signing Secret
     - Nylas Access Token (Client ID and Secret optional for v3)
     - AssemblyAI API Key (free tier available)
     - Google Drive Credentials Path and Folder IDs
     - Admin Password for uploads

4. **Nylas Setup** (Optional for basic calendar access):
   - Sign up for [Nylas](https://www.nylas.com/) (free tier available).
   - Generate an Access Token from your dashboard.
   - Set `NYLAS_ACCESS_TOKEN` in `.env`.
   - Client ID and Secret are optional for v3 API.

5. **Google Drive Setup**:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/).
   - Create a new project or select an existing one.
   - Enable the Google Drive API: Search for "Google Drive API" and enable it.
   - Create credentials: Go to "Credentials" > "Create Credentials" > "Service Account".
   - Name the service account (e.g., "AI Agent Service Account").
   - Grant it the "Editor" role or custom role with Drive read access.
   - Create a key: Click on the service account > "Keys" > "Add Key" > "JSON". Download the file.
   - Set `GOOGLE_DRIVE_CREDENTIALS_PATH` to the path of this JSON file (e.g., `./credentials.json`).
   - Create folders in Google Drive for each agent (e.g., "E Alex Docs", "E Lazar Docs", "Client Success Docs").
   - Share each folder with the service account email (found in the JSON or console).
   - Get Folder IDs: Open each folder in Google Drive, copy the ID from the URL (e.g., `https://drive.google.com/drive/folders/FOLDER_ID`).
   - Set the corresponding `GOOGLE_DRIVE_FOLDER_*` variables in `.env`.

5. **Slack Setup**:
   - Go to [https://api.slack.com/apps](https://api.slack.com/apps) and create a new app.
   - Choose "From scratch" and name it (e.g., "AI Agent Bot").
   - Add features: Enable "Bots" and "Event Subscriptions".
   - Set Request URL for Events: Use a temporary URL (e.g., from ngrok) pointing to `/slack/events` (e.g., `https://your-ngrok-url.ngrok.io/slack/events`).
     - **Ngrok Setup Guide**:
       - Download ngrok from [https://ngrok.com/download](https://ngrok.com/download).
       - Sign up for a free account and get your auth token.
       - Run `ngrok config add-authtoken YOUR_TOKEN`.
       - Start your server locally: `python -m src.main` (runs on port 8000).
       - In another terminal, run `ngrok http 8000`.
       - Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`) and append `/slack/events` for the Request URL.
   - Subscribe to events: Add `app_mention` under "Bot Events".
   - Add OAuth Scopes: Under "OAuth & Permissions", add `app_mentions:read`, `channels:history`, `chat:write`, `files:read`.
   - Install the app to your workspace.
   - Copy the "Bot User OAuth Token" (starts with `xoxb-`) for `SLACK_BOT_TOKEN`.
   - Copy the "Signing Secret" from "Basic Information" for `SLACK_SIGNING_SECRET`.
   - Create dedicated channels for each agent (e.g., #e-alex, #e-lazar, #client-success) and invite the bot.
     - **Channel Setup Guide**:
       - In Slack, click "Add channels" > "Create a channel".
       - Name them `#e-alex`, `#e-lazar`, `#client-success` (make them public or private as needed).
       - For each channel, type `/invite @YourBotName` (replace with your bot's username, e.g., @AI Agent).
       - The bot should join and be able to respond to mentions.

6. **Run Data Ingestion**:
   ```
   python -m src.ingest
   ```
   Run this periodically to sync data.

7. **Start the Server**:
   ```
   python -m src.main
   ```
   Or use uvicorn: `uvicorn src.main:app --reload`

## Testing the System

1. **Ingest Data**:
   ```
   python -m src.ingest
   ```
   - This fetches calendar events from Nylas and files from Google Drive, indexing them for the agents.

2. **Start the Server**:
   ```
   python -m src.main
   ```
   - Runs on http://localhost:8000. Keep it running.

3. **Set Up Ngrok (for Slack)**:
   - In another terminal: `ngrok http 8000`
   - Ensure the Slack app's Request URL is set to `https://your-ngrok-url.ngrok.io/slack/events`.

4. **Test in Slack**:
   - Go to #e-alex and type: `@YourBotName What meetings are scheduled?`
   - Go to #e-lazar and type: `@YourBotName What are the SOPs?`
   - For #client-success: `@YourBotName client123: What is the project status?`
   - The bot should respond with answers based on indexed data.

5. **Test Manual Upload** (Optional):
   - Use a tool like Postman or curl:
     ```
     curl -X POST "http://localhost:8000/admin/upload/e_alex" \
     -F "file=@your_file.txt" \
     -F "password=your_admin_password"
     ```
   - Then re-ingest or query again.

If no data is found, responses will be "I don't have information on that." Ensure your .env has valid keys and data exists in Nylas/Google Drive.

## SOPs and Guidance

### Data Ingestion SOP
- Run ingestion script daily or after new data is added.
- Monitor logs for errors.
- Ensure API rate limits are not exceeded.

### Security Guidance
- Never share API keys.
- Use HTTPS for all communications.
- Regularly rotate credentials.
- Audit access logs.

### Maintenance
- Update dependencies quarterly.
- Monitor ChromaDB performance.
- Backup the vector database regularly.

### Error Handling
- If no data found, agents respond with "I don't have information on that."
- Log all errors and notify admins.

### Acceptance Criteria Verification
- Test each agent responds only from its dataset.
- Verify Fireflies and Drive data ingestion.
- Confirm client data isolation.

## Architecture

- **Backend**: FastAPI for web server.
- **Database**: ChromaDB for vector storage.
- **APIs**: OpenAI, Slack SDK, Google API, Fireflies API.
- **Security**: Environment variables, input sanitization, access validation.

## Contributing

Follow standard Python practices. Add tests for new features. Update documentation.

## License

[Specify License]