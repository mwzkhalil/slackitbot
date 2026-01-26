# Multi-Agent Setup Guide

## ✅ Fireflies Integration Status

All three agents now have Fireflies API integration enabled:

### 1. E. Alex (Active)
- **Status**: ✅ Fully configured and running
- **Data Sources**: 
  - Google Drive: `GOOGLE_DRIVE_FOLDER_E_ALEX=1HUXPOSLxF3ECUAzFv8Cgusf-3mGJ_-FN`
  - Fireflies: ✅ Enabled
- **Folders**:
  - Internal Meetings (Final)
  - Linkedin Videos Transcripts
  - Monthly 1-2-1 (Final)
  - Sales (Final)
  - Youtube videos

### 2. E. Lazar (Ready to Configure)
- **Status**: ⏳ Code ready, awaiting folder configuration
- **Data Sources**:
  - Google Drive: Need to add `GOOGLE_DRIVE_FOLDER_E_LAZAR` to `.env`
  - Fireflies: ✅ Enabled (uses same API key)
- **Purpose**: Internal SOPs, onboarding, policies, workflows

### 3. Client Success (Ready to Configure)
- **Status**: ⏳ Code ready, awaiting folder configuration
- **Data Sources**:
  - Google Drive: Need to add `GOOGLE_DRIVE_FOLDER_CLIENT_SUCCESS` to `.env`
  - Fireflies: ✅ Enabled (uses same API key)
- **Purpose**: Client-specific answers with data isolation

## 📋 To-Do Tomorrow Morning

When you have the folder information, add to your `.env` file:

```bash
# E-Lazar (E-Lezzat) Google Drive Folder
GOOGLE_DRIVE_FOLDER_E_LAZAR=your-folder-id-here

# Client Success Google Drive Folder
GOOGLE_DRIVE_FOLDER_CLIENT_SUCCESS=your-folder-id-here
```

**How to get folder IDs:**
1. Open the Google Drive folder in browser
2. Copy the ID from URL: `https://drive.google.com/drive/folders/FOLDER_ID`
3. Paste into `.env`

## 🚀 Ingestion Commands

### E. Alex (Current)
```bash
source /home/mahwiz/miniconda3/bin/activate mahwiz && python -m src.ingest
```

### E. Lazar (After adding folder)
The ingestion script will automatically include E. Lazar once folder ID is configured.

### Client Success (After adding folder)
The ingestion script will automatically include Client Success once folder ID is configured.

## 🔧 What's Been Updated

### Code Files Modified:
1. ✅ [src/agents/e_lazar.py](src/agents/e_lazar.py) - Added Fireflies integration
2. ✅ [src/agents/client_success.py](src/agents/client_success.py) - Added Fireflies integration
3. ✅ [src/utils/config.py](src/utils/config.py) - Enabled folder configurations
4. ✅ [.env.example](.env.example) - Added folder ID templates

### Features Added:
- ✅ Fireflies meeting transcript ingestion for E-Lazar
- ✅ Fireflies meeting transcript ingestion for Client Success
- ✅ Comprehensive logging for both agents
- ✅ Error handling and empty content filtering
- ✅ Metadata tracking (agent, source, meeting_id, etc.)
- ✅ Unique document IDs to prevent duplicates

## 📊 Data Isolation

Each agent maintains strict data isolation:

| Agent | Metadata Filter | Example |
|-------|----------------|---------|
| E. Alex | `{"agent": "e_alex"}` | Sales, meetings, Amazon strategies |
| E. Lazar | `{"agent": "e_lazar"}` | SOPs, onboarding, internal policies |
| Client Success | `{"agent": "client_success", "client_id": "X"}` | Client-specific data only |

## 🔄 Shared Resources

All agents share:
- ✅ Same Fireflies API key (`FIREFLIES_API_KEY`)
- ✅ Same OpenAI API key for GPT-4o
- ✅ Same ChromaDB database (with metadata filtering)
- ✅ Same Google Drive service account credentials

## 🎯 Next Steps

1. **Tomorrow Morning**: Get folder IDs for E-Lazar and Client Success
2. **Add to .env**: Update configuration file
3. **Run Ingestion**: Execute `python -m src.ingest` to sync all agents
4. **Test**: Verify each agent responds correctly in Slack
5. **Monitor**: Check logs for any errors

## 📝 Notes

- All agents will fetch meetings from the **same Fireflies account**
- Meetings are tagged with agent name in metadata
- You can filter which meetings belong to which agent by date, participants, or title
- The current setup assumes all agents share the same meeting transcripts
- If you need different Fireflies accounts per agent, we can add separate API keys

---

**Current Status**: E. Alex is fully operational with Fireflies. E-Lazar and Client Success are code-ready and awaiting folder configuration.
