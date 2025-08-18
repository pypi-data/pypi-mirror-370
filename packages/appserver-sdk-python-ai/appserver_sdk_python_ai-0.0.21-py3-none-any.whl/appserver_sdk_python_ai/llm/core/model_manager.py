"""
Gerenciador de modelos de tokenização.
Fornece interface unificada para diferentes tipos de tokenizadores.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from appserver_sdk_python_ai.llm.core.enums import (
    HuggingFaceModelEnum,
    OpenAIModelEnum,
    TokenizerTypeEnum,
)


@dataclass
class ModelInfo:
    """Informações sobre um modelo."""

    name: str
    type: TokenizerTypeEnum
    provider: str
    max_tokens: int
    description: str


class TokenizerModelManager:
    """Gerenciador de modelos de tokenização."""

    def __init__(self) -> None:
        """Inicializa o gerenciador."""
        self._models: dict[str, ModelInfo] = {}
        self._load_predefined_models()

    def _load_predefined_models(self) -> None:
        """Carrega modelos pré-definidos."""
        # Modelos OpenAI
        openai_model: OpenAIModelEnum
        for openai_model in OpenAIModelEnum:
            self._models[openai_model.value] = ModelInfo(
                name=openai_model.value,
                type=TokenizerTypeEnum.OPENAI,
                provider="OpenAI",
                max_tokens=4096,  # Valor padrão, pode ser ajustado por modelo
                description=f"Modelo OpenAI: {openai_model.value}",
            )

        # Modelos HuggingFace
        hf_model: HuggingFaceModelEnum
        for hf_model in HuggingFaceModelEnum:
            self._models[hf_model.value] = ModelInfo(
                name=hf_model.value,
                type=TokenizerTypeEnum.HUGGINGFACE,
                provider="HuggingFace",
                max_tokens=512,  # Valor padrão, pode ser ajustado por modelo
                description=f"Modelo HuggingFace: {hf_model.value}",
            )

    def count_tokens(self, text: str, model_name: str) -> dict[str, Any]:
        """Conta tokens usando fallback básico."""
        if not text:
            return {
                "token_count": 0,
                "model": model_name,
                "method": "fallback",
                "character_count": 0,
                "word_count": 0,
                "text_preview": "",
            }

        # Estimativa básica: ~4 caracteres por token
        token_count = max(1, len(text) // 4)

        return {
            "token_count": token_count,
            "model": model_name,
            "method": "fallback_estimation",
            "character_count": len(text),
            "word_count": len(text.split()),
            "text_preview": text[:50] + "..." if len(text) > 50 else text,
            "warning": "Usando implementação fallback. Instale tiktoken para funcionalidade completa.",
        }

    def register_custom_model(self, name: str, **kwargs) -> None:
        """Registra modelo customizado."""
        if name in self._models:
            raise ValueError(f"Modelo '{name}' já registrado")

        # Valores padrão para modelos customizados
        model_info = ModelInfo(
            name=name,
            type=kwargs.get("type", TokenizerTypeEnum.DEFAULT),
            provider=kwargs.get("provider", "Custom"),
            max_tokens=kwargs.get("max_tokens", 4096),
            description=kwargs.get("description", f"Modelo customizado: {name}"),
        )

        self._models[name] = model_info

    def list_models(self, tokenizer_type: TokenizerTypeEnum | None = None) -> list[str]:
        """Lista modelos disponíveis."""
        if tokenizer_type is None:
            return list(self._models.keys())

        return [
            name for name, info in self._models.items() if info.type == tokenizer_type
        ]

    def get_model_info(self, model_name: str) -> ModelInfo | None:
        """Obtém informações do modelo."""
        return self._models.get(model_name)

    def get_portuguese_models(self) -> list[str]:
        """Lista modelos para português."""
        return [model.value for model in HuggingFaceModelEnum.get_portuguese_models()]

    def get_multilingual_models(self) -> list[str]:
        """Lista modelos multilíngues."""
        multilingual_models = []

        # Adicionar modelos OpenAI (geralmente multilíngues)
        for model in OpenAIModelEnum:
            multilingual_models.append(model.value)

        # Adicionar modelos HuggingFace multilíngues específicos
        multilingual_huggingface = [
            "bert-base-multilingual-cased",
            "xlm-roberta-base",
            "distilbert-base-multilingual-cased",
        ]

        for model_name in multilingual_huggingface:
            if model_name in self._models:
                multilingual_models.append(model_name)

        return multilingual_models

    def is_model_available(self, model_name: str) -> bool:
        """Verifica se um modelo está disponível."""
        return model_name in self._models

    def is_model_registered(self, model_name: str) -> bool:
        """Verifica se modelo está registrado (alias para is_model_available)."""
        return self.is_model_available(model_name)

    def get_default_model(self) -> str:
        """Retorna o modelo padrão."""
        # Prioridade: GPT-3.5 > GPT-4 > primeiro disponível
        preferred_models = [
            "gpt-3.5-turbo",
            "gpt-4",
            "text-davinci-003",
        ]

        for model in preferred_models:
            if model in self._models:
                return model

        # Se nenhum modelo preferido estiver disponível, retorna o primeiro
        models = list(self._models.keys())
        if models:
            return models[0]

        # Fallback caso não haja modelos (não deveria acontecer)
        return "gpt-3.5-turbo"

    def get_model_max_tokens(self, model_name: str) -> int:
        """Obtém o número máximo de tokens para um modelo."""
        model_info = self.get_model_info(model_name)
        if model_info:
            return model_info.max_tokens

        # Fallback padrão
        return 4096

    def get_models_by_provider(self, provider: str) -> list[str]:
        """Lista modelos de um provider específico."""
        return [
            name
            for name, info in self._models.items()
            if info.provider.lower() == provider.lower()
        ]

    def get_supported_providers(self) -> list[str]:
        """Lista providers suportados."""
        return sorted({info.provider for info in self._models.values()})

    def __contains__(self, model_name: str) -> bool:
        """Verifica se modelo está registrado."""
        return model_name in self._models

    def __len__(self) -> int:
        """Retorna o número de modelos registrados."""
        return len(self._models)

    def __repr__(self) -> str:
        """Representação string do gerenciador."""
        return f"TokenizerModelManager(models={len(self._models)})"


# Instância global do gerenciador
model_manager = TokenizerModelManager()
