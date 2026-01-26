"""
Script to run data ingestion for E. Alex and E. Lazar agents.
Uses Google Drive for both agents.
"""

import asyncio
import logging
from dotenv import load_dotenv
from src.utils.config import Config
from src.agents.e_alex import EAlexAgent
from src.agents.e_lazar import ELazarAgent
# from src.agents.client_success import ClientSuccessAgent  # COMMENTED OUT - Not used

# Load environment variables
load_dotenv()
logging.basicConfig(level=logging.INFO)

async def main():
    config = Config()
    
    # E. Alex and E. Lazar agents are active
    agents = [
        EAlexAgent(config),
        ELazarAgent(config),
    ]
    for agent in agents:
    await agent.ingest_data()
    print(f"Data ingested for {agent.__class__.__name__}")
    
    # COMMENTED OUT - Client Success not used
    # clients = ["client1", "client2"]
    # for client_id in clients:
    #     agent = ClientSuccessAgent(config)
    #     await agent.ingest_data(client_id)
    #     print(f"Data ingested for Client Success: {client_id}")

if __name__ == "__main__":
    asyncio.run(main())