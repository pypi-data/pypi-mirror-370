"""Exceções base comuns para todos os módulos do SDK."""

from typing import Any


class SDKError(Exception):
    """Exceção base para todos os erros do SDK."""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message

    def to_dict(self) -> dict[str, Any]:
        """Converte a exceção para dicionário."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
        }


class ConfigurationError(SDKError):
    """Erro de configuração."""

    pass


class ValidationError(SDKError):
    """Erro de validação de dados."""

    pass


class NetworkError(SDKError):
    """Erro de rede."""

    pass


class TimeoutError(SDKError):
    """Erro de timeout."""

    pass


class AuthenticationError(SDKError):
    """Erro de autenticação."""

    pass


class RateLimitError(SDKError):
    """Erro de limite de taxa."""

    pass


class SharedError(SDKError):
    """Erro base do módulo shared."""

    pass


class LoggingError(SDKError):
    """Erro relacionado ao sistema de logging."""

    pass


class UtilityError(SDKError):
    """Erro relacionado aos utilitários."""

    pass
