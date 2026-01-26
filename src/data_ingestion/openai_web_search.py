"""
OpenAI-powered web search and URL content fetching.
Uses OpenAI's capabilities for web search and content analysis.
"""

import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
import re

class OpenAIWebSearch:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o"  # GPT-4o supports web capabilities
    
    async def search_web(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search the web using OpenAI's capabilities.
        Note: OpenAI doesn't have direct web search API, so we'll use GPT-4o with web browsing
        or fall back to providing search guidance.
        """
        try:
            # Use GPT-4o to provide web search results
            # Since OpenAI doesn't have direct web search, we'll use the model's knowledge
            # and provide it with search query context
            prompt = f"""
            Based on the following search query, provide the most relevant and current information:
            Query: {query}
            
            Provide information as if you searched the web for this query. Include:
            1. Key findings
            2. Best practices
            3. Current trends (as of 2024-2025)
            4. Actionable recommendations
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a web search assistant that provides current, accurate information based on web searches. Provide comprehensive, actionable answers."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            
            # Format as search results
            return [{
                "title": f"Web Search Results for: {query}",
                "snippet": content,
                "link": "OpenAI GPT-4o Knowledge"
            }]
            
        except Exception as e:
            logging.error(f"OpenAI web search error: {str(e)}")
            return []
    
    async def analyze_url_with_openai(self, url: str, query: str, web_content: Optional[str] = None) -> str:
        """
        Use OpenAI to analyze URL content in context of a query.
        If web_content is provided, analyze it. Otherwise, instruct GPT to analyze the URL.
        """
        try:
            if web_content:
                # Analyze the fetched content
                prompt = f"""
                Analyze the following web page content from {url} in response to this question: {query}
                
                Web Page Content:
                {web_content[:30000]}  # Limit to 30k chars
                
                Provide a comprehensive analysis with specific recommendations and actionable insights.
                """
            else:
                # Instruct GPT to analyze the URL conceptually
                prompt = f"""
                Based on the URL provided: {url}
                And the question: {query}
                
                Provide analysis and recommendations. If this is an Amazon listing URL, analyze:
                - Listing optimization opportunities
                - Image and video recommendations
                - A+ content suggestions
                - Pricing strategy
                - Conversion optimization
                - Competitive positioning
                
                Be specific and actionable.
                """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert Amazon listing optimization and e-commerce growth consultant. Provide detailed, actionable analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logging.error(f"OpenAI URL analysis error: {str(e)}")
            return f"Error analyzing URL: {str(e)}"
    
    def extract_urls_from_text(self, text: str) -> List[str]:
        """
        Extract URLs from text.
        """
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+[^\s<>"{}|\\^`\[\].,;:!?]'
        urls = re.findall(url_pattern, text)
        return urls
