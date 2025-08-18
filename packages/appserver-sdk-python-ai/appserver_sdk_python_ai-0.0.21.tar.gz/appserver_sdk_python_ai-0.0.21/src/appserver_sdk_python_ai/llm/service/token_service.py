"""Serviço de contagem de tokens para modelos LLM.

Este módulo fornece funcionalidades para contar tokens em textos,
utilizando diferentes tokenizadores baseado no modelo especificado.
Inclui cache, validação e logging estruturado.
"""

from __future__ import annotations

import time
from typing import Any

try:
    # Usar importações absolutas
    from appserver_sdk_python_ai.llm.core.cache import cache_result
    from appserver_sdk_python_ai.llm.core.enums import (
        HuggingFaceModelEnum,
        OpenAIModelEnum,
        TokenizerTypeEnum,
    )
    from appserver_sdk_python_ai.llm.core.logging_config import (
        OperationType,
        get_logger,
        log_function_call,
    )
    from appserver_sdk_python_ai.llm.core.model_manager import TokenizerModelManager
    from appserver_sdk_python_ai.llm.core.validation import (
        ValidationLevel,
        validate_text,
        validate_token_count,
    )
except ImportError:
    # Fallback para importações absolutas se necessário
    from appserver_sdk_python_ai.llm.core.cache import cache_result
    from appserver_sdk_python_ai.llm.core.enums import (
        HuggingFaceModelEnum,
        OpenAIModelEnum,
        TokenizerTypeEnum,
    )
    from appserver_sdk_python_ai.llm.core.logging_config import (
        OperationType,
        get_logger,
        log_function_call,
    )
    from appserver_sdk_python_ai.llm.core.model_manager import TokenizerModelManager
    from appserver_sdk_python_ai.llm.core.validation import (
        ValidationLevel,
        validate_text,
        validate_token_count,
    )

# Instância global do gerenciador
_model_manager: TokenizerModelManager | None = None


def _get_model_manager() -> TokenizerModelManager:
    """Obtém instância do model manager (lazy loading)."""
    global _model_manager
    if _model_manager is None:
        _model_manager = TokenizerModelManager()
    return _model_manager


@cache_result(key_prefix="token_count", ttl=1800.0)  # Cache por 30 minutos
@log_function_call(OperationType.TOKEN_COUNT, log_args=True, log_result=True)
def get_token_count(text: str, model: str | None = None) -> int:
    """Conta o número de tokens em um texto.

    Args:
        text: O texto para contar tokens
        model: Nome do modelo (opcional, usa padrão se não especificado)

    Returns:
        Número de tokens no texto

    Example:
        >>> count = get_token_count("Hello world")
        >>> print(f"Tokens: {count}")
    """
    logger = get_logger()

    # Validar entrada
    text_validation = validate_text(text, ValidationLevel.MODERATE)
    if not text_validation.is_valid:
        logger.error(f"Texto inválido: {text_validation.errors}")
        raise ValueError(f"Texto inválido: {'; '.join(text_validation.errors)}")

    if text_validation.warnings:
        logger.warning(f"Avisos no texto: {'; '.join(text_validation.warnings)}")

    start_time = time.time()

    with logger.operation_context(OperationType.TOKEN_COUNT, "count_tokens") as ctx:
        ctx.metadata.update(
            {
                "text_length": len(text),
                "model": model or "default",
                "text_preview": text[:100] + "..." if len(text) > 100 else text,
            }
        )

        try:
            manager = _get_model_manager()
            if model:
                result = manager.count_tokens(text, model)
            else:
                # Usa modelo padrão (GPT-4)
                default_model = OpenAIModelEnum.GPT_4.value
                result = manager.count_tokens(text, default_model)
                ctx.metadata["model"] = default_model

            token_count = result["token_count"]
            token_count = (
                int(token_count)
                if isinstance(token_count, int | float)
                else max(1, len(text) // 4)
            )

            # Validar resultado
            count_validation = validate_token_count(
                token_count, {"text": text, "max_tokens": 200000}
            )
            if not count_validation.is_valid:
                logger.warning(
                    f"Contagem de tokens suspeita: {count_validation.warnings}"
                )

            duration_ms = (time.time() - start_time) * 1000
            logger.log_performance(
                "token_count",
                duration_ms,
                {
                    "token_count": token_count,
                    "text_length": len(text),
                    "tokens_per_ms": token_count / duration_ms
                    if duration_ms > 0
                    else 0,
                },
            )

            return token_count

        except Exception as e:
            logger.error(f"Erro ao contar tokens: {e}")
            # Fallback simples se tiktoken não estiver disponível
            fallback_count = max(1, len(text) // 4)
            logger.warning(f"Usando contagem fallback: {fallback_count} tokens")
            return fallback_count


@cache_result(key_prefix="token_count_detailed", ttl=1800.0)  # Cache por 30 minutos
@log_function_call(OperationType.TOKEN_COUNT, log_args=True, log_result=True)
def get_token_count_with_model(
    text: str,
    model: str | OpenAIModelEnum | HuggingFaceModelEnum,
    max_tokens: int | None = None,
) -> dict[str, Any]:
    """Conta tokens com modelo específico.

    Args:
        text: Texto para análise.
        model: Modelo de tokenização.
        max_tokens: Limite máximo de tokens.

    Returns:
        Dicionário com resultado detalhado incluindo:
        - token_count: número de tokens
        - character_count: número de caracteres
        - word_count: número de palavras
        - model: modelo usado
        - validation_status: status da validação
        - performance_metrics: métricas de performance

    Raises:
        ValueError: Se texto for None.
    """
    logger = get_logger()

    # Validar entradas
    text_validation = validate_text(text, ValidationLevel.MODERATE)
    if not text_validation.is_valid:
        logger.error(f"Texto inválido: {text_validation.errors}")
        raise ValueError(f"Texto inválido: {'; '.join(text_validation.errors)}")

    if text_validation.warnings:
        logger.warning(f"Avisos no texto: {'; '.join(text_validation.warnings)}")

    # Converte enum para string
    model_name = model.value if hasattr(model, "value") else str(model)

    start_time = time.time()

    with logger.operation_context(
        OperationType.TOKEN_COUNT, "count_tokens_detailed"
    ) as ctx:
        ctx.metadata.update(
            {
                "text_length": len(text),
                "model": model_name,
                "text_preview": text[:100] + "..." if len(text) > 100 else text,
            }
        )

        try:
            manager = _get_model_manager()
            result = manager.count_tokens(text, model_name)

            token_count = result.get("token_count", max(1, len(text) // 4))
            character_count = len(text)
            word_count = len(text.split()) if text.strip() else 0

            # Validar contagem de tokens
            count_validation = validate_token_count(
                token_count, {"text": text, "max_tokens": 200000, "model": model_name}
            )

            duration_ms = (time.time() - start_time) * 1000

            # Log de performance
            logger.log_performance(
                "token_count_detailed",
                duration_ms,
                {
                    "token_count": token_count,
                    "character_count": character_count,
                    "word_count": word_count,
                    "tokens_per_char": token_count / character_count
                    if character_count > 0
                    else 0,
                },
            )

            # Preparar resultado base
            enhanced_result = {
                "token_count": token_count,
                "character_count": character_count,
                "word_count": word_count,
                "model": model_name,
                "method": result.get("method", "standard"),
                "type": result.get("type", "standard"),
                "text_preview": text[:100] + "..." if len(text) > 100 else text,
                "validation_status": {
                    "text_valid": text_validation.is_valid,
                    "count_valid": count_validation.is_valid,
                    "warnings": text_validation.warnings + count_validation.warnings,
                },
                "performance_metrics": {
                    "duration_ms": duration_ms,
                    "tokens_per_second": (token_count / (duration_ms / 1000))
                    if duration_ms > 0
                    else 0,
                    "processing_efficiency": "high"
                    if duration_ms < 100
                    else "medium"
                    if duration_ms < 500
                    else "low",
                },
            }

        except Exception as e:
            logger.error(f"Erro ao usar modelo '{model_name}': {e}")

            # Fallback em caso de erro
            token_count = max(1, len(text) // 4)
            duration_ms = (time.time() - start_time) * 1000

            enhanced_result = {
                "token_count": token_count,
                "character_count": len(text),
                "word_count": len(text.split()) if text.strip() else 0,
                "model": model_name,
                "method": "fallback",
                "type": "fallback",
                "text_preview": text[:100] + "..." if len(text) > 100 else text,
                "warning": f"Erro ao usar modelo '{model_name}': {e}. Usando fallback.",
                "validation_status": {
                    "text_valid": text_validation.is_valid,
                    "count_valid": False,
                    "warnings": [f"Erro na contagem: {str(e)}"],
                },
                "performance_metrics": {
                    "duration_ms": duration_ms,
                    "tokens_per_second": 0,
                    "processing_efficiency": "error",
                },
            }

        # Aplica limite se especificado
        if max_tokens is not None:
            enhanced_result["max_tokens"] = max_tokens
            enhanced_result["truncated"] = enhanced_result["token_count"] > max_tokens
        else:
            enhanced_result["max_tokens"] = None
            enhanced_result["truncated"] = False

        return enhanced_result


def register_custom_model(
    name: str,
    tokenizer_type: TokenizerTypeEnum = TokenizerTypeEnum.CUSTOM,
    max_tokens: int | None = None,
    encoding: str | None = None,
    description: str | None = None,
) -> None:
    """Registra modelo customizado.

    Args:
        name: Nome único do modelo.
        tokenizer_type: Tipo de tokenizer.
        max_tokens: Limite de tokens.
        encoding: Encoding para modelos OpenAI.
        description: Descrição do modelo.

    Raises:
        ValueError: Se nome já estiver registrado.
    """
    manager = _get_model_manager()
    manager.register_custom_model(
        name=name,
        tokenizer_type=tokenizer_type,
        max_tokens=max_tokens,
        encoding=encoding,
        description=description,
    )


def list_available_models(tokenizer_type: TokenizerTypeEnum | None = None) -> list[str]:
    """Lista modelos disponíveis.

    Args:
        tokenizer_type: Filtro por tipo (opcional).

    Returns:
        Lista de nomes de modelos.
    """
    try:
        manager = _get_model_manager()
        return manager.list_models(tokenizer_type)
    except Exception:
        return []


def get_model_info(model_name: str) -> dict[str, Any] | None:
    """Obtém informações do modelo.

    Args:
        model_name: Nome do modelo.

    Returns:
        Informações do modelo ou None.
    """
    try:
        manager = _get_model_manager()
        model_info = manager.get_model_info(model_name)
        if model_info is None:
            return None

        return {
            "name": model_info.name,
            "type": model_info.type.value,
            "max_tokens": model_info.max_tokens,
            "provider": model_info.provider,
            "description": model_info.description,
        }
    except Exception:
        return None


def is_model_registered(model_name: str) -> bool:
    """Verifica se modelo está registrado.

    Args:
        model_name: Nome do modelo.

    Returns:
        True se registrado.
    """
    try:
        manager = _get_model_manager()
        return model_name in manager
    except Exception:
        return False


def get_portuguese_models() -> list[str]:
    """Lista modelos para português.

    Returns:
        Lista de modelos recomendados.
    """
    try:
        manager = _get_model_manager()
        return manager.get_portuguese_models()
    except Exception:
        return []


# Compatibilidade com versão anterior
try:
    TokenizerModel = OpenAIModelEnum  # Alias para compatibilidade
except NameError:
    pass  # Se OpenAIModelEnum não estiver disponível, ignora
