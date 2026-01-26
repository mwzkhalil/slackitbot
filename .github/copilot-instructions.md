# AI Agent Instructions for Slackitbot

## Architecture Overview

This is a **simplified RAG (Retrieval Augmented Generation) system** built with FastAPI that provides **one AI agent** responding to Slack mentions:

- **E. Alex**: Answers questions from:
  - Google Drive documents in `My Drive/AI/e-ALex`
  - Fireflies meeting transcripts (if API key configured)

**Critical principle**: Data is sourced from:
1. **Google Drive** at the specified folder path with subfolders:
   - Internal Meetings (Final)
   - Linkedin Videos Transcripts
   - Monthly 1-2-1 (Final)
   - Sale (Final)
2. **Fireflies API** (optional): Meeting transcripts with summaries

**Other agents (E. Lazar, Client Success) are COMMENTED OUT and not in use.**

## Data Flow

1. **Ingestion** (`src/ingest.py`): Pulls from:
   - Google Drive folder `My Drive/AI/e-ALex` and all subfolders
   - Fireflies API for meeting transcripts (if configured)
2. **Storage**: ChromaDB vector database at `./chroma_db` with metadata:
   - Google Drive: `{"agent": "e_alex", "source": "drive"}`
   - Fireflies: `{"agent": "e_alex", "source": "fireflies"}`
3. **Query**: Slack mention → E. Alex agent → Vector search → GPT-4 response

## Key Patterns & Conventions

### E. Alex Agent Implementation
Located in `src/agents/e_alex.py`:
- `__init__`: Initialize DB, LLM, and Google Drive API
- `respond(query)`: Query DB with `{"agent": "e_alex"}` filter, generate GPT-4 response
- `ingest_data()`: Fetch all files from Google Drive folder recursively

Example from [src/agents/e_alex.py](src/agents/e_alex.py#L24-L32):
```python
filters = check_data_isolation("e_alex")
results = self.db.query(query, filters)
context_docs = results.get("documents", [[]])[0] if results.get("documents") else []
```

**Critical**: Empty results return `"I don't have information on that."` - never hallucinate answers.

### Slack Channel → Agent Mapping
Channel IDs are **hardcoded** in [src/slack/slack_integration.py](src/slack/slack_integration.py#L75-L79):
```python
channel_to_agent = {
    "C0A6Q87TQTC": "e_alex",  # Only E. Alex is active
}
```
**When setting up**, update this ID from your Slack channel URL (`/archives/CHANNEL_ID`).

### Google Drive Folder Structure
The system reads from `My Drive/AI/e-ALex` and processes ALL subfolders:
- **Internal Meetings (Final)**: Meeting notes and recordings
- **Linkedin Videos Transcripts**: Video transcription files
- **Monthly 1-2-1 (Final)**: One-on-one meeting documents
- **Sale (Final)**: Sales-related documents
Environment variables required in `.env`:
- `OPENAI_API_KEY`: For GPT-4 responses
- `SLACK_BOT_TOKEN`: Slack bot OAuth token
- `SLACK_SIGNING_SECRET`: For webhook verification
- `GOOGLE_DRIVE_CREDENTIALS_PATH`: Path to service account JSON file
- `GOOGLE_DRIVE_FOLDER_E_ALEX`: Google Drive folder ID for E. Alex data
- `FIREFLIES_API_KEY`: (Optional) Fireflies API key for meeting transcripts
- `CHROMA_DB_PATH`: (Optional) Defaults to `./chroma_db`

**Not needed**: AssemblyAIth to service account JSON file
- `GOOGLE_DRIVE_FOLDER_E_ALEX`: Google Drive folder ID for E. Alex data
- `CHROMA_DB_PATH`: (Optional) Defaults to `./chroma_db`

**Not needed**: AssemblyAI, Fireflies, Nylas, admin password (manual uploads disabled).

## Developer Workflows

### Running Locally
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure .env (see .env.example)
# 3. Run initial data ingestion
python -m src.ingest

# 4. Start server (port 5001 by default)
python -m src.main
# OR with reload:
uvicorn src.main:app --reload --host 0.0.0.0 --port 5001

# 5. Expose with ngrok for Slack webhooks
ngrok http 5001
# Update Slack Event URL to: https://<ngrok-url>/slack/events
```

### Data Ingestion
- **Scheduled**: Run `python -m src.ingest` daily (recommended via cron at 2 AM)
- **Manual**: Run anytime to refresh data from Google Drive
- **Re-ingestion**: Safe to run repeatedly; uses unique IDs like `drive_{file_id}`

### Testing E. Alex
Mention bot in the E. Alex Slack channel:
```
@BotName what meetings did we have last week?
@BotName summarize the sales documents
@BotName what action items came from today's Fireflies meeting?
@BotName what was discussed in the monthly 1-2-1?
```

**Debugging**: Check terminal logs for `"Query: {query} for agent e_alex"` to verify routing.

## Critical Implementation Details

### Async/Await Consistency
FastAPI endpoints and agent methods use `async/await`. **Critical**: Google Drive API wraps sync `googleapiclient` calls in async methods (see [google_drive.py](src/data_ingestion/google_drive.py#L20-L28)). These don't truly run async but maintain consistent interface. For truly async operations, transcription polling uses AssemblyAI's async SDK.

### Error Handling
- Agents return friendly strings on failure: `"I don't have information on that."`
- Main app catches exceptions and returns `PlainTextResponse` with error (see [main.py](src/main.py#L40))
- Never expose internal errors to Slack users
- LLM errors return formatted string: `"Error generating response: {str(e)}"` (see [gpt_integration.py](src/llm/gpt_integration.py#L40))

### ChromaDB Metadata Schema
When adding documents, **alwaor `"fireflies"`
- Additional: `file_id`, `name`, `meeting_id`, `title`, etc.

**Document ID conventions** (prevent duplicates on re-ingestion):
- Google Drive: `f"drive_{file_id}"`
- Fireflies: `f"fireflies_{meeting
**Document ID conventions** (prevent duplicates on re-ingestion):
- Google Drive: `f"drive_{file_id}"`

### OpenAI Integration
Uses OpenAI SDK v1.x with `client.chat.completions.create()` (see [gpt_integration.py](src/llm/gpt_integration.py#L32-L38)). Response format:
```python
response.choices[0].message.content.strip()
```
Model is hardcoded to `"gpt-4"` with `temperature=0.1` and `max_tokens=500` for consistency.

## Common Pitfalls

1. **Channel ID mismatches**: Bot won't respond if channel isn't in `channel_to_agent` map
2. **Signature verification**: Slack events fail if signing secret is wrong or request body is read twice
3. **ChromaDB persistence**: Path must be consistent across runs (`CHROMA_DB_PATH` env var)
4. **Google Drive service account**: Folders MUST be shared with service account email (from JSON credentials)
5. **Async wrapper pattern**: Google Drive methods are `async def` but call sync `googleapiclient` - don't expect parallelism
6. **Subfolder processing**: Make sure Google Drive API recursively processes all subfolders in `My Drive/AI/e-ALex`

## Adding a New Agent

1. Create `src/agents/new_agent.py` following the pattern from existing agents
2. Add folder ID to `.env`: `GOOGLE_DRIVE_FOLDER_NEW_AGENT=...`
3. Update [Config](src/utils/config.py) to load the new folder ID
4. Register in [SlackIntegration](src/slack/slack_integration.py#L23) `self.agents` dict
5. Add channel mapping in `channel_to_agent`
6. Update [ingest.py](src/ingest.py) to include new agent
7. Create Slack channel, invite bot, get channel ID

## External Dependencies
Fireflies API**: GraphQL endpoint for meeting transcripts (optional - gracefully degrades if not configured)
- **AssemblyAI**: Audio transcription - COMMENTED OUT, not currently used
- **AssemblyAI**: Audio transcription (free tier: 5 hours/month) - COMMENTED OUT, not currently used
- **Fireflies**: Meeting transcripts (API key required but currently unused in code) - COMMENTED OUT
- **OpenAI**: GPT-4 responses (prompts in [gpt_integration.py](src/llm/gpt_integration.py#L16-L28))

## Reference Files

- Architecture: [docs/README.md](docs/README.md)
- Operations: [docs/SOPs.md](docs/SOPs.md) (backup, monitoring, security)
- User Guide: [docs/guidance.md](docs/guidance.md)
