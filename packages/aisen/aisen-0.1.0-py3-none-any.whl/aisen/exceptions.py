"""
Custom exceptions for the aisen SDK
"""


class AisenError(Exception):
    """Base exception for all aisen SDK errors."""
    pass


class APIError(AisenError):
    """Exception raised for API-related errors."""
    pass


class AuthenticationError(AisenError):
    """Exception raised for authentication failures."""
    pass