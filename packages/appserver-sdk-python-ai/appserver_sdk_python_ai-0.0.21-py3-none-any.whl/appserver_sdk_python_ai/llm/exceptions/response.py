# appserver_sdk_python_ai/llm/exceptions/response.py
"""
Exceções relacionadas às respostas de LLM
========================================

Define exceções específicas para processamento de respostas de LLM.
"""

from appserver_sdk_python_ai.llm.exceptions.base import LLMError


class LLMResponseError(LLMError):
    """Exceção lançada quando há erro na resposta do LLM."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_data: dict | None = None,
        model: str | None = None,
        provider: str | None = None,
    ):
        self.response_data = response_data
        self.status_code = status_code
        super().__init__(message, model, provider)

    def __str__(self) -> str:
        parts = [self.message]
        if self.provider:
            parts.append(f"Provider: {self.provider}")
        if self.model:
            parts.append(f"Modelo: {self.model}")
        if self.status_code:
            parts.append(f"Status: {self.status_code}")
        return " | ".join(parts)


class LLMStreamingError(LLMError):
    """Exceção lançada quando há erro durante streaming de resposta."""

    def __init__(
        self,
        message: str,
        model: str | None = None,
        provider: str | None = None,
        chunk_index: int | None = None,
    ):
        self.chunk_index = chunk_index
        super().__init__(message, model, provider)


class LLMContentFilterError(LLMError):
    """Exceção lançada quando o conteúdo é filtrado pelo provedor."""

    def __init__(
        self,
        message: str = "Conteúdo filtrado pelo provedor",
        filter_reason: str | None = None,
        model: str | None = None,
        provider: str | None = None,
    ):
        self.filter_reason = filter_reason
        super().__init__(message, model, provider)
