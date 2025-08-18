# appserver_sdk_python_ai/webscraping/exceptions/__init__.py
"""
Exceções específicas para o módulo de WebScraping
===============================================

Este módulo define exceções customizadas para operações de web scraping.
"""

from appserver_sdk_python_ai.webscraping.exceptions.base import WebScrapingError
from appserver_sdk_python_ai.webscraping.exceptions.cache import CacheError
from appserver_sdk_python_ai.webscraping.exceptions.config import ScrapingConfigError
from appserver_sdk_python_ai.webscraping.exceptions.content import (
    ContentTooLargeError,
    ConversionError,
    JavaScriptError,
    ParsingError,
    RobotsTxtError,
    UnsupportedFormatError,
)
from appserver_sdk_python_ai.webscraping.exceptions.network import (
    AuthenticationError,
    NetworkError,
    ProxyError,
    RateLimitError,
    SSLVerificationError,
    TimeoutError,
)
from appserver_sdk_python_ai.webscraping.exceptions.validation import ValidationError

__all__ = [
    "WebScrapingError",
    "NetworkError",
    "TimeoutError",
    "AuthenticationError",
    "RateLimitError",
    "ProxyError",
    "SSLVerificationError",
    "ContentTooLargeError",
    "UnsupportedFormatError",
    "ConversionError",
    "JavaScriptError",
    "ParsingError",
    "RobotsTxtError",
    "ValidationError",
    "CacheError",
    "ScrapingConfigError",
]
