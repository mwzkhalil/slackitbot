"""
Slack integration for handling events and posting responses.
"""

import json
import re
import logging
import hmac
import hashlib
from typing import Dict, Any
from slack_sdk import WebClient
from slack_sdk.signature import SignatureVerifier
from src.agents.e_alex import EAlexAgent
from src.agents.e_lazar import ELazarAgent
from src.utils.config import Config
from src.utils.security import validate_agent_access, sanitize_input


def markdown_to_slack(text: str) -> str:
    """
    Convert LLM Markdown output to Slack mrkdwn format.
    """
    # Convert ### Heading / ## Heading / # Heading → *Heading*
    text = re.sub(r'^#{1,6}\s+(.+)$', r'*\1*', text, flags=re.MULTILINE)

    # Convert **bold** → *bold*
    text = re.sub(r'\*\*(.+?)\*\*', r'*\1*', text)

    # Convert __bold__ → *bold*
    text = re.sub(r'__(.+?)__', r'*\1*', text)

    # Convert *italic* or _italic_ → _italic_  (Slack uses _ for italic)
    # Be careful not to re-convert already converted *bold*
    # Only single asterisks that aren't already bold
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'_\1_', text)

    # Convert `inline code` → keep as-is (Slack supports backticks)
    # No change needed

    # Convert ```code blocks``` → keep backticks, Slack renders them
    # No change needed

    # Convert numbered lists: "1. item" stays as-is (Slack renders them fine)
    # No change needed

    # Convert unordered lists: "- item" or "* item" → "• item"
    text = re.sub(r'^[\-\*]\s+', '• ', text, flags=re.MULTILINE)

    # Convert [link text](url) → <url|link text>
    text = re.sub(r'\[(.+?)\]\((https?://[^\)]+)\)', r'<\2|\1>', text)

    # Remove any remaining bare markdown underscores used as dividers (e.g. --- or ***)
    text = re.sub(r'^(\*{3,}|-{3,}|_{3,})$', '', text, flags=re.MULTILINE)

    # Collapse more than 2 consecutive blank lines into 2
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


class SlackIntegration:
    def __init__(self, config: Config):
        self.config = config
        self.client = WebClient(token=config.slack_bot_token)
        self.signature_verifier = SignatureVerifier(config.slack_signing_secret)
        self.agents = {
            "e_alex": EAlexAgent(config),
            "e_lazar": ELazarAgent(config),
        }
        try:
            self.bot_user_id = self.client.auth_test()["user_id"]
            logging.info(f"Bot user ID: {self.bot_user_id}")
        except Exception as e:
            logging.error(f"Failed to get bot user ID: {e}")
            self.bot_user_id = None

    async def handle_event(self, request) -> str:
        logging.info("Slack event received")
        body = await request.body()
        headers = dict(request.headers)

        try:
            data = json.loads(body.decode('utf-8'))
            logging.info(f"Parsed data: {data}")
        except Exception as e:
            logging.error(f"JSON load failed: {e}, body: {body.decode('utf-8')}")
            return "json failed"

        if data.get("type") == "url_verification":
            logging.info("URL verification")
            return {"challenge": data.get("challenge", "")}

        if not self.signature_verifier.is_valid_request(body, headers):
            logging.info("Invalid signature")
            return "Invalid signature"

        if "event" in data:
            event = data["event"]
            if event.get("type") == "app_mention":
                logging.info("App mention event")
                return await self.handle_app_mention(event)

        return ""

    async def handle_app_mention(self, event: Dict[str, Any]) -> str:
        logging.info(f"Handling mention in channel: {event.get('channel')}")
        text = event.get("text", "")
        channel = event.get("channel")
        user = event.get("user")
        event_ts = event.get("event_ts", "")

        channel_to_agent = {
            "C0A7E80RA79": "e_alex",
            "C0A8Z329GVD": "e_lazar",
            "C0AFJS2JD9S": "e_alex",  
        }

        agent_name = channel_to_agent.get(channel)
        if not agent_name:
            logging.info(f"No agent for channel {channel}")
            return "This channel is not associated with an agent."

        if self.bot_user_id:
            query = text.replace(f"<@{self.bot_user_id}>", "").strip()
        else:
            query = text.split(">", 1)[-1].strip() if ">" in text else text.strip()

        if not validate_agent_access(agent_name, user, None):
            logging.info("Access denied")
            return "You do not have access to this agent."

        query = sanitize_input(query)
        logging.info(f"Query: {query} for agent {agent_name} (event_ts: {event_ts})")

        import asyncio
        asyncio.create_task(self._process_and_respond(agent_name, query, channel, event_ts))

        return ""

    async def _process_and_respond(self, agent_name: str, query: str, channel: str, event_ts: str):
        """Process query, convert Markdown to Slack mrkdwn, and post response."""
        try:
            agent = self.agents[agent_name]
            response = await agent.respond(query, None)
            logging.info(f"Raw response for {event_ts}: {response[:100]}...")

            # ✅ Convert Markdown → Slack mrkdwn before posting
            slack_response = markdown_to_slack(response)
            logging.info(f"Converted response for {event_ts}: {slack_response[:100]}...")

            self.client.chat_postMessage(
                channel=channel,
                text=slack_response,
                mrkdwn=True  # Tell Slack to render mrkdwn formatting
            )
            logging.info(f"Posted to Slack for {event_ts}")
        except Exception as e:
            logging.error(f"Error processing query: {e}")
            try:
                self.client.chat_postMessage(
                    channel=channel,
                    text=f"Sorry, I encountered an error: {str(e)}"
                )
            except:
                pass


async def handle_slack_event(request, config: Config) -> str:
    slack = SlackIntegration(config)
    return await slack.handle_event(request)