"""
Document analysis utility for Excel files, PDFs, and other documents.
Uses OpenAI to analyze structured data.
"""

import logging
from typing import Optional, Dict, Any
from openai import OpenAI
import re

class DocumentAnalyzer:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o"
    
    async def analyze_excel_data(self, content: str, query: str) -> str:
        """
        Analyze Excel/CSV data content using OpenAI.
        """
        try:
            prompt = f"""
            Analyze the following data in response to this question: {query}
            
            Data:
            {content[:50000]}  # Limit to 50k chars
            
            Provide:
            1. Specific findings with column references
            2. Calculations and recommendations
            3. Numbered list of insights
            4. Actionable recommendations
            
            If asked about stock/inventory with sales forecasts, calculate restock amounts clearly.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert data analyst specializing in sales data, inventory management, and business intelligence. Provide detailed, numbered analysis with specific column references."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.2
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logging.error(f"Error analyzing Excel data: {str(e)}")
            return f"Error analyzing document: {str(e)}"
    
    async def analyze_transcript(self, transcript: str, query: str) -> str:
        """
        Analyze meeting transcript to extract action items and provide suggestions.
        """
        try:
            prompt = f"""
            Analyze this meeting transcript and answer: {query}
            
            Transcript:
            {transcript[:30000]}  # Limit to 30k chars
            
            Provide:
            1. Clear list of action items extracted
            2. Numbered suggestions for how to execute each action
            3. Format: "1) Actions were X, Y, Z. 2) For X you can do A, B, C..."
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing meeting transcripts and extracting actionable insights. Provide clear action items and execution suggestions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logging.error(f"Error analyzing transcript: {str(e)}")
            return f"Error analyzing transcript: {str(e)}"
    
    async def compare_listings(self, listing1_content: str, listing2_content: str, query: str) -> str:
        """
        Compare two Amazon listings and provide improvement suggestions.
        """
        try:
            prompt = f"""
            Compare these two Amazon listings and answer: {query}
            
            Listing 1:
            {listing1_content[:15000]}
            
            Listing 2:
            {listing2_content[:15000]}
            
            Provide:
            1. Price comparison and implications
            2. Content comparison (videos, images, A+ content)
            3. Specific improvement suggestions
            4. Format: "1) Your price is X, competitors are Y, therefore Z. 2) Competitors have 2 videos, you have 1..."
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert Amazon listing optimization consultant. Compare listings and provide specific, actionable improvement recommendations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logging.error(f"Error comparing listings: {str(e)}")
            return f"Error comparing listings: {str(e)}"
