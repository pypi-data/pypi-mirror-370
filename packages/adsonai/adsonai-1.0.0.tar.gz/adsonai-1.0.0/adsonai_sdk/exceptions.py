"""
Exception classes for AdsonAI SDK
"""

class AdsonAIError(Exception):
    """Base exception for AdsonAI SDK"""
    pass

class AuthenticationError(AdsonAIError):
    """Raised when API authentication fails"""
    pass

class APIError(AdsonAIError):
    """Raised when API returns an error"""
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code

class ValidationError(AdsonAIError):
    """Raised when request validation fails"""
    pass

class NetworkError(AdsonAIError):
    """Raised when network connection fails"""
    pass
