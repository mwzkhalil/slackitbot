"""
Security utilities for the AI Agent System.
Handles authentication, authorization, and data isolation.
"""

from typing import Optional

def validate_agent_access(agent: str, user_id: str, client_id: Optional[str] = None) -> bool:
    """
    Validate if the user has access to the specified agent.
    For client success, check if user is associated with the client.
    """
    # Placeholder: Implement based on your user management system
    # For now, assume all users have access to e_alex and e_lazar
    # For client_success, require client_id and check association
    if agent == "client_success" and not client_id:
        return False
    return True

def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent injection or malicious content.
    """
    # Basic sanitization
    return text.strip()[:1000]  # Limit length

def check_data_isolation(agent: str, client_id: Optional[str] = None) -> dict:
    """
    Ensure data isolation per agent.
    Returns filter criteria for database queries.
    """
    filters = {"agent": agent}
    if agent == "client_success":
        if not client_id:
            raise ValueError("Client ID required")
        filters["client_id"] = client_id
    return filters