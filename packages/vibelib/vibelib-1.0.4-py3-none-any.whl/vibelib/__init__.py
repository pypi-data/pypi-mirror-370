"""
VibeLib: AI-powered computational operations

Copyright (C) 2024 soradotwav

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import logging
import os
from typing import Any, List, Optional, Union

from .client import Client
from .config import Config
from .exceptions import APIError, ConfigurationError, ParseError, ValidationError, VibeLibError
from .operations import BasicService, ListService, SortingService, StringService

logger = logging.getLogger(__name__)

__version__ = "1.0.4"
__all__ = [
    # Core functions
    "sort", "max", "min", "sum", "abs",
    "upper", "lower", "split", "join", "strip", "replace",
    "count", "index", "reverse",
    # Classes
    "Config", "Client",
    # Exceptions
    "VibeLibError", "ConfigurationError", "APIError", "ParseError", "ValidationError"
]

# Service instances
_services: dict[str, Any] = {}
_current_api_key: Optional[str] = None


def _get_service(service_class: type, api_key: Optional[str] = None) -> Any:
    """Get or create a service instance with caching and key rotation support."""
    global _current_api_key, _services

    # Determine effective API key
    effective_key = api_key or os.getenv('OPENAI_API_KEY')

    # Reset all services if API key changed
    if _current_api_key != effective_key:
        logger.debug(f"API key changed, resetting services")
        _services.clear()
        _current_api_key = effective_key

    # Get or create service
    service_name = service_class.__name__.lower()
    if service_name not in _services:
        logger.debug(f"Creating new {service_class.__name__} instance")
        config = Config(api_key=api_key)
        client = Client(config)
        _services[service_name] = service_class(client)

    return _services[service_name]


# Sorting operations
def sort(items: Any, api_key: Optional[str] = None) -> List[Any]:
    """
    Sort input using AI-powered analysis.

    Args:
        items: The items to sort
        api_key: Optional OpenAI API key override

    Returns:
        Sorted list of items

    Raises:
        ValidationError: If input is invalid
        APIError: If API request fails
    """
    service = _get_service(SortingService, api_key)
    return service.sort(items)


# Basic mathematical operations
def max(items: List[Union[int, float]], api_key: Optional[str] = None) -> Union[int, float]:
    """
    Find the maximum value in a list using AI analysis.

    Args:
        items: List of numeric values
        api_key: Optional OpenAI API key override

    Returns:
        Maximum value preserving original type

    Raises:
        ValidationError: If input is invalid
        APIError: If API request fails
    """
    service = _get_service(BasicService, api_key)
    return service.max(items)


def min(items: List[Union[int, float]], api_key: Optional[str] = None) -> Union[int, float]:
    """
    Find the minimum value in a list using AI analysis.

    Args:
        items: List of numeric values
        api_key: Optional OpenAI API key override

    Returns:
        Minimum value preserving original type

    Raises:
        ValidationError: If input is invalid
        APIError: If API request fails
    """
    service = _get_service(BasicService, api_key)
    return service.min(items)


def sum(items: List[Union[int, float]], api_key: Optional[str] = None) -> Union[int, float]:
    """
    Sum all values in a list using AI calculation.

    Args:
        items: List of numeric values
        api_key: Optional OpenAI API key override

    Returns:
        Sum of all values with appropriate type

    Raises:
        ValidationError: If input is invalid
        APIError: If API request fails
    """
    service = _get_service(BasicService, api_key)
    return service.sum(items)


def abs(number: Union[int, float], api_key: Optional[str] = None) -> Union[int, float]:
    """
    Get the absolute value of a number using AI processing.

    Args:
        number: The number to process
        api_key: Optional OpenAI API key override

    Returns:
        Absolute value preserving original type

    Raises:
        ValidationError: If input is invalid
        APIError: If API request fails
    """
    service = _get_service(BasicService, api_key)
    return service.abs(number)


# String operations
def upper(string: str, api_key: Optional[str] = None) -> str:
    """
    Convert string to uppercase using AI text processing.

    Args:
        string: The string to convert
        api_key: Optional OpenAI API key override

    Returns:
        Uppercase version of the string

    Raises:
        ValidationError: If input is invalid
        APIError: If API request fails
    """
    service = _get_service(StringService, api_key)
    return service.upper(string)


def lower(string: str, api_key: Optional[str] = None) -> str:
    """
    Convert string to lowercase using AI text processing.

    Args:
        string: The string to convert
        api_key: Optional OpenAI API key override

    Returns:
        Lowercase version of the string

    Raises:
        ValidationError: If input is invalid
        APIError: If API request fails
    """
    service = _get_service(StringService, api_key)
    return service.lower(string)


def split(string: str, separator: str, api_key: Optional[str] = None) -> List[str]:
    """
    Split a string into a list using AI text analysis.

    Args:
        string: The string to split
        separator: The separator to split on
        api_key: Optional OpenAI API key override

    Returns:
        List of string parts

    Raises:
        ValidationError: If input is invalid
        APIError: If API request fails
    """
    service = _get_service(StringService, api_key)
    return service.split(string, separator)


def join(items: List[Union[int, float, str]], separator: str, api_key: Optional[str] = None) -> str:
    """
    Join list items into a string using AI processing.

    Args:
        items: The items to join
        separator: The separator to use
        api_key: Optional OpenAI API key override

    Returns:
        Joined string

    Raises:
        ValidationError: If input is invalid
        APIError: If API request fails
    """
    service = _get_service(StringService, api_key)
    return service.join(items, separator)


def strip(string: str, api_key: Optional[str] = None) -> str:
    """
    Remove whitespace from string ends using AI text processing.

    Args:
        string: The string to strip
        api_key: Optional OpenAI API key override

    Returns:
        String with whitespace removed from ends

    Raises:
        ValidationError: If input is invalid
        APIError: If API request fails
    """
    service = _get_service(StringService, api_key)
    return service.strip(string)


def replace(string: str, old: str, new: str, api_key: Optional[str] = None) -> str:
    """
    Replace substring occurrences using AI text processing.

    Args:
        string: The string to process
        old: The substring to replace
        new: The replacement substring
        api_key: Optional OpenAI API key override

    Returns:
        String with replacements made

    Raises:
        ValidationError: If input is invalid
        APIError: If API request fails
    """
    service = _get_service(StringService, api_key)
    return service.replace(string, old, new)


# List operations
def count(items: List[Any], value: Any, api_key: Optional[str] = None) -> int:
    """
    Count occurrences of a value in a list using AI analysis.

    Args:
        items: The list to search
        value: The value to count
        api_key: Optional OpenAI API key override

    Returns:
        Number of occurrences

    Raises:
        ValidationError: If input is invalid
        APIError: If API request fails
    """
    service = _get_service(ListService, api_key)
    return service.count(items, value)


def index(items: List[Any], value: Any, api_key: Optional[str] = None) -> int:
    """
    Find the index of first occurrence using AI analysis.

    Args:
        items: The list to search
        value: The value to find
        api_key: Optional OpenAI API key override

    Returns:
        Index of first occurrence

    Raises:
        ValidationError: If input is invalid
        APIError: If API request fails
    """
    service = _get_service(ListService, api_key)
    return service.index(items, value)


def reverse(items: List[Any], api_key: Optional[str] = None) -> List[Any]:
    """
    Reverse list order using AI processing.

    Args:
        items: The list to reverse
        api_key: Optional OpenAI API key override

    Returns:
        New list with elements in reverse order

    Raises:
        ValidationError: If input is invalid
        APIError: If API request fails
    """
    service = _get_service(ListService, api_key)
    return service.reverse(items)
