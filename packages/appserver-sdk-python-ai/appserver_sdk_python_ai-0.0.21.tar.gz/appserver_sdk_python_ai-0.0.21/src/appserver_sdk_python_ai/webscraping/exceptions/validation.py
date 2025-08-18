# appserver_sdk_python_ai/webscraping/exceptions/validation.py
"""
Exceções de validação para WebScraping
=====================================

Define exceções relacionadas à validação de dados durante web scraping.
"""

from appserver_sdk_python_ai.webscraping.exceptions.base import WebScrapingError


class ValidationError(WebScrapingError):
    """Exceção para erros de validação."""

    def __init__(
        self,
        message: str,
        field: str,
        value: str,
        url: str | None = None,
    ):
        self.field = field
        self.value = value
        formatted_message = f"Erro de validação no campo '{field}': {message}"
        super().__init__(formatted_message, url)
