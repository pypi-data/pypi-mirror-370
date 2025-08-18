# appserver_sdk_python_ai/llm/exceptions/provider.py
"""
Exceções relacionadas aos provedores de LLM
==========================================

Define exceções específicas para operações com provedores de LLM.
"""

from appserver_sdk_python_ai.llm.exceptions.base import LLMError


class LLMProviderError(LLMError):
    """Exceção lançada quando há erro específico do provedor de LLM."""

    def __init__(
        self,
        message: str,
        provider: str,
        model: str | None = None,
        original_error: Exception | None = None,
    ):
        self.original_error = original_error
        super().__init__(message, model, provider)


class LLMAuthenticationError(LLMError):
    """Exceção lançada quando há erro de autenticação com o provedor."""

    def __init__(self, message: str, provider: str):
        super().__init__(message, provider=provider)


class LLMRateLimitError(LLMError):
    """Exceção lançada quando o limite de taxa é excedido."""

    def __init__(
        self,
        message: str,
        retry_after: int | None = None,
        model: str | None = None,
        provider: str | None = None,
    ):
        self.retry_after = retry_after
        if retry_after:
            message = f"{message} | Retry after: {retry_after}"
        super().__init__(message, model, provider)


class LLMModelNotFoundError(LLMError):
    """Exceção lançada quando o modelo especificado não é encontrado."""

    def __init__(self, message: str, model_name: str, provider: str | None = None):
        self.model_name = model_name
        super().__init__(message, model_name, provider)


class LLMTokenLimitError(LLMError):
    """Exceção lançada quando o limite de tokens é excedido."""

    def __init__(
        self,
        model: str,
        token_count: int,
        max_tokens: int,
        provider: str | None = None,
    ):
        message = f"Limite de tokens excedido: {token_count}/{max_tokens}"
        self.token_count = token_count
        self.max_tokens = max_tokens
        super().__init__(message, model, provider)


class LLMTimeoutError(LLMError):
    """Exceção lançada quando a requisição para o LLM excede o timeout."""

    def __init__(
        self,
        message: str,
        timeout: float,
        model: str | None = None,
        provider: str | None = None,
    ):
        self.timeout = timeout
        message = f"{message} | Timeout: {timeout}s"
        super().__init__(message, model, provider)


class LLMNetworkError(LLMError):
    """Exceção lançada quando há erro de rede durante comunicação com o LLM."""

    def __init__(
        self,
        message: str,
        endpoint: str | None = None,
        model: str | None = None,
        provider: str | None = None,
    ):
        self.endpoint = endpoint
        if endpoint:
            message = f"Erro de rede ({endpoint}): {message}"
        else:
            message = f"Erro de rede: {message}"
        super().__init__(message, model, provider)
