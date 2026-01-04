"""
Slack integration for handling events and posting responses.
"""

import json
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
        print("Slack event received")  # Debug
        body = await request.body()
        headers = dict(request.headers)

        # Verify signature
        if not self.signature_verifier.is_valid_request(body, headers):
            print("Invalid signature")  # Debug
            return "Invalid signature"

        data = json.loads(body)

        if data.get("type") == "url_verification":
            print("URL verification")  # Debug
            return data["challenge"]

        if "event" in data:
            event = data["event"]
            if event.get("type") == "app_mention":
                print("App mention event")  # Debug
                return await self.handle_app_mention(event)

        return ""

    async def handle_app_mention(self, event: Dict[str, Any]) -> str:
        """
        Handle @mention in Slack.
        Parse the message to determine agent and query.
        """
        print(f"Handling mention in channel: {event.get('channel')}")  # Debug
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
            print(f"No agent for channel {channel}")  # Debug
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
            print("Access denied")  # Debug
            return "You do not have access to this agent."

        query = sanitize_input(query)
        print(f"Query: {query} for agent {agent_name}")  # Debug

        agent = self.agents[agent_name]
        response = await agent.respond(query, client_id)
        print(f"Response: {response}")  # Debug

        # Post response back to channel
        try:
            self.client.chat_postMessage(channel=channel, text=response)
            print("Posted to Slack")  # Debug
        except Exception as e:
            print(f"Failed to post: {e}")  # Debug

        return response  # For the webhook response, but since we post, maybe empty

# Function for main.py
async def handle_slack_event(request, config: Config) -> str:
    slack = SlackIntegration(config)
    return await slack.handle_event(request)