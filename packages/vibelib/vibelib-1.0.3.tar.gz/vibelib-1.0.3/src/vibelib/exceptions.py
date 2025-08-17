"""Custom exceptions for VibeLib operations."""


class VibeLibError(Exception):
    """Base exception for all VibeLib operations."""
    pass


class ConfigurationError(VibeLibError):
    """Raised when there are configuration-related errors."""
    pass


class APIError(VibeLibError):
    """Raised when API communication fails."""
    pass


class ParseError(VibeLibError):
    """Raised when AI response parsing fails."""
    pass


class ValidationError(VibeLibError):
    """Raised when input validation fails."""
    pass
