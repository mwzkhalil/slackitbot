"""
LLM integration using OpenAI GPT-4.
Handles query processing and response generation.
"""

import openai
from typing import List, Dict, Any

class GPTIntegration:
    def __init__(self, api_key: str):
        openai.api_key = api_key
        self.model = "gpt-4"  # Assuming GPT-4, as GPT-5 doesn't exist yet

    def generate_response(self, query: str, context_docs: List[str], agent_purpose: str) -> str:
        """
        Generate a response using GPT-4 based on query and context.
        """
        context = "\n".join(context_docs)
        prompt = f"""
You are an AI agent with the following purpose: {agent_purpose}

Use only the provided context to answer the user's query. If the context does not contain relevant information, say "I don't have information on that."

Context:
{context}

Query: {query}

Answer:
"""
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating response: {str(e)}"