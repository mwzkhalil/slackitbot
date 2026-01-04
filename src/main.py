"""
Main FastAPI application for the AI Agent System.
Handles Slack integrations, data ingestion, and agent responses.
"""

from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form
from fastapi.responses import PlainTextResponse
import os
from dotenv import load_dotenv
from src.slack.slack_integration import handle_slack_event
from src.data_ingestion.manual_upload import handle_manual_upload
from src.utils.config import Config

load_dotenv()

app = FastAPI(title="AI Agent System", version="1.0.0")

config = Config()

@app.get("/")
async def root():
    return {"message": "AI Agent System is running"}

@app.post("/slack/events")
async def slack_events(request: Request):
    """
    Handle Slack events and route to appropriate agent.
    """
    try:
        response = await handle_slack_event(request, config)
        return PlainTextResponse(response)
    except Exception as e:
        return PlainTextResponse(f"Error: {str(e)}")

@app.post("/admin/upload/{agent}")
async def upload_file(
    agent: str,
    file: UploadFile = File(...),
    password: str = Form(...),
    client_id: str = Form(None)  # For client success agent
):
    """
    Admin endpoint for manual file uploads.
    Requires admin password.
    For client success agent, client_id must be provided.
    """
    if password != config.admin_password:
        raise HTTPException(status_code=403, detail="Unauthorized")

    try:
        result = await handle_manual_upload(agent, file, client_id, config)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)