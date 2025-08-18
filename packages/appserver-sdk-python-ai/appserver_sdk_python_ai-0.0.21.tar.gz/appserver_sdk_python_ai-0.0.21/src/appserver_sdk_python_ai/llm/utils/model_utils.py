"""Utilitários avançados para gerenciamento de modelos LLM.

Este módulo fornece funcionalidades avançadas para:
- Listagem detalhada de modelos disponíveis
- Registro de modelos customizados
- Filtragem por idioma e capacidades
- Análise e resumos de modelos
"""

from __future__ import annotations

from typing import Any

from appserver_sdk_python_ai.llm.core.cache import cache_result
from appserver_sdk_python_ai.llm.core.enums import (
    HuggingFaceModelEnum,
    ModelProvider,
    OpenAIModelEnum,
    TokenizerTypeEnum,
)
from appserver_sdk_python_ai.llm.core.logging_config import (
    OperationType,
    get_logger,
    log_function_call,
)
from appserver_sdk_python_ai.llm.core.model_manager import (
    ModelInfo,
    TokenizerModelManager,
)
from appserver_sdk_python_ai.llm.core.validation import (
    ValidationLevel,
    validate_model_name,
)


@cache_result(key_prefix="models", ttl=300.0)  # Cache por 5 minutos
@log_function_call(OperationType.MODEL_LOAD, log_args=True)
def list_available_models(
    provider: str | ModelProvider | None = None,
    model_type: str | TokenizerTypeEnum | None = None,
    include_custom: bool = True,
) -> dict[str, list[dict[str, Any]]]:
    """Lista todos os modelos disponíveis organizados por provedor.

    Args:
        provider: Filtrar por provedor específico (opcional)
        model_type: Filtrar por tipo de modelo (opcional)
        include_custom: Incluir modelos customizados registrados

    Returns:
        Dicionário com modelos organizados por provedor

    Example:
        >>> models = list_available_models()
        >>> print(f"OpenAI: {len(models['OpenAI'])} modelos")
        >>> print(f"HuggingFace: {len(models['HuggingFace'])} modelos")
    """
    logger = get_logger()
    manager = TokenizerModelManager()
    all_models: dict[str, list[dict[str, Any]]] = {}

    with logger.operation_context(OperationType.MODEL_LOAD, "list_models") as ctx:
        ctx.metadata.update(
            {
                "provider": provider,
                "model_type": model_type,
                "include_custom": include_custom,
            }
        )

        # Converter parâmetros para string se necessário
        provider_filter = (
            provider.value
            if provider is not None and hasattr(provider, "value")
            else provider
        )
        type_filter = (
            model_type.value
            if model_type is not None and hasattr(model_type, "value")
            else model_type
        )

        # Obter todos os modelos registrados
        model_names = manager.list_models()
        logger.debug(f"Encontrados {len(model_names)} modelos registrados")

        for model_name in model_names:
            model_info = manager.get_model_info(model_name)
            if not model_info:
                continue

            # Aplicar filtros
            if provider_filter and model_info.provider != provider_filter:
                continue

            # Garantir que type seja tratado corretamente
            model_type_value = (
                model_info.type.value
                if hasattr(model_info.type, "value")
                else str(model_info.type)
            )
            if type_filter and model_type_value != type_filter:
                continue

            # Organizar por provedor
            provider_name = (
                model_info.provider
                if isinstance(model_info.provider, str)
                else str(model_info.provider)
            )
            if provider_name not in all_models:
                all_models[provider_name] = []

            model_dict = {
                "name": model_info.name,
                "type": model_type_value,
                "max_tokens": model_info.max_tokens,
                "description": model_info.description,
                "is_custom": model_name not in [m.value for m in OpenAIModelEnum]
                and model_name not in [m.value for m in HuggingFaceModelEnum],
            }

            # Filtrar modelos customizados se solicitado
            if not include_custom and model_dict["is_custom"]:
                continue

            all_models[provider_name].append(model_dict)

        total_models = sum(len(model_list) for model_list in all_models.values())
        logger.info(
            f"Listagem concluída: {total_models} modelos em {len(all_models)} provedores"
        )

    return all_models


@cache_result(key_prefix="model_details", ttl=600.0)  # Cache por 10 minutos
@log_function_call(OperationType.MODEL_LOAD, log_args=True)
def get_model_details(model_name: str) -> dict[str, Any] | None:
    """Obtém detalhes completos de um modelo específico.

    Args:
        model_name: Nome do modelo

    Returns:
        Dicionário com detalhes do modelo ou None se não encontrado

    Example:
        >>> details = get_model_details("gpt-4")
        >>> print(f"Max tokens: {details['max_tokens']}")
    """
    logger = get_logger()

    # Validar nome do modelo
    if not validate_model_name(model_name, ValidationLevel.STRICT):
        logger.warning(f"Nome de modelo inválido: {model_name}")
        return None

    with logger.operation_context(OperationType.MODEL_LOAD, "get_model_details") as ctx:
        ctx.metadata.update({"model_name": model_name})

        manager = TokenizerModelManager()
        model_info = manager.get_model_info(model_name)

        if not model_info:
            logger.warning(f"Modelo não encontrado: {model_name}")
            return None

        logger.debug(f"Detalhes obtidos para modelo: {model_name}")

        # Garantir que provider e type sejam tratados corretamente
        provider = (
            model_info.provider
            if isinstance(model_info.provider, str)
            else str(model_info.provider)
        )
        model_type = (
            model_info.type.value
            if hasattr(model_info.type, "value")
            else str(model_info.type)
        )

        return {
            "name": model_info.name,
            "provider": provider,
            "type": model_type,
            "max_tokens": model_info.max_tokens,
            "description": model_info.description,
            "is_registered": True,
            "is_available": manager.is_model_available(model_name),
            "encoding_info": _get_encoding_info(model_name, model_info),
        }


def _get_encoding_info(model_name: str, model_info: ModelInfo) -> dict[str, Any]:
    """Obtém informações de encoding para um modelo."""
    encoding_info = {"method": "unknown"}

    try:
        # Tentar obter informações específicas do modelo
        if model_info.type == TokenizerTypeEnum.OPENAI:
            # Verificar se é um modelo OpenAI conhecido
            for openai_model in OpenAIModelEnum:
                if openai_model.value == model_name:
                    encoding_info.update(
                        {
                            "method": "tiktoken",
                            "encoding_name": openai_model.get_encoding_name(),
                            "max_context_tokens": str(openai_model.get_max_tokens()),
                        }
                    )
                    break
        elif model_info.type == TokenizerTypeEnum.HUGGINGFACE:
            # Verificar se é um modelo HuggingFace conhecido
            for hf_model in HuggingFaceModelEnum:
                if hf_model.value == model_name:
                    encoding_info.update(
                        {
                            "method": "huggingface",
                            "max_sequence_length": str(
                                hf_model.get_max_sequence_length()
                            ),
                        }
                    )
                    break
    except Exception:
        # Em caso de erro, manter informações básicas
        pass

    return encoding_info


@log_function_call(OperationType.MODEL_LOAD, log_args=True)
def register_custom_model_advanced(
    name: str,
    provider: str = "Custom",
    model_type: TokenizerTypeEnum = TokenizerTypeEnum.DEFAULT,
    max_tokens: int = 4096,
    description: str | None = None,
    encoding_method: str = "fallback",
    **kwargs,
) -> bool:
    """Registra um modelo customizado com configurações avançadas.

    Args:
        name: Nome único do modelo
        provider: Nome do provedor
        model_type: Tipo do tokenizador
        max_tokens: Limite máximo de tokens
        description: Descrição do modelo
        encoding_method: Método de encoding a ser usado
        **kwargs: Parâmetros adicionais

    Returns:
        True se registrado com sucesso, False caso contrário

    Example:
        >>> success = register_custom_model_advanced(
        ...     name="meu-modelo-local",
        ...     provider="Local",
        ...     max_tokens=8192,
        ...     description="Modelo local personalizado"
        ... )
        >>> print(f"Modelo registrado: {success}")
    """
    logger = get_logger()

    # Validar nome do modelo
    if not validate_model_name(name, ValidationLevel.LENIENT):
        logger.error(f"Nome de modelo inválido: {name}")
        return False

    with logger.operation_context(
        OperationType.MODEL_LOAD, "register_custom_model"
    ) as ctx:
        ctx.metadata.update(
            {
                "name": name,
                "provider": provider,
                "model_type": model_type.value,
                "max_tokens": max_tokens,
            }
        )

        try:
            manager = TokenizerModelManager()

            # Preparar descrição
            if description is None:
                description = f"Modelo customizado: {name}"

            # Registrar o modelo
            manager.register_custom_model(
                name=name,
                provider=provider,
                type=model_type,
                max_tokens=max_tokens,
                description=description,
                encoding_method=encoding_method,
                **kwargs,
            )

            logger.info(f"Modelo customizado registrado com sucesso: {name}")

            # Invalidar cache relacionado
            from appserver_sdk_python_ai.llm.core.cache import clear_cache

            clear_cache("models:")
            clear_cache("model_details:")

            return True

        except Exception as e:
            logger.error(f"Erro ao registrar modelo customizado {name}: {e}")
            return False


def get_portuguese_models() -> list[dict[str, Any]]:
    """Lista modelos otimizados para português.

    Returns:
        Lista de modelos com suporte ao português

    Example:
        >>> pt_models = get_portuguese_models()
        >>> for model in pt_models:
        ...     print(f"{model['name']} - {model['description']}")
    """
    from appserver_sdk_python_ai.llm.core.enums.huggingface_model_enum import (
        HuggingFaceModelEnum,
    )

    manager = TokenizerModelManager()
    pt_model_enums = HuggingFaceModelEnum.get_portuguese_models()

    models = []
    for model_enum in pt_model_enums:
        model_name = model_enum.value
        model_info = manager.get_model_info(model_name)
        if model_info:
            # Garantir que provider seja uma string
            provider = (
                model_info.provider
                if isinstance(model_info.provider, str)
                else str(model_info.provider)
            )
            models.append(
                {
                    "name": model_info.name,
                    "provider": provider,
                    "type": model_info.type.value
                    if hasattr(model_info.type, "value")
                    else str(model_info.type),
                    "max_tokens": model_info.max_tokens,
                    "description": model_info.description,
                    "language_support": "Portuguese",
                }
            )

    return models


def get_multilingual_models() -> list[dict[str, Any]]:
    """Lista modelos com suporte multilíngue.

    Returns:
        Lista de modelos multilíngues
    """
    manager = TokenizerModelManager()
    ml_model_names = manager.get_multilingual_models()

    models = []
    for model_name in ml_model_names:
        model_info = manager.get_model_info(model_name)
        if model_info:
            # Garantir que provider seja uma string
            provider = (
                model_info.provider
                if isinstance(model_info.provider, str)
                else str(model_info.provider)
            )
            models.append(
                {
                    "name": model_info.name,
                    "provider": provider,
                    "type": model_info.type.value
                    if hasattr(model_info.type, "value")
                    else str(model_info.type),
                    "max_tokens": model_info.max_tokens,
                    "description": model_info.description,
                    "language_support": "Multilingual",
                }
            )

    return models


def print_models_summary() -> None:
    """Imprime um resumo formatado de todos os modelos disponíveis.

    Example:
        >>> print_models_summary()
        📊 Resumo de Modelos Disponíveis
        ================================

        🤖 OpenAI: 8 modelos
        🤗 HuggingFace: 15 modelos
        ...
    """
    models = list_available_models()

    print("📊 Resumo de Modelos Disponíveis")
    print("=" * 35)
    print()

    total_models = 0
    for provider, provider_models in models.items():
        icon = (
            "🤖" if provider == "OpenAI" else "🤗" if provider == "HuggingFace" else "⚙️"
        )
        print(f"{icon} {provider}: {len(provider_models)} modelos")
        total_models += len(provider_models)

    print()
    print(f"📈 Total: {total_models} modelos disponíveis")

    # Mostrar modelos para português
    pt_models = get_portuguese_models()
    if pt_models:
        print(f"🇧🇷 Português: {len(pt_models)} modelos otimizados")

    # Mostrar modelos multilíngues
    ml_models = get_multilingual_models()
    if ml_models:
        print(f"🌍 Multilíngue: {len(ml_models)} modelos")
