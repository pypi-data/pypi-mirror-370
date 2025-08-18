"""
Lumera Agent SDK

This SDK provides helpers for agents running within the Lumera Notebook environment
to interact with the Lumera API and define dynamic user interfaces.
"""

# Import key functions from submodules to make them available at the top level.
from .sdk import get_access_token, get_google_access_token, save_to_lumera
from .ui import input

# Define what `from lumera import *` imports.
__all__ = [
    "get_access_token",
    "save_to_lumera",
    "get_google_access_token",  # Kept for backwards compatibility
    "input",
]
