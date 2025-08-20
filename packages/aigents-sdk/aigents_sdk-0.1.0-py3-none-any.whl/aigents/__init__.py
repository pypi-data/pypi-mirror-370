"""
AIgents Python Client
====================

A simple and elegant Python client for the AIgents platform.

Usage:
    from aigents import AIgentsClient
    
    client = AIgentsClient(api_key="your-api-key")
    
    # List applications
    apps = client.applications.list()
    
    # Start a chat
    chat = client.chat.create(application_id="app-id", agent_id="agent-id")
    response = chat.send("Hello!")
"""

from .client import AIgentsClient

__version__ = "0.1.0"
__all__ = ["AIgentsClient"]