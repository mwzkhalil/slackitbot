"""
E. Alex Agent: Handles client meetings, internal meetings, shared project documents.
Data sources: Google Drive + Fireflies meeting transcripts
"""

import logging
from typing import Optional
from src.utils.config import Config
from src.utils.database import get_vector_db
from src.utils.security import check_data_isolation
from src.llm.gpt_integration import GPTIntegration
from src.data_ingestion.google_drive import GoogleDriveAPI
from src.data_ingestion.fireflies_api import FirefliesAPI
from src.data_ingestion.google_search import GoogleSearchAPI
from src.data_ingestion.web_scraper import WebScraper
from src.data_ingestion.openai_web_search import OpenAIWebSearch
from src.data_ingestion.document_analyzer import DocumentAnalyzer

class EAlexAgent:
    def __init__(self, config: Config):
        self.config = config
        self.db = get_vector_db(config.chroma_db_path)
        self.llm = GPTIntegration(config.openai_api_key)
        self.drive = GoogleDriveAPI(config.google_drive_credentials_path)
        
        # Initialize Fireflies API if key is provided
        self.fireflies = None
        if config.fireflies_api_key:
            self.fireflies = FirefliesAPI(config.fireflies_api_key)
            logging.info("Fireflies API initialized")
        else:
            logging.warning("No Fireflies API key - meeting transcripts will not be synced")
        
        # Initialize Google Search API for Amazon queries (optional)
        self.google_search = None
        if config.google_search_api_key and config.google_search_engine_id:
            self.google_search = GoogleSearchAPI(config.google_search_api_key, config.google_search_engine_id)
            logging.info("Google Search API initialized for Amazon queries")
        else:
            logging.warning("No Google Search API configured - Amazon queries will use ChromaDB only")
        
        # Initialize web scraping, OpenAI web search, and document analysis
        self.web_scraper = WebScraper()
        self.openai_web = OpenAIWebSearch(config.openai_api_key)
        self.document_analyzer = DocumentAnalyzer(config.openai_api_key)
        logging.info("Web scraping, OpenAI web search, and document analysis initialized")

    async def respond(self, query: str, client_id: Optional[str] = None) -> str:
        """
        Respond to query using agent's data, web search, URL fetching, and document analysis.
        """
        # Handle identity/purpose questions that don't need document lookup
        query_lower = query.lower().strip()
        identity_questions = [
            "who are you", "what are you", "what do you do", "who is e. alex", 
            "who is e alex", "who is ealex", "introduce yourself", "tell me about yourself"
        ]
        
        if any(identity_q in query_lower for identity_q in identity_questions):
            return "I am E. Alex, your Sales and Amazon Growth assistant. I help answer questions about Amazon listings, conversion optimization, A/B testing, sales strategies, client meetings, and business growth. I can access your sales documents, meeting transcripts, analyze Amazon listings from URLs, compare competitors, analyze PPC data, and provide actionable recommendations."
        
        filters = check_data_isolation("e_alex")
        logging.info(f"E. Alex querying with filters: {filters}")
        
        # Extract URLs from query
        urls = self.openai_web.extract_urls_from_text(query)
        amazon_urls = [url for url in urls if 'amazon.' in url.lower() or 'amzn.' in url.lower()]
        other_urls = [url for url in urls if url not in amazon_urls]
        
        # Fetch and analyze URLs
        url_contexts = []
        amazon_listing_contents = {}  # Store for comparison
        
        if amazon_urls:
            logging.info(f"Found {len(amazon_urls)} Amazon URL(s) in query")
            for url in amazon_urls:
                try:
                    # Fetch URL content
                    content = await self.web_scraper.fetch_url_content(url)
                    if content:
                        # Extract structured info
                        listing_info = self.web_scraper.extract_amazon_listing_info(url, content)
                        formatted_info = self.web_scraper.format_listing_info(listing_info)
                        url_contexts.append(formatted_info)
                        amazon_listing_contents[url] = content  # Store for comparison
                        logging.info(f"✓ Fetched and analyzed Amazon listing: {url}")
                except Exception as e:
                    logging.error(f"Error fetching Amazon URL {url}: {str(e)}")
            
            # If multiple listings and comparison is needed, do comparison analysis
            if len(amazon_listing_contents) >= 2 and needs_comparison:
                logging.info("Multiple listings found - performing comparison analysis")
                urls_list = list(amazon_listing_contents.keys())
                comparison_result = await self.document_analyzer.compare_listings(
                    amazon_listing_contents[urls_list[0]],
                    amazon_listing_contents[urls_list[1]],
                    query
                )
                url_contexts.append(f"=== Listing Comparison Analysis ===\n\n{comparison_result}\n")
        
        if other_urls:
            logging.info(f"Found {len(other_urls)} other URL(s) in query")
            for url in other_urls:
                try:
                    content = await self.web_scraper.fetch_url_content(url)
                    if content:
                        url_contexts.append(f"=== Content from {url} ===\n\n{content[:20000]}\n")
                        logging.info(f"✓ Fetched content from URL: {url}")
                except Exception as e:
                    logging.error(f"Error fetching URL {url}: {str(e)}")
        
        # Check for PPC advisor questions
        if "ppc advisor" in query_lower or "audit an amazon account" in query_lower or "what documents do you need" in query_lower:
            logging.info("PPC advisor question detected")
            # This will be handled by the enhanced prompt which includes PPC advisor instructions
        
        # Check if this is an Amazon-related query
        amazon_keywords = ["amazon", "listing", "conversion", "a/b test", "ab test", "split test", "video", "a plus content", "ppc", "advertising", "assess ppc", "ppc performance"]
        query_lower = query.lower()
        is_amazon_query = any(keyword in query_lower for keyword in amazon_keywords)
        
        # Check if query is asking for document analysis
        analysis_keywords = {
            "excel": ["excel", "spreadsheet", "stock report", "sales data", "inventory", "restock"],
            "transcript": ["transcript", "call", "meeting transcript", "actions", "action items"],
            "ppc": ["ppc", "advertising", "spend", "campaign", "audit"],
            "comparison": ["compare", "competitor", "competitors", "vs", "versus", "difference"]
        }
        
        needs_excel_analysis = any(kw in query_lower for kw in analysis_keywords["excel"])
        needs_transcript_analysis = any(kw in query_lower for kw in analysis_keywords["transcript"])
        needs_ppc_analysis = any(kw in query_lower for kw in analysis_keywords["ppc"])
        needs_comparison = any(kw in query_lower for kw in analysis_keywords["comparison"])
        
        # Query ChromaDB for internal documents
        results = self.db.query(query, filters)
        context_docs = results.get("documents", [[]])[0] if results.get("documents") else []
        
        logging.info(f"Found {len(context_docs)} internal documents for query: {query}")
        if context_docs:
            # Log first 500 chars of each document to see what content we have
            for i, doc in enumerate(context_docs[:3], 1):
                preview = doc[:500].replace('\n', ' ')[:200]
                logging.info(f"Document {i} preview ({len(doc)} chars): {preview}...")
            
            # If specific analysis is needed, use document analyzer
            if needs_excel_analysis:
                # Find Excel/CSV-like documents
                excel_docs = [doc for doc in context_docs if any(x in doc.lower() for x in ['excel', 'csv', 'column', 'row', 'sales', 'stock', 'inventory'])]
                if excel_docs:
                    logging.info("Excel analysis requested - using document analyzer")
                    excel_content = "\n\n---\n\n".join(excel_docs[:3])  # Use top 3 Excel-like docs
                    analysis_result = await self.document_analyzer.analyze_excel_data(excel_content, query)
                    url_contexts.append(f"=== Excel Data Analysis ===\n\n{analysis_result}\n")
            
            if needs_transcript_analysis:
                # Find transcript-like documents
                transcript_docs = [doc for doc in context_docs if any(x in doc.lower() for x in ['transcript', 'meeting', 'call', '00:00', 'speaker'])]
                if transcript_docs:
                    logging.info("Transcript analysis requested - using document analyzer")
                    transcript_content = "\n\n---\n\n".join(transcript_docs[:2])  # Use top 2 transcripts
                    analysis_result = await self.document_analyzer.analyze_transcript(transcript_content, query)
                    url_contexts.append(f"=== Transcript Analysis ===\n\n{analysis_result}\n")
            
            if needs_ppc_analysis:
                # Find PPC-related documents
                ppc_docs = [doc for doc in context_docs if any(x in doc.lower() for x in ['ppc', 'sponsored', 'advertising', 'campaign', 'spend'])]
                if ppc_docs:
                    logging.info("PPC analysis requested - analyzing PPC documents")
                    ppc_content = "\n\n---\n\n".join(ppc_docs[:3])
                    url_contexts.append(f"=== PPC Data ===\n\n{ppc_content[:20000]}\n")

        # If Amazon-related query and Google Search is available, enhance with search results
        search_context = ""
        if is_amazon_query and self.google_search:
            logging.info(f"Amazon-related query detected, fetching Google Search results...")
            search_results = await self.google_search.search_amazon(query, num_results=3)
            if search_results:
                search_context = self.google_search.format_search_results(search_results)
                logging.info(f"Added {len(search_results)} Google Search results to context")
        
        # Also use OpenAI web search for general queries
        if not search_context and is_amazon_query:
            logging.info("Using OpenAI web search for Amazon best practices...")
            openai_search_results = await self.openai_web.search_web(query, num_results=3)
            if openai_search_results:
                search_context = "\n\n".join([f"{r['title']}\n{r['snippet']}" for r in openai_search_results])
                logging.info("Added OpenAI web search results to context")
        
        # Combine all contexts: URLs first (most specific), then search, then internal docs
        all_context_docs = []
        if url_contexts:
            all_context_docs.extend(url_contexts)
        if search_context:
            all_context_docs.append(search_context)
        all_context_docs.extend(context_docs)

        # If we still have no context, fall back to answering from general expertise
        if not all_context_docs:
            logging.warning(
                "No documents found for E. Alex query – falling back to general Amazon expertise."
            )
            all_context_docs = [
                "No internal documents matched this question. Answer using general Amazon "
                "selling and e‑commerce best practices."
            ]

        # Enhanced purpose for all use cases
        purpose = (
            "You are E. Alex, an expert Amazon sales and growth consultant. Answer questions about: "
            "1. Amazon listing optimization (images, videos, A+ content, titles, bullet points) "
            "2. A/B testing on Amazon using Manage Your Experiments "
            "3. Sales data analysis and pattern identification "
            "4. Competitor comparison and listing improvements "
            "5. Meeting transcript analysis and action items "
            "6. Stock/inventory recommendations based on sales forecasts "
            "7. Amazon PPC auditing and optimization "
            "8. Website vs Amazon listing comparison "
            "9. Conversion rate optimization strategies "
            "10. General Amazon best practices and strategies. "
            "When analyzing URLs, documents, or data, provide specific, actionable recommendations "
            "with numbered lists and clear next steps. Always be practical and focused on growth."
        )
        return self.llm.generate_response(query, all_context_docs, purpose, agent_name="E. Alex")

    async def ingest_data(self):
        """
        Ingest data from:
        1. Google Drive (My Drive/AI/e-ALex with all subfolders)
        2. Fireflies (meeting transcripts if API key is configured)
        """
        logging.info("=" * 60)
        logging.info("Starting E. Alex data ingestion...")
        logging.info("=" * 60)
        
        total_ingested = 0
        
        # 1. Ingest from Google Drive
        logging.info("\n[1/2] Google Drive ingestion...")
        folder_id = self.config.google_drive_folder_e_alex
        logging.info(f"Google Drive folder ID: {folder_id}")
        
        try:
            # Get all files recursively from folder and subfolders
            files = await self.drive.get_files(folder_id, recursive=True)
            logging.info(f"Found {len(files)} files in Google Drive")
            
            drive_ingested = 0
            for file in files:
                try:
                    logging.info(f"Processing file: {file['name']} (ID: {file['id']})")
                    content = await self.drive.get_file_content(file["id"])
                    
                    if content and len(content.strip()) > 0:
                        metadata = {
                            "agent": "e_alex", 
                            "source": "drive", 
                            "file_id": file["id"], 
                            "name": file["name"]
                        }
                        doc_id = f"drive_{file['id']}"
                        self.db.add_documents([content], [metadata], [doc_id])
                        drive_ingested += 1
                        logging.info(f"✓ Ingested: {file['name']} ({len(content)} chars)")
                    else:
                        logging.warning(f"✗ Skipped (empty): {file['name']}")
                except Exception as e:
                    logging.error(f"✗ Error processing {file.get('name', 'unknown')}: {str(e)}")
            
            total_ingested += drive_ingested
            logging.info(f"Google Drive complete: {drive_ingested}/{len(files)} files ingested")
        except Exception as e:
            logging.error(f"Error during Google Drive ingestion: {str(e)}")
        
        # 2. Ingest from Fireflies
        if self.fireflies:
            logging.info("\n[2/2] Fireflies meeting transcripts ingestion...")
            try:
                # Fetch recent meetings (last 30 days to capture all relevant meetings)
                meetings = await self.fireflies.get_recent_meetings(days=30)
                logging.info(f"Found {len(meetings)} meetings from Fireflies")
                
                fireflies_ingested = 0
                for meeting in meetings:
                    try:
                        # Combine transcript and summary for better context
                        content_parts = []
                        
                        # Add meeting title and metadata
                        content_parts.append(f"Meeting Title: {meeting['title']}")
                        content_parts.append(f"Date: {meeting['date']}")
                        if meeting.get('participants'):
                            content_parts.append(f"Participants: {', '.join(meeting['participants'])}")
                        content_parts.append(f"Duration: {meeting.get('duration', 0)} minutes")
                        content_parts.append("")
                        
                        # Add summary if available
                        if meeting.get('summary'):
                            content_parts.append("=== Summary ===")
                            content_parts.append(meeting['summary'])
                            content_parts.append("")
                        
                        # Add full transcript
                        if meeting.get('transcript'):
                            content_parts.append("=== Transcript ===")
                            content_parts.append(meeting['transcript'])
                        
                        content = "\n".join(content_parts)
                        
                        if content and len(content.strip()) > 0:
                            metadata = {
                                "agent": "e_alex",
                                "source": "fireflies",
                                "meeting_id": meeting["id"],
                                "title": meeting["title"],
                                "date": meeting["date"]
                            }
                            doc_id = f"fireflies_{meeting['id']}"
                            self.db.add_documents([content], [metadata], [doc_id])
                            fireflies_ingested += 1
                            logging.info(f"✓ Ingested meeting: {meeting['title']} ({len(content)} chars)")
                        else:
                            logging.warning(f"✗ Skipped (empty): {meeting['title']}")
                    except Exception as e:
                        logging.error(f"✗ Error processing meeting {meeting.get('title', 'unknown')}: {str(e)}")
                
                total_ingested += fireflies_ingested
                logging.info(f"Fireflies complete: {fireflies_ingested}/{len(meetings)} meetings ingested")
            except Exception as e:
                logging.error(f"Error during Fireflies ingestion: {str(e)}")
        else:
            logging.info("\n[2/2] Fireflies skipped (no API key configured)")
        
        # Final summary
        logging.info("\n" + "=" * 60)
        logging.info(f"INGESTION COMPLETE! Total documents ingested: {total_ingested}")
        logging.info("=" * 60)
