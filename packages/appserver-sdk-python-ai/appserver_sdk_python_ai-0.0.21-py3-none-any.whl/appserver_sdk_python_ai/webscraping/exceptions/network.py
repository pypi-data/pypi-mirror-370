# appserver_sdk_python_ai/webscraping/exceptions/network.py
"""
Exceções relacionadas à rede para WebScraping
============================================

Define exceções específicas para operações de rede durante web scraping.
"""

from appserver_sdk_python_ai.webscraping.exceptions.base import WebScrapingError


class NetworkError(WebScrapingError):
    """Exceção para erros de rede."""

    def __init__(
        self,
        message: str,
        url: str | None = None,
        original_error: Exception | None = None,
    ):
        self.original_error = original_error
        super().__init__(message, url)


class TimeoutError(WebScrapingError):
    """Exceção para timeouts."""

    def __init__(
        self,
        url: str,
        timeout: int,
        message: str = "Timeout durante requisição",
    ):
        self.timeout = timeout
        super().__init__(message, url)


class AuthenticationError(WebScrapingError):
    """Exceção para erros de autenticação."""

    def __init__(
        self,
        url: str,
        message: str = "Erro de autenticação",
        auth_type: str | None = None,
    ):
        self.auth_type = auth_type
        super().__init__(message, url)


class RateLimitError(WebScrapingError):
    """Exceção para erros de rate limit."""

    def __init__(
        self,
        url: str,
        retry_after: int | None = None,
        message: str = "Limite de taxa excedido",
    ):
        self.retry_after = retry_after
        super().__init__(message, url, status_code=429)


class ProxyError(WebScrapingError):
    """Exceção para erros de proxy."""

    def __init__(
        self,
        message: str,
        proxy_url: str | None = None,
        url: str | None = None,
    ):
        self.proxy_url = proxy_url
        super().__init__(message, url)


class SSLVerificationError(WebScrapingError):
    """Exceção para erros de verificação SSL."""

    def __init__(
        self,
        url: str,
        message: str = "Erro de verificação SSL",
        certificate_info: dict | None = None,
    ):
        self.certificate_info = certificate_info
        super().__init__(message, url)
