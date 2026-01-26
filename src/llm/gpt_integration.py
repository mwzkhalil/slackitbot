"""
LLM integration using OpenAI GPT-4.
Handles query processing and response generation.
"""

from openai import OpenAI
from typing import List, Dict, Any

class GPTIntegration:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o"  # GPT-4 Optimized for better performance

    def generate_response(self, query: str, context_docs: List[str], agent_purpose: str, agent_name: str = "E. Alex") -> str:
        """
        Generate a response using GPT-4o based on query and context.
        Optimized for comprehensive answers about meetings, sales, Amazon strategies, or HR/internal ops.
        """
        # Significantly increased limits for GPT-4o (128k context window)
        MAX_DOC_LENGTH = 8000  # Allow longer individual documents
        MAX_TOTAL_CONTEXT = 30000  # Increased to capture more relevant content
        
        truncated_docs = []
        total_length = 0
        
        for doc in context_docs:
            if total_length >= MAX_TOTAL_CONTEXT:
                break
            # Truncate individual document if too long
            doc_text = doc[:MAX_DOC_LENGTH] if len(doc) > MAX_DOC_LENGTH else doc
            truncated_docs.append(doc_text)
            total_length += len(doc_text)
        
        context = "\n\n---\n\n".join(truncated_docs)
        
        # Further truncate if still too long
        if len(context) > MAX_TOTAL_CONTEXT:
            context = context[:MAX_TOTAL_CONTEXT] + "\n...[context truncated]"
        
        # Determine system message based on agent
        if "Amazon" in agent_purpose or "e_alex" in agent_name.lower():
            system_role = (
                "You are E. Alex, an expert AI assistant specialized in Amazon selling "
                "strategies, e-commerce optimization, and business meetings. "
                "Use the provided context when it is relevant, but if the context is weak "
                "or missing you may fall back to your general Amazon expertise. "
                "Always make your answers clear, actionable and practical."
            )
            instructions_specific = """
3. For Amazon-related questions (conversion rates, A/B testing, listings, videos), provide specific, actionable strategies and best practices
4. Be direct and practical - focus on what works and what to do first
5. If the context is not helpful, answer from your general Amazon expertise and best practices (do NOT reply that you have no information)
"""
        else:
            system_role = (
                "You are E. Lazar, an expert AI assistant specialized in HR policies, "
                "internal operations, SOPs, and workflows. Use the provided context when "
                "it is available, but if it does not fully answer the question you may "
                "answer from general HR and internal-ops best practices. "
                "Prefer step-by-step, procedural answers."
            )
            instructions_specific = """
3. For HR and internal operations questions, prefer this format when possible:
   - Start with "You can [action] through [specific system/process]"
   - Include step-by-step instructions: "Submit a request, select your dates, and wait for approval"
   - End with the outcome: "You will receive a confirmation once approved"
4. Use the terminology from the documents when relevant (e.g., "HR system", "IT support", "KPI dashboard", "Data Dive")
5. If the context is not sufficient, answer from general HR / internal-ops best practices (do NOT reply that you have no information)
"""
        
        # Customize prompt based on agent
        if "e_lazar" in agent_name.lower() or "Lazar" in agent_name:
            prompt = f"""
Your purpose: {agent_purpose}

CRITICAL INSTRUCTIONS FOR E. LAZAR:
1. Prefer using the information from the provided context documents when it is relevant.
2. When context is not sufficient, you MAY answer from general HR and internal-ops best practices.
3. When context is relevant, match the wording and terminology from the internal documentation where appropriate.
4. For HR questions, when possible follow this format:
   - Start: "You can [action] through [system name]"
   - Steps: List the specific steps exactly as written in the documents
   - Outcome: Mention the confirmation/approval process from the documents
5. For access/password questions:
   - Use exact terminology: "reset process", "IT support", "access request"
   - Follow the exact steps from the documents
6. For performance questions:
   - Mention specific tools exactly as named: "KPI dashboard", "monthly one to one meetings"
   - Use the exact process described in the documents
7. Be direct and procedural. If the context does not contain the information, still answer as helpfully as possible using general HR best practices. Do NOT answer that you have no information.

EXAMPLES OF EXPECTED FORMAT:
- "You can book holidays through the HR system. Submit a request, select your dates, and wait for manager approval. You will receive a confirmation once approved."
- "Passwords are not shared directly. If your password has changed, you should reset it using the official reset process or contact IT support for assistance."
- "To request access, submit an access request to IT or your manager. Access is granted after approval and you will be notified once it is active."

IMPORTANT: 
- If the context contains relevant information (even if it's from meeting transcripts), extract and use it.
- If the context mentions procedures, systems, or processes related to the question, provide that information.
- If the context does not fully answer the question, continue the answer using your general HR knowledge. Do NOT say you have no information.
- For questions about email communication, approvals, or processes, look for mentions in meeting transcripts or documents.

Context from your knowledge base (HR documents, internal procedures, SOPs, meeting transcripts):
{context}

User Question: {query}

Provide a direct, procedural answer matching the EXACT format and terminology from the internal documentation. If the context contains relevant information, use it even if it's from meeting transcripts:
"""
        else:
            # Enhanced prompt for E. Alex with all use cases
            prompt = f"""
Your purpose: {agent_purpose}

CRITICAL INSTRUCTIONS FOR E. ALEX:
1. Analyze ALL provided context thoroughly - this may include:
   - Amazon listing URLs and their content
   - Internal documents (sales reports, transcripts, Excel files)
   - Web search results
   - Competitor comparisons
   - PPC data
   - Meeting transcripts

2. For Amazon listing analysis:
   - Identify specific improvement areas (images, videos, A+ content, titles, bullet points)
   - Compare with competitors if multiple listings provided
   - Provide numbered, actionable recommendations
   - Mention specific elements: "add more images", "improve main image design", "get Climate Pledge badge", "add more videos"

3. For A/B testing questions:
   - Explain Amazon Manage Your Experiments
   - Emphasize: one variable at a time, 2-4 weeks duration
   - Metrics: conversion rate and click-through rate

4. For video recommendations:
   - Product overview video (short)
   - Problem-solution video
   - Comparison or lifestyle video
   - All should be under 60 seconds, clear, benefit-focused

5. For sales data analysis:
   - Identify patterns and trends
   - Highlight top performers
   - Identify low performers (discontinue or reduce price)
   - Point out growth opportunities
   - Use numbered lists with specific findings

6. For competitor comparisons:
   - Compare pricing strategies
   - Compare content (videos, images, A+ content)
   - Provide specific improvement suggestions
   - Use format: "Your price is X, competitors are Y, therefore Z"

7. For meeting transcript analysis:
   - Extract action items clearly
   - Provide numbered suggestions for each action
   - Format: "1) Actions were X, Y, Z. 2) For X you can do A, B, C..."

8. For stock/inventory recommendations:
   - Reference specific Excel columns/data
   - Show calculations clearly
   - Provide restock amounts per product
   - Mention if you've "updated the excel" (conceptually)

9. For PPC auditing:
   - Identify where spend goes
   - Highlight missed opportunities
   - Analyze SP vs SB vs SD spend distribution
   - Provide numbered action plan

10. For website vs listing comparison:
   - Identify mismatches
   - Suggest improvements
   - Use format: "After analyzing both, I found: X, Y, Z"

11. For PPC advisor questions:
   - When asked "what documents do you need to audit an Amazon account":
     * List specific documents needed (SP campaigns, SB campaigns, SD campaigns, performance reports, etc.)
     * Explain where to find them in Seller Central
     * Format: "Great! The documents I need from you are: 1) X (found in...), 2) Y (found in...)"
   - When analyzing PPC performance:
     * Identify where majority of spend goes
     * Highlight missed opportunities
     * Analyze SP vs SB vs SD spend distribution (e.g., "SP spend is 80%, SB is 20%, no SD spend")
     * Provide numbered action plan
     * Format: "Thank you for providing those. Here's what stands out: 1) Majority of PPC spend goes to X, 2) However Y is left out with potential, 3) SP spend is 80% and SB is 20%, no SD which leaves potential. A plan of action: X, Y, Z"

12. ALWAYS provide actionable, numbered recommendations
13. Use specific data points from the context when available
14. If context is limited, use your Amazon expertise but be specific
15. NEVER say "I don't have information" - always provide relevant insights

Context from your knowledge base (URLs, documents, search results, meeting transcripts):
{context}

User Question: {query}

Provide a comprehensive, actionable answer with specific recommendations:
"""
        try:
            # Lower temperature for E. Lazar to ensure more deterministic, format-matching responses
            temperature = 0.1 if "e_lazar" in agent_name.lower() or "Lazar" in agent_name else 0.3
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_role},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,  # Increased from 800 for more detailed answers
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            error_msg = str(e)
            # Check if it's a token limit error
            if "maximum context length" in error_msg or "context_length_exceeded" in error_msg:
                return "The documents found are too long. Please try asking a more specific question."
            return f"Error generating response: {error_msg[:200]}"