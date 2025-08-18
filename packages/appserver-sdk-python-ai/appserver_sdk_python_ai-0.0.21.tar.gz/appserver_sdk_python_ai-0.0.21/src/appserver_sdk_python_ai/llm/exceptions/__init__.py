# appserver_sdk_python_ai/llm/exceptions/__init__.py
"""
Exceções específicas para o módulo de LLM
========================================

Este módulo define exceções customizadas para operações de LLM.
"""

from appserver_sdk_python_ai.llm.exceptions.base import LLMError
from appserver_sdk_python_ai.llm.exceptions.provider import (
    LLMAuthenticationError,
    LLMModelNotFoundError,
    LLMNetworkError,
    LLMProviderError,
    LLMRateLimitError,
    LLMTimeoutError,
    LLMTokenLimitError,
)
from appserver_sdk_python_ai.llm.exceptions.response import (
    LLMContentFilterError,
    LLMResponseError,
    LLMStreamingError,
)
from appserver_sdk_python_ai.llm.exceptions.validation import (
    LLMConfigurationError,
    LLMInvalidInputError,
    LLMValidationError,
)

__all__ = [
    "LLMError",
    "LLMProviderError",
    "LLMAuthenticationError",
    "LLMRateLimitError",
    "LLMModelNotFoundError",
    "LLMNetworkError",
    "LLMTokenLimitError",
    "LLMTimeoutError",
    "LLMResponseError",
    "LLMStreamingError",
    "LLMContentFilterError",
    "LLMValidationError",
    "LLMConfigurationError",
    "LLMInvalidInputError",
]
