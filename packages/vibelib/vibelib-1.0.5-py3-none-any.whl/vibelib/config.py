"""Configuration management for VibeLib operations."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Config:
    """
    Configuration for VibeLib operations.

    Attributes:
        api_key: OpenAI API key (falls back to OPENAI_API_KEY env var)
        model: OpenAI model to use
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
        temperature: AI response temperature (0.0-1.0)
    """
    api_key: Optional[str] = None
    model: str = "gpt-4o-mini"
    timeout: float = 30.0
    max_retries: int = 3
    temperature: float = 0.3

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        resolved = self.resolved_api_key
        if not resolved or not resolved.strip():
            raise ValueError(
                "API key required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )

        if self.temperature < 0.0 or self.temperature > 1.0:
            raise ValueError("Temperature must be between 0.0 and 1.0")

        if self.max_retries < 1:
            raise ValueError("max_retries must be at least 1")

        if self.timeout <= 0:
            raise ValueError("timeout must be positive")

    @property
    def resolved_api_key(self) -> str:
        """Get the API key, preferring direct value over environment variable."""
        return self.api_key or os.getenv('OPENAI_API_KEY', '')

    def __repr__(self) -> str:
        """Custom repr that hides the API key for security."""
        api_key_display = "***" if self.resolved_api_key else None
        return (
            f"Config("
            f"api_key={api_key_display}, "
            f"model='{self.model}', "
            f"timeout={self.timeout}, "
            f"max_retries={self.max_retries}, "
            f"temperature={self.temperature}"
            f")"
        )
