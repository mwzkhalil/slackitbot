"""
Add sample data to ChromaDB for prototyping and testing.
Run this to quickly populate the database without needing Google Drive.
"""

from src.utils.database import get_vector_db
from src.utils.config import Config
from dotenv import load_dotenv

load_dotenv()
config = Config()

# Get database instance
db = get_vector_db(config.chroma_db_path)

# Sample data for E. Alex (meetings and project docs)
e_alex_docs = [
    "Meeting with Client ABC on December 15, 2025. Discussed new feature requirements for the mobile app. Participants: John Smith, Sarah Lee. Key takeaways: Need dark mode, push notifications, and offline support.",
    "Internal team meeting on January 2, 2026. Project status review - Dashboard redesign is 80% complete. Need to finalize API integration by next week. Team members: Mike, Jessica, Tom.",
    "Project Overview: Mobile App Redesign. Goals: Improve user experience, add new features, reduce load time by 30%. Timeline: 3 months. Budget: $50,000.",
    "Client feedback: Users love the new interface but requesting better search functionality and faster page load times.",
]

e_alex_metadata = [
    {"agent": "e_alex", "source": "manual", "name": "client_abc_meeting.txt"},
    {"agent": "e_alex", "source": "manual", "name": "team_meeting_jan2.txt"},
    {"agent": "e_alex", "source": "manual", "name": "mobile_app_overview.txt"},
    {"agent": "e_alex", "source": "manual", "name": "client_feedback.txt"},
]

e_alex_ids = ["sample_alex_1", "sample_alex_2", "sample_alex_3", "sample_alex_4"]

# Sample data for E. Lazar (SOPs, policies, onboarding)
e_lazar_docs = [
    "Onboarding Process: Day 1 - Complete HR paperwork, setup email and Slack account. Day 2 - Meet the team, review company policies. Day 3 - Begin training on internal tools and systems.",
    "Work from Home Policy: Employees can work remotely up to 3 days per week. Must maintain regular hours 9 AM - 5 PM. Weekly team meeting attendance is mandatory.",
    "Code Review SOP: All code must be reviewed by at least one senior developer before merging to main branch. Use pull requests, include tests, and update documentation.",
    "Time Off Policy: 15 days PTO per year, 10 sick days. Submit requests at least 2 weeks in advance. Manager approval required.",
]

e_lazar_metadata = [
    {"agent": "e_lazar", "source": "manual", "name": "onboarding_guide.txt"},
    {"agent": "e_lazar", "source": "manual", "name": "wfh_policy.txt"},
    {"agent": "e_lazar", "source": "manual", "name": "code_review_sop.txt"},
    {"agent": "e_lazar", "source": "manual", "name": "time_off_policy.txt"},
]

e_lazar_ids = ["sample_lazar_1", "sample_lazar_2", "sample_lazar_3", "sample_lazar_4"]

# Sample data for Client Success (client-specific)
client_success_docs = [
    "Client ACME Corp: Current project status - Phase 2 implementation in progress. Next milestone: January 15, 2026. Contact: Jane Doe (jane@acme.com)",
    "Client ACME Corp: Recent support tickets - Issue with login resolved on Jan 3. Performance optimization requested for dashboard.",
    "Client XYZ Inc: Onboarding completed December 2025. Training sessions scheduled for January 10-12. Primary contact: Bob Wilson.",
]

client_success_metadata = [
    {"agent": "client_success", "client_id": "ACME123", "source": "manual", "name": "acme_status.txt"},
    {"agent": "client_success", "client_id": "ACME123", "source": "manual", "name": "acme_support.txt"},
    {"agent": "client_success", "client_id": "XYZ456", "source": "manual", "name": "xyz_onboarding.txt"},
]

client_success_ids = ["sample_client_1", "sample_client_2", "sample_client_3"]

# Add all sample data
print("Adding sample data for E. Alex...")
db.add_documents(e_alex_docs, e_alex_metadata, e_alex_ids)

print("Adding sample data for E. Lazar...")
db.add_documents(e_lazar_docs, e_lazar_metadata, e_lazar_ids)

print("Adding sample data for Client Success...")
db.add_documents(client_success_docs, client_success_metadata, client_success_ids)

print("\n✅ Sample data added successfully!")
print("\nNow test in Slack:")
print("- E. Alex channel: @BotName what meetings did we have with clients?")
print("- E. Lazar channel: @BotName what is the onboarding process?")
print("- Client Success channel: @BotName client_id: ACME123 what's the project status?")
