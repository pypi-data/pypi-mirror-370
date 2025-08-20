"""
AIgents Client Exceptions
========================

Custom exceptions for the AIgents Python client.
"""


class AIgentsError(Exception):
    """Base exception for all AIgents client errors."""
    pass


class APIError(AIgentsError):
    """Raised when the API returns an error response."""
    
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
    
    def __str__(self):
        if self.status_code:
            return f"API Error {self.status_code}: {self.message}"
        return f"API Error: {self.message}"


class AuthenticationError(AIgentsError):
    """Raised when authentication fails (invalid API key, etc.)."""
    pass


class ValidationError(AIgentsError):
    """Raised when request data is invalid."""
    pass


class ResourceNotFoundError(APIError):
    """Raised when a requested resource is not found."""
    pass


class InsufficientCreditsError(APIError):
    """Raised when user has insufficient credits for an operation."""
    pass