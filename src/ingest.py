"""
Script to run data ingestion for all agents.
Uses Nylas for calendar events and Google Drive.
For transcripts, use manual audio uploads with AssemblyAI.
"""

import asyncio
from src.utils.config import Config
from src.agents.e_alex import EAlexAgent
from src.agents.e_lazar import ELazarAgent
from src.agents.client_success import ClientSuccessAgent

async def main():
    config = Config()
    agents = [
        EAlexAgent(config),
        ELazarAgent(config),
        # For client success, need to specify clients
        # ClientSuccessAgent(config) - but ingest per client
    ]

    for agent in agents:
        await agent.ingest_data()
        print(f"Data ingested for {agent.__class__.__name__}")

    # For client success, assume list of clients
    clients = ["client1", "client2"]  # From config or DB
    for client_id in clients:
        agent = ClientSuccessAgent(config)
        await agent.ingest_data(client_id)
        print(f"Data ingested for Client Success: {client_id}")

if __name__ == "__main__":
    asyncio.run(main())