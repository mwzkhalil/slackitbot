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
# from src.agents.client_success import ClientSuccessAgent  # COMMENTED OUT - Not used
from src.utils.config import Config
from src.utils.security import validate_agent_access, sanitize_input

class SlackIntegration:
    def __init__(self, config: Config):
        self.config = config
        self.client = WebClient(token=config.slack_bot_token)
        self.signature_verifier = SignatureVerifier(config.slack_signing_secret)
        # E. Alex and E. Lazar agents are active
        self.agents = {
            "e_alex": EAlexAgent(config),
            "e_lazar": ELazarAgent(config),
            # "client_success": ClientSuccessAgent(config)  # COMMENTED OUT - Not used
        }
        # Get bot user ID
        try:
            self.bot_user_id = self.client.auth_test()["user_id"]
            logging.info(f"Bot user ID: {self.bot_user_id}")
        except Exception as e:
            logging.error(f"Failed to get bot user ID: {e}")
            self.bot_user_id = None

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
        event_ts = event.get("event_ts", "")

        # Map channel IDs to agents - UPDATE THESE WITH YOUR ACTUAL CHANNEL IDs
        # E. Alex and E. Lazar agents are active
        channel_to_agent = {
            "C0A7E80RA79": "e_alex",  # Replace with actual #e-alex channel ID
            "C0A8Z329GVD": "e_lazar",  # Replace with actual #e-lezzat channel ID
            # "C0A7JHGV07J": "client_success"  # COMMENTED OUT - Not used
        }

        agent_name = channel_to_agent.get(channel)
        if not agent_name:
            logging.info(f"No agent for channel {channel}")  # Debug
            return "This channel is not associated with an agent."

        # Extract query
        if self.bot_user_id:
            query = text.replace(f"<@{self.bot_user_id}>", "").strip()
        else:
            # Fallback: assume the mention is at the start
            query = text.split(">", 1)[-1].strip() if ">" in text else text.strip()

        # COMMENTED OUT - Client Success not used, no client_id needed
        # client_id = None
        # if agent_name == "client_success":
        #     if ":" in query:
        #         client_id, query = query.split(":", 1)
        #         client_id = client_id.strip()
        #         query = query.strip()

        if not validate_agent_access(agent_name, user, None):
            logging.info("Access denied")  # Debug
            return "You do not have access to this agent."

        query = sanitize_input(query)
        logging.info(f"Query: {query} for agent {agent_name} (event_ts: {event_ts})")  # Debug

        # Process in background to avoid Slack retries (return 200 OK immediately)
        import asyncio
        asyncio.create_task(self._process_and_respond(agent_name, query, channel, event_ts))
        
        # Return empty string immediately to acknowledge event
        return ""
    
    async def _process_and_respond(self, agent_name: str, query: str, channel: str, event_ts: str):
        """Process query and post response (runs in background)"""
        try:
            agent = self.agents[agent_name]
            response = await agent.respond(query, None)
            logging.info(f"Response for {event_ts}: {response[:100]}...")  # Debug
            
            # Post response back to channel
            self.client.chat_postMessage(channel=channel, text=response)
            logging.info(f"Posted to Slack for {event_ts}")  # Debug
        except Exception as e:
            logging.error(f"Error processing query: {e}")
            try:
                self.client.chat_postMessage(
                    channel=channel, 
                    text=f"Sorry, I encountered an error: {str(e)}"
                )
            except:
                pass

# Function for main.py
async def handle_slack_event(request, config: Config) -> str:
    slack = SlackIntegration(config)
    return await slack.handle_event(request)