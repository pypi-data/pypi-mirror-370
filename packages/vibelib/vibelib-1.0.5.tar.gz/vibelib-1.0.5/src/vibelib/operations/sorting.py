"""AI-powered sorting operations with creative interpretation."""

import logging
from typing import Any, List

from .base import BaseService
from ..exceptions import ValidationError

logger = logging.getLogger(__name__)


class SortingService(BaseService):
    """
    AI-powered sorting service with intelligent and creative sorting algorithms.

    Provides sorting capabilities that go beyond traditional algorithms,
    using AI to interpret and sort data in contextually appropriate ways.
    """

    def sort(self, items: Any) -> List[Any]:
        """
        Sort input using AI-powered analysis and creative interpretation.

        Args:
            items: The items to sort (can be various types)

        Returns:
            Sorted list with preserved data types

        Raises:
            ValidationError: If input is invalid or too large
            ParseError: If AI response parsing fails
        """
        logger.debug(f"Sorting items: {type(items).__name__}")

        # Handle edge cases
        if not items:
            logger.debug("Empty input, returning empty list")
            return []

        if hasattr(items, '__len__') and len(items) == 1:
            logger.debug("Single item input, returning as list")
            return list(items)

        if hasattr(items, '__len__') and len(items) > 10000:
            logger.error(f"Input too large: {len(items)} items")
            raise ValidationError(
                f"Input too large ({len(items)} items). Maximum allowed: 10,000 items."
            )

        system_prompt = (
            "You are an advanced sorting service. Sort the given input in the most "
            "appropriate and intelligent way possible. Consider the data types, "
            "patterns, and context to determine the best sorting approach. "
            "Be creative but logical in your interpretation of 'sorting'. "
            "IMPORTANT: Preserve all original data types exactly "
            "(numbers stay numbers, strings stay strings, etc.). "
            'Always return JSON in format: {"response": [your_sorted_result]}'
        )
        user_prompt = f"Intelligently sort this data: {items}"

        result = self._request_json(user_prompt, system_prompt)
        logger.debug(f"Successfully sorted {len(items)} items")
        return result
