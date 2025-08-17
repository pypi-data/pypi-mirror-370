"""Basic mathematical operations powered by AI."""

import logging
from typing import List, Union

from .base import BaseService

logger = logging.getLogger(__name__)

Number = Union[int, float]


class BasicService(BaseService):
    """
    Service for basic mathematical operations using AI processing.

    Provides AI-powered implementations of fundamental math operations
    while preserving number types and ensuring accurate results.
    """

    def max(self, items: List[Number]) -> Number:
        """
        Find the maximum value in a list using AI analysis.

        Args:
            items: List of numeric values

        Returns:
            Maximum value preserving original type

        Raises:
            ValidationError: If input list is empty
            ParseError: If AI response parsing fails
        """
        logger.debug(f"Finding max of {len(items)} items")

        system_prompt = (
            "Find the maximum (largest) value in the given list. "
            "IMPORTANT: Preserve the original number type exactly "
            "(integer→integer, float→float). "
            'Return JSON in format: {"response": max_value}'
        )
        user_prompt = f"Find the maximum value in this list, preserving number type: {items}"

        return self._request_json(user_prompt, system_prompt)

    def min(self, items: List[Number]) -> Number:
        """
        Find the minimum value in a list using AI analysis.

        Args:
            items: List of numeric values

        Returns:
            Minimum value preserving original type

        Raises:
            ValidationError: If input list is empty
            ParseError: If AI response parsing fails
        """
        logger.debug(f"Finding min of {len(items)} items")

        system_prompt = (
            "Find the minimum (smallest) value in the given list. "
            "IMPORTANT: Preserve the original number type exactly "
            "(integer→integer, float→float). "
            'Return JSON in format: {"response": min_value}'
        )
        user_prompt = f"Find the minimum value in this list, preserving number type: {items}"

        return self._request_json(user_prompt, system_prompt)

    def sum(self, items: List[Number]) -> Number:
        """
        Calculate the sum of all values using AI computation.

        Args:
            items: List of numeric values

        Returns:
            Sum with appropriate type (int if all ints, float otherwise)

        Raises:
            ParseError: If AI response parsing fails
        """
        logger.debug(f"Calculating sum of {len(items)} items")

        system_prompt = (
            "Calculate the sum (total) of all values in the given list. "
            "IMPORTANT: If all numbers are integers, return integer sum. "
            "If any are floats, return float sum. "
            'Return JSON in format: {"response": sum_value}'
        )
        user_prompt = f"Calculate the sum of all values, preserving appropriate number type: {items}"

        return self._request_json(user_prompt, system_prompt)

    def abs(self, number: Number) -> Number:
        """
        Get the absolute value using AI processing.

        Args:
            number: The number to process

        Returns:
            Absolute value preserving original type

        Raises:
            ParseError: If AI response parsing fails
        """
        logger.debug(f"Getting absolute value of {number}")

        system_prompt = (
            "Calculate the absolute value (remove negative sign if present) of the given number. "
            "IMPORTANT: Keep the exact same number type "
            "(integer input→integer output, float input→float output). "
            'Return JSON in format: {"response": absolute_value}'
        )
        user_prompt = f"What is the absolute value of {number}, keeping the same number type?"

        return self._request_json(user_prompt, system_prompt)
