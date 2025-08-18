# appserver_sdk_python_ai/llm/exceptions/validation.py
"""
Exceções de validação e configuração para LLM
=============================================

Define exceções relacionadas à validação de dados e configuração.
"""

from appserver_sdk_python_ai.llm.exceptions.base import LLMError


class LLMValidationError(LLMError):
    """Exceção lançada quando há erro de validação nos dados de entrada."""

    def __init__(self, message: str, field: str | None = None):
        self.field = field
        if field:
            message = f"Erro de validação no campo '{field}': {message}"
        super().__init__(message)


class LLMConfigurationError(LLMError):
    """Exceção lançada quando há erro na configuração do LLM."""

    def __init__(self, message: str, config_key: str | None = None):
        self.config_key = config_key
        if config_key:
            message = f"Erro de configuração '{config_key}': {message}"
        super().__init__(message)


class LLMInvalidInputError(LLMError):
    """Exceção lançada quando há entrada inválida para o LLM."""

    def __init__(self, message: str, input_type: str | None = None):
        self.input_type = input_type
        if input_type:
            message = f"Entrada inválida '{input_type}': {message}"
        super().__init__(message)
