# appserver_sdk_python_ai/llm/exceptions/base.py
"""
Exceção base para o módulo de LLM
===============================

Define a exceção base para todas as operações de LLM.
"""


class LLMError(Exception):
    """Exceção base para erros de LLM."""

    def __init__(
        self,
        message: str,
        model: str | None = None,
        provider: str | None = None,
        error_code: str | None = None,
    ):
        self.message = message
        self.model = model
        self.provider = provider
        self.error_code = error_code
        super().__init__(self.message)

    def __str__(self) -> str:
        parts = [self.message]
        if self.provider:
            parts.append(f"Provider: {self.provider}")
        if self.model:
            parts.append(f"Modelo: {self.model}")
        if self.error_code:
            parts.append(f"Código: {self.error_code}")
        return " | ".join(parts)
