"""
Google Custom Search API integration for Amazon-related queries.
"""

import requests
import logging
from typing import List, Dict, Any, Optional

class GoogleSearchAPI:
    def __init__(self, api_key: str, search_engine_id: str):
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        
    async def search_amazon(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for Amazon-related information using Google Custom Search.
        Focuses on Amazon seller best practices, A/B testing, listing optimization, etc.
        """
        if not self.api_key or not self.search_engine_id:
            logging.warning("Google Search API not configured - skipping search")
            return []
        
        # Enhance query for Amazon-specific results
        amazon_query = f"Amazon seller {query} best practices 2024"
        
        params = {
            "key": self.api_key,
            "cx": self.search_engine_id,
            "q": amazon_query,
            "num": num_results
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                
                search_results = []
                for item in items:
                    search_results.append({
                        "title": item.get("title", ""),
                        "snippet": item.get("snippet", ""),
                        "link": item.get("link", "")
                    })
                
                logging.info(f"Google Search found {len(search_results)} results for: {query}")
                return search_results
            else:
                logging.error(f"Google Search API error: {response.status_code} - {response.text}")
                return []
                
        except requests.exceptions.Timeout:
            logging.warning("Google Search API request timed out")
            return []
        except requests.exceptions.RequestException as e:
            logging.error(f"Google Search API error: {str(e)}")
            return []
    
    def format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Format search results as context text for LLM.
        """
        if not results:
            return ""
        
        formatted = "=== Google Search Results (Amazon Best Practices) ===\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result['title']}\n"
            formatted += f"   {result['snippet']}\n"
            formatted += f"   Source: {result['link']}\n\n"
        
        return formatted
