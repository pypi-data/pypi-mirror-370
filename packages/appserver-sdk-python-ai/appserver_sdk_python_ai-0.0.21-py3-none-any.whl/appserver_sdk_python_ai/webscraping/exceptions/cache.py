# appserver_sdk_python_ai/webscraping/exceptions/cache.py
"""
Exceções de cache para WebScraping
=================================

Define exceções relacionadas ao sistema de cache durante web scraping.
"""

from appserver_sdk_python_ai.webscraping.exceptions.base import WebScrapingError


class CacheError(WebScrapingError):
    """Exceção para erros de cache."""

    def __init__(
        self,
        message: str,
        cache_key: str | None = None,
        operation: str | None = None,
    ):
        self.cache_key = cache_key
        self.operation = operation
        if cache_key and operation:
            message = f"Erro de cache na operação '{operation}' para chave '{cache_key}': {message}"
        super().__init__(message)
