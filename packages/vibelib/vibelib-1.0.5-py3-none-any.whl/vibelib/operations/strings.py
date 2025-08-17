"""String manipulation operations powered by AI."""

import logging
from typing import List, Union

from .base import BaseService

logger = logging.getLogger(__name__)


class StringService(BaseService):
    """
    Service for string manipulation operations using AI processing.

    Provides AI-powered implementations of common string operations
    with enhanced natural language understanding capabilities.
    """

    def upper(self, string: str) -> str:
        """
        Convert string to uppercase using AI text processing.

        Args:
            string: The string to convert

        Returns:
            Uppercase version of the string

        Raises:
            ParseError: If AI response parsing fails
        """
        logger.debug(f"Converting string to uppercase (length: {len(string)})")

        system_prompt = (
            "Convert the given string to fully uppercase format. "
            'Return JSON in format: {"response": "UPPER_STRING"}'
        )
        user_prompt = f"Convert this string to uppercase: {string}"

        return self._request_json(user_prompt, system_prompt)

    def lower(self, string: str) -> str:
        """
        Convert string to lowercase using AI text processing.

        Args:
            string: The string to convert

        Returns:
            Lowercase version of the string

        Raises:
            ParseError: If AI response parsing fails
        """
        logger.debug(f"Converting string to lowercase (length: {len(string)})")

        system_prompt = (
            "Convert the given string to fully lowercase format. "
            'Return JSON in format: {"response": "lower_string"}'
        )
        user_prompt = f"Convert this string to lowercase: {string}"

        return self._request_json(user_prompt, system_prompt)

    def split(self, string: str, separator: str) -> List[str]:
        """
        Split string into list using AI text analysis.

        Args:
            string: The string to split
            separator: The separator to split on

        Returns:
            List of string parts

        Raises:
            ParseError: If AI response parsing fails
        """
        logger.debug(f"Splitting string (length: {len(string)}) on separator: '{separator}'")

        system_prompt = (
            "Split the given string at every occurrence of the specified separator "
            "into an array of strings. "
            'Return JSON in format: {"response": ["part1", "part2", "part3"]}'
        )
        user_prompt = f"Split this string '{string}' at separator '{separator}'"

        return self._request_json(user_prompt, system_prompt)

    def join(self, items: List[Union[str, int, float]], separator: str) -> str:
        """
        Join list items into string using AI processing.

        Args:
            items: The items to join
            separator: The separator to use between items

        Returns:
            Joined string

        Raises:
            ParseError: If AI response parsing fails
        """
        logger.debug(f"Joining {len(items)} items with separator: '{separator}'")

        system_prompt = (
            "Join all elements of the given list into a single string "
            "using the specified separator between each element. "
            "Convert non-string elements to strings first. "
            'Return JSON in format: {"response": "joined_string"}'
        )
        user_prompt = f"Join this list {items} using separator '{separator}'"

        return self._request_json(user_prompt, system_prompt)

    def strip(self, string: str) -> str:
        """
        Remove whitespace from string ends using AI text processing.

        Args:
            string: The string to strip

        Returns:
            String with leading and trailing whitespace removed

        Raises:
            ParseError: If AI response parsing fails
        """
        logger.debug(f"Stripping whitespace from string (length: {len(string)})")

        system_prompt = (
            "Remove all whitespace characters (spaces, tabs, newlines) "
            "from the beginning and end of the given string. "
            "Leave whitespace in the middle untouched. "
            'Return JSON in format: {"response": "stripped_string"}'
        )
        user_prompt = f"Strip whitespace from the beginning and end of this string: '{string}'"

        return self._request_json(user_prompt, system_prompt)

    def replace(self, string: str, old: str, new: str) -> str:
        """
        Replace substring occurrences using AI text processing.

        Args:
            string: The string to process
            old: The substring to replace
            new: The replacement substring

        Returns:
            String with all occurrences replaced

        Raises:
            ParseError: If AI response parsing fails
        """
        logger.debug(f"Replacing '{old}' with '{new}' in string (length: {len(string)})")

        system_prompt = (
            "In the given string, replace ALL occurrences of the old substring "
            "with the new substring. Be thorough and replace every instance. "
            'Return JSON in format: {"response": "modified_string"}'
        )
        user_prompt = f"In string '{string}', replace all '{old}' with '{new}'"

        return self._request_json(user_prompt, system_prompt)
