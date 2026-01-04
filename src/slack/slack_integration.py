"""
Slack integration for handling events and posting responses.
"""

import json
import logging
import hmac
import hashlib
from typing import Dict, Any
from slack_sdk import WebClient
from slack_sdk.signature import SignatureVerifier
from src.agents.e_alex import EAlexAgent
from src.agents.e_lazar import ELazarAgent
from src.agents.client_success import ClientSuccessAgent
from src.utils.config import Config
from src.utils.security import validate_agent_access, sanitize_input

class SlackIntegration:
    def __init__(self, config: Config):
        self.config = config
        self.client = WebClient(token=config.slack_bot_token)
        self.signature_verifier = SignatureVerifier(config.slack_signing_secret)
        self.agents = {
            "e_alex": EAlexAgent(config),
            "e_lazar": ELazarAgent(config),
            "client_success": ClientSuccessAgent(config)
        }

    async def handle_event(self, request) -> str:
        """
        Handle incoming Slack event.
        """
        logging.info("Slack event received")  # Debug
        body = await request.body()
        headers = dict(request.headers)

        try:
            data = json.loads(body.decode('utf-8'))
            logging.info(f"Parsed data: {data}")
        except Exception as e:
            logging.error(f"JSON load failed: {e}, body: {body.decode('utf-8')}")
            return "json failed"

        if data.get("type") == "url_verification":
            logging.info("URL verification")  # Debug
            return {"challenge": data.get("challenge", "")}

        # Verify signature for other events
        if not self.signature_verifier.is_valid_request(body, headers):
            logging.info("Invalid signature")  # Debug
            return "Invalid signature"

        if "event" in data:
            event = data["event"]
            if event.get("type") == "app_mention":
                logging.info("App mention event")  # Debug
                return await self.handle_app_mention(event)

        return ""

    async def handle_app_mention(self, event: Dict[str, Any]) -> str:
        """
        Handle @mention in Slack.
        Parse the message to determine agent and query.
        """
        logging.info(f"Handling mention in channel: {event.get('channel')}")  # Debug
        text = event.get("text", "")
        channel = event.get("channel")
        user = event.get("user")

        # Map channel IDs to agents - UPDATE THESE WITH YOUR ACTUAL CHANNEL IDs
        channel_to_agent = {
            "C0A6Q87TQTC": "e_alex",  # Replace with actual #e-alex channel ID
            "C0A68QU90CX": "e_lazar",  # Replace with actual #e-lazar channel ID
            "C0A7JHGV07J": "client_success"  # Replace with actual #client-success channel ID
        }

        agent_name = channel_to_agent.get(channel)
        if not agent_name:
            logging.info(f"No agent for channel {channel}")  # Debug
            return "This channel is not associated with an agent."

        # Extract query
        query = text.replace(f"<@{self.config.slack_bot_token.split('-')[1]}>", "").strip()  # Remove @mention

        # For client_success, extract client_id if present
        client_id = None
        if agent_name == "client_success":
            # Assume query starts with client_id:
            if ":" in query:
                client_id, query = query.split(":", 1)
                client_id = client_id.strip()
                query = query.strip()

        if not validate_agent_access(agent_name, user, client_id):
            logging.info("Access denied")  # Debug
            return "You do not have access to this agent."

        query = sanitize_input(query)
        logging.info(f"Query: {query} for agent {agent_name}")  # Debug

        agent = self.agents[agent_name]
        response = await agent.respond(query, client_id)
        logging.info(f"Response: {response}")  # Debug

        # Post response back to channel
        try:
            self.client.chat_postMessage(channel=channel, text=response)
            logging.info("Posted to Slack")  # Debug
        except Exception as e:
            logging.error(f"Failed to post: {e}")  # Debug

        return response  # For the webhook response, but since we post, maybe empty

# Function for main.py
async def handle_slack_event(request, config: Config) -> str:
    slack = SlackIntegration(config)
    return await slack.handle_event(request)