"""List manipulation operations powered by AI."""

import logging
from typing import Any, List

from .base import BaseService

logger = logging.getLogger(__name__)


class ListService(BaseService):
    """
    Service for list manipulation operations using AI processing.

    Provides AI-powered implementations of common list operations
    with intelligent handling of different data types.
    """

    def count(self, items: List[Any], value: Any) -> int:
        """
        Count occurrences of a value using AI analysis.

        Args:
            items: The list to search
            value: The value to count

        Returns:
            Number of times the value appears

        Raises:
            ParseError: If AI response parsing fails
        """
        logger.debug(f"Counting occurrences of {value} in list of {len(items)} items")

        system_prompt = (
            "Count how many times the specified value appears in the given list. "
            "Count ALL exact matches of the value. Use precise equality comparison. "
            'Return JSON in format: {"response": count_number}'
        )
        user_prompt = f"Count occurrences of {value} in list: {items}"

        return self._request_json(user_prompt, system_prompt)

    def index(self, items: List[Any], value: Any) -> int:
        """
        Find index of first occurrence using AI analysis.

        Args:
            items: The list to search
            value: The value to find

        Returns:
            Zero-based index of first occurrence

        Raises:
            ParseError: If AI response parsing fails
        """
        logger.debug(f"Finding index of {value} in list of {len(items)} items")

        system_prompt = (
            "Find the index (position) of the first occurrence of the specified value "
            "in the list. Index counting starts at 0. "
            "Return the position number where the value is first found. "
            'Return JSON in format: {"response": index_number}'
        )
        user_prompt = f"Find the index of value {value} in list: {items}"

        return self._request_json(user_prompt, system_prompt)

    def reverse(self, items: List[Any]) -> List[Any]:
        """
        Reverse list order using AI processing.

        Args:
            items: The list to reverse

        Returns:
            New list with elements in reverse order

        Raises:
            ParseError: If AI response parsing fails
        """
        logger.debug(f"Reversing list of {len(items)} items")

        system_prompt = (
            "Create a new list with all elements from the given list "
            "in reverse order. The last element becomes first, "
            "second-to-last becomes second, etc. "
            "IMPORTANT: Preserve all original data types exactly "
            "(numbers stay numbers, strings stay strings). "
            'Return JSON in format: {"response": [reversed_list]}'
        )
        user_prompt = f"Reverse the order of elements in list: {items}"

        return self._request_json(user_prompt, system_prompt)
