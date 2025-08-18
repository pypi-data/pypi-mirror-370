# appserver_sdk_python_ai/webscraping/exceptions/config.py
"""
Exceções de configuração para WebScraping
========================================

Define exceções relacionadas à configuração durante web scraping.
"""

from appserver_sdk_python_ai.webscraping.exceptions.base import WebScrapingError


class ScrapingConfigError(WebScrapingError):
    """Exceção para erros de configuração de scraping."""

    def __init__(
        self,
        message: str,
        config_key: str | None = None,
        config_section: str | None = None,
    ):
        self.config_key = config_key
        self.config_section = config_section
        if config_key and config_section:
            message = f"Erro de configuração na seção '{config_section}', chave '{config_key}': {message}"
        elif config_key:
            message = f"Erro de configuração na chave '{config_key}': {message}"
        super().__init__(message)
