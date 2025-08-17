"""Base service class for all VibeLib operations."""

import json
import logging
from abc import ABC
from typing import Any

from ..client import Client
from ..exceptions import ParseError

logger = logging.getLogger(__name__)


class BaseService(ABC):
    """
    Base class for all VibeLib operation services.

    Provides common functionality for making AI requests and parsing responses
    in a standardized format across all service implementations.
    """

    def __init__(self, client: Client) -> None:
        """
        Initialize the service with an API client.

        Args:
            client: Configured OpenAI client instance
        """
        self._client = client
        logger.debug(f"Initialized {self.__class__.__name__}")

    def _request_json(self, user_prompt: str, system_prompt: str) -> Any:
        """
        Make AI request and parse JSON response.

        Args:
            user_prompt: The user's request
            system_prompt: System instructions for the AI

        Returns:
            Parsed response data

        Raises:
            ParseError: If response parsing fails
        """
        logger.debug(f"Making JSON request for {self.__class__.__name__}")
        response = self._client.request(user_prompt, system_prompt)
        return self._parse_json_response(response)

    def _parse_json_response(self, response: str) -> Any:
        """
        Parse AI JSON response with comprehensive error handling.

        Args:
            response: Raw response string from AI

        Returns:
            The parsed response data

        Raises:
            ParseError: If JSON parsing or validation fails
        """
        try:
            # Clean up the response string
            cleaned_response = response.strip()

            # Handle potential markdown code blocks
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:-3].strip()
            elif cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:-3].strip()

            parsed = json.loads(cleaned_response)

            if not isinstance(parsed, dict):
                raise ValueError("Response must be a JSON object")

            if "response" not in parsed:
                raise ValueError("Response must contain 'response' field")

            result = parsed["response"]
            logger.debug(f"Successfully parsed JSON response: {type(result).__name__}")
            return result

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.error(f"JSON parsing failed: {e}. Raw response: {response[:200]}...")
            raise ParseError(
                f"Invalid JSON response: {e}. "
                f"Raw response (first 200 chars): {response[:200]}"
            ) from e
