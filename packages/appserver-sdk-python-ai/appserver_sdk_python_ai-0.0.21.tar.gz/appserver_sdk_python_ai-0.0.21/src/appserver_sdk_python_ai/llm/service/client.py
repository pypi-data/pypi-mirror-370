# appserver_sdk_python_ai/llm/service/client.py
"""
Cliente de serviço para LLM
==========================

Define cliente base para comunicação com provedores de LLM.
"""

import time
from abc import ABC, abstractmethod
from typing import Any

from appserver_sdk_python_ai.llm.core.config import LLMConfig
from appserver_sdk_python_ai.llm.core.metrics import (
    OperationStatus,
    get_metrics_collector,
    record_operation_metric,
)
from appserver_sdk_python_ai.llm.exceptions import (
    LLMAuthenticationError,
    LLMProviderError,
)


class LLMClient(ABC):
    """Cliente base abstrato para provedores de LLM."""

    def __init__(self, config: LLMConfig | None = None):
        """Inicializa o cliente com configuração."""
        self.config = config or LLMConfig()
        self._authenticated = False
        self._metrics_collector = get_metrics_collector()

    @abstractmethod
    def authenticate(self, **kwargs) -> bool:
        """Autentica com o provedor."""
        pass

    @abstractmethod
    def generate_text(self, prompt: str, model: str, **kwargs) -> dict[str, Any]:
        """Gera texto usando o modelo especificado."""
        pass

    def _record_operation_metrics(
        self,
        operation_type: str,
        start_time: float,
        success: bool = True,
        model: str | None = None,
        token_count: int | None = None,
        error: str | None = None,
    ) -> None:
        """Registra métricas de operação."""
        duration_ms = (time.time() - start_time) * 1000
        status = OperationStatus.SUCCESS if success else OperationStatus.ERROR

        record_operation_metric(
            operation_type=operation_type,
            duration_ms=duration_ms,
            status=status,
            model_name=model,
            token_count=token_count,
            error_message=error,
        )

    @abstractmethod
    def list_models(self) -> list[str]:
        """Lista modelos disponíveis."""
        pass

    @abstractmethod
    def get_model_info(self, model: str) -> dict[str, Any]:
        """Obtém informações sobre um modelo."""
        pass

    def is_authenticated(self) -> bool:
        """Verifica se o cliente está autenticado."""
        return self._authenticated

    def health_check(self) -> dict[str, Any]:
        """Verifica a saúde da conexão com o provedor."""
        try:
            models = self.list_models()
            return {
                "status": "healthy",
                "authenticated": self.is_authenticated(),
                "models_available": len(models) > 0,
                "model_count": len(models),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "authenticated": self.is_authenticated(),
            }


class MockLLMClient(LLMClient):
    """Cliente mock para testes."""

    def __init__(self, config: LLMConfig | None = None):
        super().__init__(config)
        self._models = ["mock-model-1", "mock-model-2"]

    def authenticate(self, **kwargs) -> bool:
        """Mock de autenticação."""
        self._authenticated = True
        return True

    def generate_text(self, prompt: str, model: str, **kwargs) -> dict[str, Any]:
        """Mock de geração de texto."""
        start_time = time.time()

        try:
            if not self._authenticated:
                raise LLMAuthenticationError("Cliente não autenticado", "mock")

            if model not in self._models:
                raise LLMProviderError(f"Modelo {model} não encontrado", "mock")

            result = {
                "text": f"Resposta mock para: {prompt}",
                "model": model,
                "tokens_used": len(prompt.split()) + 10,
                "provider": "mock",
            }

            # Registrar métricas de sucesso
            self._record_operation_metrics(
                operation_type="generate_text",
                start_time=start_time,
                success=True,
                model=model,
                token_count=int(result["tokens_used"])
                if result.get("tokens_used") is not None
                and isinstance(result["tokens_used"], int | float | str)
                else None,
            )

            return result

        except Exception as e:
            # Registrar métricas de erro
            self._record_operation_metrics(
                operation_type="generate_text",
                start_time=start_time,
                success=False,
                model=model,
                error=str(e),
            )
            raise

    def list_models(self) -> list[str]:
        """Lista modelos mock."""
        start_time = time.time()

        try:
            models = self._models.copy()

            # Registrar métricas de sucesso
            self._record_operation_metrics(
                operation_type="list_models", start_time=start_time, success=True
            )

            return models

        except Exception as e:
            # Registrar métricas de erro
            self._record_operation_metrics(
                operation_type="list_models",
                start_time=start_time,
                success=False,
                error=str(e),
            )
            raise

    def get_model_info(self, model: str) -> dict[str, Any]:
        """Informações mock do modelo."""
        start_time = time.time()

        try:
            if model not in self._models:
                raise LLMProviderError(f"Modelo {model} não encontrado", "mock")

            info = {
                "name": model,
                "provider": "mock",
                "max_tokens": 4096,
                "supports_streaming": True,
            }

            # Registrar métricas de sucesso
            self._record_operation_metrics(
                operation_type="get_model_info",
                start_time=start_time,
                success=True,
                model=model,
            )

            return info

        except Exception as e:
            # Registrar métricas de erro
            self._record_operation_metrics(
                operation_type="get_model_info",
                start_time=start_time,
                success=False,
                model=model,
                error=str(e),
            )
            raise
