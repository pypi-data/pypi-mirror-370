"""OpenAI API client wrapper with enterprise-grade error handling."""

import logging
import time
from typing import Optional

from openai import OpenAI
from openai.types.chat import ChatCompletion

from .config import Config
from .exceptions import APIError, ConfigurationError

logger = logging.getLogger(__name__)


class Client:
    """
    OpenAI API client with retry logic and comprehensive error handling.

    Provides a robust interface to the OpenAI API with automatic retries,
    proper timeout handling, and detailed error reporting.
    """

    def __init__(self, config: Config) -> None:
        """
        Initialize the OpenAI client.

        Args:
            config: Configuration object with API settings

        Raises:
            ConfigurationError: If client initialization fails
        """
        try:
            self._client = OpenAI(api_key=config.resolved_api_key)
            self._config = config
            logger.debug(f"Initialized OpenAI client with model: {config.model}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise ConfigurationError(f"Client initialization failed: {e}") from e

    def request(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Make a chat completion request with retry logic.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt to set context

        Returns:
            The AI response content

        Raises:
            APIError: If all retry attempts fail
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        last_error: Optional[Exception] = None

        for attempt in range(self._config.max_retries):
            try:
                logger.debug(f"Making API request (attempt {attempt + 1}/{self._config.max_retries})")

                response: ChatCompletion = self._client.chat.completions.create(
                    model=self._config.model,
                    messages=messages,
                    temperature=self._config.temperature,
                    timeout=self._config.timeout
                )

                content = response.choices[0].message.content
                if not content or not content.strip():
                    raise APIError("Received empty response from API")

                logger.debug("API request successful")
                return content.strip()

            except Exception as e:
                last_error = e
                logger.warning(f"API request attempt {attempt + 1} failed: {e}")

                if attempt < self._config.max_retries - 1:
                    backoff_time = 2 ** attempt
                    logger.info(f"Retrying in {backoff_time} seconds...")
                    time.sleep(backoff_time)

        logger.error(f"All API request attempts failed. Last error: {last_error}")
        raise APIError(f"Request failed after {self._config.max_retries} attempts: {last_error}") from last_error
