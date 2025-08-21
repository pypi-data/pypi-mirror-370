"""
Custom exceptions for pywabot.
"""


class PywabotError(Exception):
    """Base exception for all pywabot errors."""


class APIError(PywabotError):
    """Raised when the API returns an error."""

    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class AuthenticationError(PywabotError):
    """Raised when there is an authentication error."""

    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class APIKeyMissingError(PywabotError):
    """Raised when the API key is missing."""


class PyWaBotConnectionError(PywabotError):
    """Raised when there is a connection error."""


class LIDDetectionError(PywabotError):
    """Raised when the bot's LID detection fails."""
