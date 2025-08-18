"""
AdsonAI Python SDK - Phase 3
Simple SDK for contextual ad matching with AI
"""

__version__ = "1.0.0"
__author__ = "AdsonAI Team"
__email__ = "developers@adsonai.com"

# Import main classes and functions
from .client import AdsonAI
from .models import Ad
from .exceptions import AdsonAIError, AuthenticationError, APIError, ValidationError

# Convenience function
def get_ads(api_key: str, query: str, max_ads: int = 3):
    """
    Quick function to get ads without creating a persistent client
    
    Args:
        api_key: Your AdsonAI API key
        query: Search query
        max_ads: Maximum ads to return
        
    Returns:
        List of Ad objects
    """
    with AdsonAI(api_key=api_key) as client:
        return client.get_contextual_ads(query, max_ads)

# Public API
__all__ = [
    "AdsonAI",
    "Ad", 
    "get_ads",
    "AdsonAIError",
    "AuthenticationError", 
    "APIError",
    "ValidationError"
]
