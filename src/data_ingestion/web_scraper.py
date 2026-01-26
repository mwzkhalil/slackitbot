"""
Web scraping utility for fetching content from URLs, especially Amazon listings.
Uses OpenAI's capabilities and web scraping libraries.
"""

import requests
import logging
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import re
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None
    logging.warning("BeautifulSoup4 not installed. Web scraping will be limited.")
import time

class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    async def fetch_url_content(self, url: str) -> Optional[str]:
        """
        Fetch and extract text content from a URL.
        Returns cleaned text content.
        """
        try:
            logging.info(f"Fetching content from URL: {url}")
            response = self.session.get(url, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            # Parse HTML
            if BeautifulSoup is None:
                logging.error("BeautifulSoup4 not available. Cannot parse HTML.")
                return None
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "noscript"]):
                script.decompose()
            
            # Extract text
            text = soup.get_text(separator='\n', strip=True)
            
            # Clean up whitespace
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            cleaned_text = '\n'.join(lines)
            
            logging.info(f"Fetched {len(cleaned_text)} characters from URL")
            return cleaned_text[:50000]  # Limit to 50k chars
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching URL {url}: {str(e)}")
            return None
        except Exception as e:
            logging.error(f"Error parsing URL content {url}: {str(e)}")
            return None
    
    def extract_amazon_listing_info(self, url: str, content: str) -> Dict[str, Any]:
        """
        Extract structured information from Amazon listing page.
        """
        info = {
            "url": url,
            "title": "",
            "price": "",
            "rating": "",
            "reviews_count": "",
            "images_count": 0,
            "videos_count": 0,
            "a_plus_content": False,
            "bullet_points": [],
            "description": "",
            "raw_content": content[:10000]  # First 10k chars for analysis
        }
        
        # Try to extract basic info from content
        # Title pattern
        title_match = re.search(r'productTitle[^>]*>([^<]+)', content, re.IGNORECASE)
        if title_match:
            info["title"] = title_match.group(1).strip()
        
        # Price pattern
        price_match = re.search(r'£[\d,]+\.?\d*|€[\d,]+\.?\d*|\$[\d,]+\.?\d*', content)
        if price_match:
            info["price"] = price_match.group(0)
        
        # Rating pattern
        rating_match = re.search(r'(\d+\.?\d*)\s*(?:out of|stars)', content, re.IGNORECASE)
        if rating_match:
            info["rating"] = rating_match.group(1)
        
        # Reviews count
        reviews_match = re.search(r'(\d+(?:,\d+)*)\s*(?:customer|review)', content, re.IGNORECASE)
        if reviews_match:
            info["reviews_count"] = reviews_match.group(1)
        
        # Check for A+ content
        if 'a-plus' in content.lower() or 'aplus' in content.lower() or 'enhanced brand content' in content.lower():
            info["a_plus_content"] = True
        
        # Count images and videos (approximate)
        info["images_count"] = len(re.findall(r'<img[^>]*>', content, re.IGNORECASE))
        info["videos_count"] = len(re.findall(r'<video[^>]*>|video-player', content, re.IGNORECASE))
        
        return info
    
    def format_listing_info(self, info: Dict[str, Any]) -> str:
        """
        Format Amazon listing info as context text for LLM.
        """
        formatted = "=== Amazon Listing Analysis ===\n\n"
        formatted += f"URL: {info['url']}\n"
        if info.get('title'):
            formatted += f"Title: {info['title']}\n"
        if info.get('price'):
            formatted += f"Price: {info['price']}\n"
        if info.get('rating'):
            formatted += f"Rating: {info['rating']} stars\n"
        if info.get('reviews_count'):
            formatted += f"Reviews: {info['reviews_count']}\n"
        formatted += f"Images: {info['images_count']}\n"
        formatted += f"Videos: {info['videos_count']}\n"
        formatted += f"A+ Content: {'Yes' if info['a_plus_content'] else 'No'}\n"
        formatted += f"\nPage Content (first 10k chars):\n{info['raw_content']}\n"
        return formatted
