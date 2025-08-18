# appserver_sdk_python_ai/webscraping/exceptions/base.py
"""
Exceção base para o módulo de WebScraping
=======================================

Define a exceção base para todas as operações de web scraping.
"""


class WebScrapingError(Exception):
    """Exceção base para erros de scraping."""

    def __init__(
        self,
        message: str,
        url: str | None = None,
        status_code: int | None = None,
        error_code: str | None = None,
    ):
        self.message = message
        self.url = url
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(message)

    def __str__(self) -> str:
        parts = [self.message]
        if self.url:
            parts.append(f"URL: {self.url}")
        if self.status_code:
            parts.append(f"Status: {self.status_code}")
        if self.error_code:
            parts.append(f"Código: {self.error_code}")
        return " | ".join(parts)
