# AI Agent System

A professional system consisting of three AI agents that integrate with Slack, Fireflies API, Google Drive, and support manual uploads. Each agent maintains strict data isolation and responds using GPT-4.

## Overview

The system includes:
- **E. Alex**: Answers questions about client meetings, internal meetings, and shared project documents.
- **E. Lazar**: Answers internal questions on SOPs, onboarding, policies, and workflows.
- **Client Success Agent**: Provides client-specific answers without data contamination.

## Features

- **Data Sources**: Fireflies API (meeting transcripts/summaries), Google Drive (documents/presentations), Manual uploads.
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
     - Fireflies API Key
     - Google Drive Credentials Path and Folder IDs
     - Admin Password for uploads

4. **Google Drive Setup**:
   - Create a service account and download credentials JSON.
   - Share the required folders with the service account email.
   - Set folder IDs in `.env`.

5. **Slack Setup**:
   - Create a Slack app with bot permissions.
   - Set up event subscriptions for app mentions.
   - Install the app in the dedicated channels.

6. **Run Data Ingestion**:
   ```
   python src/ingest.py
   ```
   Run this periodically to sync data.

7. **Start the Server**:
   ```
   python src/main.py
   ```
   Or use uvicorn: `uvicorn src.main:app --reload`

## Usage

- **Slack Queries**: Mention the bot in the agent's channel with your query.
- **For Client Success**: Include client ID in the query, e.g., "client123: What is the status?"
- **Manual Uploads**: POST to `/admin/upload/{agent}` with file and password.

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