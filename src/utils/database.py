"""
Database utilities for vector storage and indexing.
Uses ChromaDB for vector search with metadata.
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
import os

class VectorDB:
    def __init__(self, db_path: str):
        self.client = chromadb.PersistentClient(path=db_path, settings=Settings(anonymized_telemetry=False))
        self.collection = self.client.get_or_create_collection(name="ai_agent_data")

    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        """
        Add documents to the vector database.
        """
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def query(self, query_text: str, filters: Dict[str, Any], n_results: int = 5) -> Dict[str, Any]:
        """
        Query the database with filters for data isolation.
        """
        where = filters
        results = self.collection.query(
            query_texts=[query_text],
            where=where,
            n_results=n_results
        )
        return results

    def delete_by_metadata(self, metadata_filter: Dict[str, Any]):
        """
        Delete documents matching metadata filter.
        """
        # Chroma doesn't have direct delete by metadata, so get ids first
        results = self.collection.get(where=metadata_filter)
        if results['ids']:
            self.collection.delete(ids=results['ids'])

# Global instance
_db_instance = None

def get_vector_db(db_path: str) -> VectorDB:
    global _db_instance
    if _db_instance is None:
        _db_instance = VectorDB(db_path)
    return _db_instance