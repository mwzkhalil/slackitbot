"""
Diagnostic script to check if E. Lazar documents are in the database.
Run this to verify documents were ingested properly.
"""

import asyncio
import logging
from dotenv import load_dotenv
from src.utils.config import Config
from src.utils.database import get_vector_db

load_dotenv()
logging.basicConfig(level=logging.INFO)

async def main():
    config = Config()
    db = get_vector_db(config.chroma_db_path)
    
    # Check for E. Lazar documents
    filters = {"agent": "e_lazar"}
    
    # Check Drive documents
    drive_filters = {
        "$and": [
            {"agent": "e_lazar"},
            {"source": "drive"}
        ]
    }
    
    print("=" * 60)
    print("E. Lazar Document Diagnostic")
    print("=" * 60)
    
    # Query for any E. Lazar documents
    print("\n1. Checking for ANY E. Lazar documents...")
    results = db.query("HR policies", filters, n_results=5)
    all_docs = results.get("documents", [[]])[0] if results.get("documents") else []
    print(f"   Found {len(all_docs)} documents (any source)")
    
    # Query specifically for Drive documents
    print("\n2. Checking for E. Lazar Google Drive documents...")
    drive_results = db.query("HR policies", drive_filters, n_results=5)
    drive_docs = drive_results.get("documents", [[]])[0] if drive_results.get("documents") else []
    print(f"   Found {len(drive_docs)} Google Drive documents")
    
    if drive_docs:
        print("\n   Sample Drive documents:")
        for i, doc in enumerate(drive_docs[:3], 1):
            preview = doc[:200].replace('\n', ' ')
            print(f"   {i}. {preview}...")
    else:
        print("\n   ⚠️  NO GOOGLE DRIVE DOCUMENTS FOUND!")
        print("   This means documents were not ingested.")
        print("   Please run: python -m src.ingest")
    
    # Check Fireflies documents
    fireflies_filters = {
        "$and": [
            {"agent": "e_lazar"},
            {"source": "fireflies"}
        ]
    }
    print("\n3. Checking for E. Lazar Fireflies documents...")
    fireflies_results = db.query("meeting", fireflies_filters, n_results=5)
    fireflies_docs = fireflies_results.get("documents", [[]])[0] if fireflies_results.get("documents") else []
    print(f"   Found {len(fireflies_docs)} Fireflies documents")
    
    # Get metadata to see what's actually in the database
    print("\n4. Checking collection metadata...")
    try:
        # Use the database's delete_by_metadata method pattern to check
        # We'll query with a very broad query to see what exists
        broad_results = db.query("document", filters, n_results=10)
        if broad_results.get('ids'):
            print(f"   Found {len(broad_results['ids'])} document IDs")
            print("\n   Sample document IDs:")
            for i, doc_id in enumerate(broad_results['ids'][:5], 1):
                print(f"   {i}. {doc_id}")
        else:
            print("   ⚠️  No documents found in collection!")
    except Exception as e:
        print(f"   Error checking metadata: {e}")
    
    print("\n" + "=" * 60)
    if not drive_docs:
        print("⚠️  ACTION REQUIRED: Run 'python -m src.ingest' to ingest Google Drive documents")
    else:
        print("✓ Documents found in database")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
