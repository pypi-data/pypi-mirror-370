# appserver_sdk_python_ai/webscraping/exceptions/content.py
"""
Exceções relacionadas ao conteúdo para WebScraping
=================================================

Define exceções específicas para processamento de conteúdo durante web scraping.
"""

from appserver_sdk_python_ai.webscraping.exceptions.base import WebScrapingError


class ContentTooLargeError(WebScrapingError):
    """Exceção quando o conteúdo é muito grande."""

    def __init__(
        self,
        message: str,
        size: int,
        max_size: int,
        url: str | None = None,
    ):
        self.size = size
        self.max_size = max_size
        super().__init__(f"{message}: {size}/{max_size} bytes", url)


class UnsupportedFormatError(WebScrapingError):
    """Exceção para formatos não suportados."""

    def __init__(
        self,
        message: str,
        format_type: str,
        url: str | None = None,
        supported_formats: list[str] | None = None,
    ):
        self.format = format_type
        self.supported_formats = supported_formats or []
        formatted_message = f"Formato '{format_type}' não suportado"
        if self.supported_formats:
            formatted_message += (
                f". Formatos suportados: {', '.join(self.supported_formats)}"
            )
        super().__init__(formatted_message, url)


class ConversionError(WebScrapingError):
    """Exceção para erros de conversão de conteúdo."""

    def __init__(
        self,
        message: str,
        from_format: str,
        to_format: str,
        url: str | None = None,
    ):
        self.from_format = from_format
        self.to_format = to_format
        formatted_message = (
            f"Erro convertendo de {from_format} para {to_format}: {message}"
        )
        super().__init__(formatted_message, url)


class JavaScriptError(WebScrapingError):
    """Exceção para erros relacionados ao JavaScript."""

    def __init__(
        self,
        message: str,
        script: str,
        url: str | None = None,
    ):
        self.script = script
        formatted_message = f"Erro de JavaScript: {message} - {script}"
        super().__init__(formatted_message, url)


class ParsingError(WebScrapingError):
    """Exceção para erros de parsing de conteúdo."""

    def __init__(
        self,
        message: str,
        parser_type: str | None = None,
        url: str | None = None,
    ):
        self.parser_type = parser_type
        if parser_type:
            message = f"Erro de parsing ({parser_type}): {message}"
        else:
            message = f"Erro de parsing: {message}"
        super().__init__(message, url)


class RobotsTxtError(WebScrapingError):
    """Exceção para violações do robots.txt."""

    def __init__(
        self,
        message: str,
        url: str | None = None,
        user_agent: str | None = None,
    ):
        self.user_agent = user_agent
        if user_agent:
            message = f"Bloqueado pelo robots.txt para '{user_agent}': {message}"
        else:
            message = f"Bloqueado pelo robots.txt: {message}"
        super().__init__(message, url)
