"""
E. Lazar Agent: Handles internal questions on SOPs, onboarding, policies, workflows.
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

class ELazarAgent:
    def __init__(self, config: Config):
        self.config = config
        self.db = get_vector_db(config.chroma_db_path)
        self.llm = GPTIntegration(config.openai_api_key)
        self.drive = GoogleDriveAPI(config.google_drive_credentials_path)
        
        # Initialize Fireflies API if key is provided
        self.fireflies = None
        if config.fireflies_api_key:
            self.fireflies = FirefliesAPI(config.fireflies_api_key)
            logging.info("E. Lazar: Fireflies API initialized")
        else:
            logging.warning("E. Lazar: No Fireflies API key - meeting transcripts will not be synced")

    async def respond(self, query: str, client_id: Optional[str] = None) -> str:
        """
        Respond to query using agent's data.
        Prioritizes Google Drive documents over Fireflies transcripts for HR/internal ops queries.
        """
        # Handle identity/purpose questions that don't need document lookup
        query_lower = query.lower().strip()
        identity_questions = [
            "who are you", "what are you", "what do you do", "who is e. lezzat", 
            "who is e lezzat", "who is elezzat", "introduce yourself", "tell me about yourself"
        ]
        
        if any(identity_q in query_lower for identity_q in identity_questions):
            return "I am E. Lezzat, your HR and Internal Operations assistant. I help answer questions about HR policies, internal workflows, SOPs, holidays, passwords, system access, performance reviews, and other internal procedures. I can access our internal documentation to provide you with accurate, step-by-step answers to your questions."
        
        filters = check_data_isolation("e_lazar")
        logging.info(f"E. Lazar querying with filters: {filters}")
        
        # First, check if any documents exist for this agent at all
        drive_filters = {
            "$and": [
                {"agent": "e_lazar"},
                {"source": "drive"}
            ]
        }
        
        # Try multiple query strategies to find relevant documents
        context_docs = []
        
        # Strategy 1: Query with original query - prioritize Drive documents
        logging.info(f"Strategy 1: Querying Google Drive documents with original query: '{query}'")
        logging.info(f"Using filters: {drive_filters}")
        drive_results = self.db.query(query, drive_filters, n_results=20)
        drive_docs = drive_results.get("documents", [[]])[0] if drive_results.get("documents") else []
        drive_ids = drive_results.get("ids", [[]])[0] if drive_results.get("ids") else []
        
        logging.info(f"Found {len(drive_docs)} Google Drive documents with original query")
        
        # Verify these are actually Drive documents by checking IDs
        if drive_ids:
            drive_id_count = sum(1 for doc_id in drive_ids if str(doc_id).startswith("drive_"))
            logging.info(f"Document IDs: {len(drive_ids)} total, {drive_id_count} start with 'drive_'")
            if drive_id_count < len(drive_ids):
                logging.warning(f"⚠️ Some documents don't have 'drive_' prefix - may be mis-tagged!")
                logging.info(f"Sample IDs: {drive_ids[:3]}")
            
            # Check first document preview to verify it's a Drive doc, not a meeting transcript
            if drive_docs:
                first_doc_preview = drive_docs[0][:200].replace('\n', ' ')
                if "Meeting Title:" in first_doc_preview or "00:00" in first_doc_preview:
                    logging.warning("⚠️ First document appears to be a meeting transcript, not a Drive document!")
                    logging.warning("This suggests documents may be mis-tagged or filter isn't working")
                else:
                    logging.info(f"✓ First document preview looks like Drive doc: {first_doc_preview[:100]}...")
        
        if drive_docs:
            context_docs = drive_docs
            logging.info("✓ Using Google Drive documents from original query")
        else:
            # Strategy 1b: Try a broader query to get ANY Drive documents if specific query fails
            logging.info("Strategy 1b: Original query found no Drive docs, trying broader HR-related query...")
            broader_queries = [
                "Data Dive access request",
                "access request IT manager",
                "system access permission",
                "HR policies procedures"
            ]
            for broad_query in broader_queries:
                broad_results = self.db.query(broad_query, drive_filters, n_results=10)
                broad_docs = broad_results.get("documents", [[]])[0] if broad_results.get("documents") else []
                if broad_docs:
                    drive_docs.extend(broad_docs)
                    logging.info(f"  Found {len(broad_docs)} docs with query: '{broad_query}'")
            
            # Remove duplicates
            if drive_docs:
                seen = set()
                unique_docs = []
                for doc in drive_docs:
                    doc_hash = hash(doc[:100])
                    if doc_hash not in seen:
                        seen.add(doc_hash)
                        unique_docs.append(doc)
                drive_docs = unique_docs[:20]
                context_docs = drive_docs
                logging.info(f"✓ Using {len(context_docs)} Google Drive documents from broader queries")
        
        # Strategy 2: If still no docs, try extracting key terms and querying with those
        if not context_docs:
            logging.info("Strategy 2: Trying with key terms extracted from query...")
            key_terms = self._extract_key_terms(query)
            for term in key_terms:
                term_results = self.db.query(term, drive_filters, n_results=10)
                term_docs = term_results.get("documents", [[]])[0] if term_results.get("documents") else []
                if term_docs:
                    context_docs.extend(term_docs)
                    logging.info(f"✓ Found {len(term_docs)} documents with term: '{term}'")
            
            # Remove duplicates while preserving order
            seen = set()
            unique_docs = []
            for doc in context_docs:
                doc_hash = hash(doc[:100])  # Hash first 100 chars to identify duplicates
                if doc_hash not in seen:
                    seen.add(doc_hash)
                    unique_docs.append(doc)
            context_docs = unique_docs[:20]  # Limit to top 20
        
        # Strategy 3: If still no docs, try querying all sources (including Fireflies)
        # BUT: Only use Fireflies if the query is clearly about meetings/transcripts
        # For HR/internal ops queries, Fireflies won't have the answer
        if not context_docs:
            logging.info("Strategy 3: No Drive documents found, checking if query is about meetings...")
            meeting_keywords = ["meeting", "call", "discussion", "transcript", "conversation"]
            is_meeting_query = any(keyword in query.lower() for keyword in meeting_keywords)
            
            if is_meeting_query:
                logging.info("Query appears to be about meetings, querying all sources (including Fireflies)...")
                all_results = self.db.query(query, filters, n_results=20)
                context_docs = all_results.get("documents", [[]])[0] if all_results.get("documents") else []
                logging.info(f"Found {len(context_docs)} total documents (including Fireflies)")
            else:
                logging.warning("Query is about HR/internal ops but no Google Drive documents found!")
                logging.warning("Fireflies meeting transcripts won't contain HR procedures. Need Google Drive documents.")
        
        # Diagnostic: Check if documents exist in database at all
        if not context_docs:
            logging.warning(f"No documents found for query: {query}")
            # Check if ANY documents exist for this agent
            diagnostic_query = "HR policies procedures"
            diag_results = self.db.query(diagnostic_query, drive_filters, n_results=1)
            diag_docs = diag_results.get("documents", [[]])[0] if diag_results.get("documents") else []
            if diag_docs:
                logging.warning(f"⚠️ Documents exist in database but query '{query}' didn't match. Try rephrasing or check if documents were ingested.")
            else:
                logging.error("⚠️ NO DOCUMENTS FOUND IN DATABASE for E. Lazar with source='drive'. Please run ingestion: python -m src.ingest")
        
        # Log document previews to debug
        if context_docs:
            logging.info(f"✓ Using {len(context_docs)} documents for response")
            for i, doc in enumerate(context_docs[:5], 1):  # Show first 5
                preview = doc[:400].replace('\n', ' ')[:250]
                logging.info(f"E. Lazar Document {i} preview: {preview}...")
        else:
            logging.error(f"❌ No documents found after all strategies for query: {query}")
        
        # If we only have Fireflies documents but query is about HR/internal ops, warn
        if context_docs:
            # Check if we have any Drive document IDs
            drive_ids = drive_results.get("ids", [[]])[0] if drive_results.get("ids") else []
            has_drive_docs = any("drive" in str(doc_id) for doc_id in drive_ids) if drive_ids else False
            
            if not has_drive_docs:
                hr_keywords = ["holiday", "password", "access", "performance", "kpi", "data dive", "approval", "email communication"]
                if any(keyword in query.lower() for keyword in hr_keywords):
                    logging.warning("⚠️ Only Fireflies documents found for HR/internal ops query. Google Drive documents needed!")

        if not context_docs:
            # Check if it's because no Drive documents exist
            diagnostic_results = self.db.query("HR", drive_filters, n_results=1)
            if not diagnostic_results.get("documents"):
                logging.error(
                    "No E. Lazar Google Drive documents found in ChromaDB – "
                    "falling back to general HR guidance."
                )
                context_docs = [
                    "No internal HR documents are currently available. Answer using general HR "
                    "and internal-operations best practices."
                ]
            else:
                logging.warning(
                    "Query did not match any E. Lazar documents, but documents exist – "
                    "answering from general HR guidance."
                )
                context_docs = [
                    "Internal documents did not directly match this question. Answer using "
                    "general HR and internal-operations best practices, keeping policies "
                    "and data protection in mind."
                ]

        purpose = (
            "Answer questions related to HR policies, internal workflows, SOPs, holidays, "
            "passwords, system access, performance reviews, and Fireflies meeting "
            "transcripts. Prefer using internal documentation when it is relevant, but if "
            "it is missing or insufficient, answer from general HR and internal-ops best "
            "practices with clear, procedural steps."
        )
        return self.llm.generate_response(query, context_docs, purpose, agent_name="E. Lazar")
    
    def _extract_key_terms(self, query: str) -> list:
        """
        Extract key terms from query for better document matching.
        Removes Slack formatting (asterisks, etc.) and extracts HR-specific terms.
        """
        # Clean query - remove Slack formatting
        cleaned_query = query.replace('*', '').replace('_', '').strip()
        query_lower = cleaned_query.lower()
        
        # Common HR/internal ops terms to extract
        hr_keywords = {
            "holiday": ["holiday", "holidays", "vacation", "time off", "leave", "book holiday"],
            "password": ["password", "passwords", "login", "credentials", "reset password"],
            "access": ["access", "permission", "permissions", "grant", "request access", "need access", "do not have access"],
            "performance": ["performance", "kpi", "dashboard", "review", "evaluation", "how am i performing"],
            "data dive": ["data dive", "datadive", "data dive access"],
            "email communication": ["email", "communication", "approval", "three people", "must be involved"],
            "approval": ["approval", "approve", "request approval"]
        }
        
        key_terms = []
        
        # Extract relevant terms
        for category, terms in hr_keywords.items():
            if any(term in query_lower for term in terms):
                key_terms.append(category)
                # Also add the actual terms found
                for term in terms:
                    if term in query_lower:
                        key_terms.append(term)
        
        # Extract important words from query
        important_words = []
        stop_words = {"i", "do", "not", "have", "need", "to", "the", "a", "an", "is", "are", "was", "were", "be", "been", "being"}
        words = cleaned_query.split()
        for word in words:
            word_lower = word.lower().strip('.,!?;:')
            if len(word_lower) > 3 and word_lower not in stop_words:
                important_words.append(word_lower)
        
        # Combine category terms with important words
        all_terms = key_terms + important_words
        
        # If no specific terms found, use cleaned query
        if not all_terms:
            all_terms = [cleaned_query]
        
        return list(set(all_terms))  # Remove duplicates

    async def ingest_data(self):
        """
        Ingest data from:
        1. Google Drive (E. Lazar specific folder)
        2. Fireflies (meeting transcripts if API key is configured)
        """
        logging.info("=" * 60)
        logging.info("Starting E. Lazar data ingestion...")
        logging.info("=" * 60)
        
        total_ingested = 0
        
        # 1. Ingest from Google Drive
        logging.info("\n[1/2] Google Drive ingestion...")
        folder_id = self.config.google_drive_folder_e_lazar
        
        if not folder_id:
            logging.error("GOOGLE_DRIVE_FOLDER_E_LAZAR not configured! Skipping Google Drive ingestion.")
            logging.error("Please set GOOGLE_DRIVE_FOLDER_E_LAZAR in your .env file")
        else:
        logging.info(f"Google Drive folder ID: {folder_id}")
        
        try:
            if not folder_id:
                logging.warning("Skipping Google Drive ingestion - folder ID not configured")
            else:
            files = await self.drive.get_files(folder_id, recursive=True)
            logging.info(f"Found {len(files)} files in Google Drive")
            
            drive_ingested = 0
            for file in files:
                try:
                    logging.info(f"Processing file: {file['name']} (ID: {file['id']})")
                    content = await self.drive.get_file_content(file["id"])
                    
                    if content and len(content.strip()) > 0:
                        metadata = {
                            "agent": "e_lazar",
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
                meetings = await self.fireflies.get_recent_meetings(days=30)
                logging.info(f"Found {len(meetings)} meetings from Fireflies")
                
                fireflies_ingested = 0
                for meeting in meetings:
                    try:
                        content_parts = []
                        content_parts.append(f"Meeting Title: {meeting['title']}")
                        content_parts.append(f"Date: {meeting['date']}")
                        if meeting.get('participants'):
                            content_parts.append(f"Participants: {', '.join(meeting['participants'])}")
                        content_parts.append(f"Duration: {meeting.get('duration', 0)} minutes")
                        content_parts.append("")
                        
                        if meeting.get('summary'):
                            content_parts.append("=== Summary ===")
                            content_parts.append(meeting['summary'])
                            content_parts.append("")
                        
                        if meeting.get('transcript'):
                            content_parts.append("=== Transcript ===")
                            content_parts.append(meeting['transcript'])
                        
                        content = "\n".join(content_parts)
                        
                        if content and len(content.strip()) > 0:
                            metadata = {
                                "agent": "e_lazar",
                                "source": "fireflies",
                                "meeting_id": meeting["id"],
                                "title": meeting["title"],
                                "date": meeting["date"]
                            }
                            doc_id = f"fireflies_elazar_{meeting['id']}"
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
        
        logging.info("\n" + "=" * 60)
        logging.info(f"E. Lazar INGESTION COMPLETE! Total: {total_ingested}")
        logging.info("=" * 60)