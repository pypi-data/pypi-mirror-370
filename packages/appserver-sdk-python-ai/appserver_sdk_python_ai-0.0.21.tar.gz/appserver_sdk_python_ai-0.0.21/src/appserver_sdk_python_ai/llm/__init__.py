"""Módulo LLM do AppServer SDK Python AI"""

import logging

__version__ = "1.0.0"

# Imports absolutos dentro do módulo
# Importar funcionalidades do core (cache, validação, logging)
from appserver_sdk_python_ai.llm.core import (
    # Logging
    LogLevel,
    # Metrics
    MetricType,
    OperationStatus,
    OperationType,
    # Validation
    ValidationLevel,
    # Cache
    cache_result,
    clear_cache,
    export_metrics,
    get_cache,
    get_cache_memory_usage,
    get_cache_stats,
    get_logger,
    get_metrics_collector,
    get_metrics_summary,
    increment_counter,
    log_function_call,
    record_operation_metric,
    set_gauge,
    validate_config,
    validate_model_name,
    validate_text,
    validate_token_count,
)
from appserver_sdk_python_ai.llm.core.enums import (
    ModelCapability,
    ModelProvider,
    ModelType,
    SupportedLanguage,
    TokenizationMethod,
)

# Importar documentação interativa
from appserver_sdk_python_ai.llm.docs import (
    docs as docs_llm,
)
from appserver_sdk_python_ai.llm.docs import (
    help as help_llm,
)
from appserver_sdk_python_ai.llm.docs import (
    search as search_llm_docs,
)
from appserver_sdk_python_ai.llm.exceptions import (
    LLMAuthenticationError,
    LLMConfigurationError,
    LLMContentFilterError,
    LLMError,
    LLMInvalidInputError,
    LLMModelNotFoundError,
    LLMNetworkError,
    LLMProviderError,
    LLMRateLimitError,
    LLMResponseError,
    LLMStreamingError,
    LLMTimeoutError,
    LLMTokenLimitError,
    LLMValidationError,
)
from appserver_sdk_python_ai.llm.service.ai_service import (
    AIConfig,
    AIService,
    AsyncAIService,
    ChatResponse,
    Message,
    StreamChunk,
    Usage,
)
from appserver_sdk_python_ai.llm.service.client import (
    LLMClient,
    MockLLMClient,
)
from appserver_sdk_python_ai.llm.service.token_service import (
    get_model_info,
    get_token_count,
    get_token_count_with_model,
    is_model_registered,
    list_available_models,
    register_custom_model,
)

# Importar utilitários avançados
from appserver_sdk_python_ai.llm.utils import (
    get_model_details,
    get_multilingual_models,
    get_portuguese_models,
    print_models_summary,
    register_custom_model_advanced,
)
from appserver_sdk_python_ai.llm.utils import (
    list_available_models as list_models_detailed,
)

# Importar funcionalidades comuns do módulo shared
from appserver_sdk_python_ai.shared import (
    DependencyChecker,
    HealthChecker,
    SDKLogger,
    VersionInfo,
)


def get_version_info():
    """Retorna informações sobre a versão e dependências."""
    return VersionInfo.create_version_info(
        module_name="llm",
        module_version=__version__,
        dependencies=check_dependencies(),
        additional_info={
            "available_models": len(list_available_models()),
            "portuguese_models": len(get_portuguese_models()),
        },
    )


def check_dependencies():
    """Verifica se todas as dependências estão instaladas."""
    return DependencyChecker.check_dependencies(
        ["tiktoken", "openai", "anthropic", "requests"]
    )


def health_check():
    """Verifica a saúde do módulo e suas dependências."""
    dependencies = check_dependencies()
    features = {
        "token_counting": True,
        "model_management": True,
        "portuguese_support": len(get_portuguese_models()) > 0,
        "custom_models": True,
    }

    return HealthChecker.create_health_report(
        module_name="llm",
        version=__version__,
        dependencies=dependencies,
        features=features,
        critical_deps=[],  # Nenhuma dependência é crítica por padrão
        optional_deps=["tiktoken", "openai", "anthropic", "requests"],
    )


def print_status():
    """Imprime status do módulo."""
    health = health_check()

    # Adicionar informações específicas do LLM
    print("=" * 60)
    print("MÓDULO LLM - appserver_sdk_python_ai")
    print("=" * 60)
    print(f"Versão: {__version__}")
    print(f"Status: {health['status']}")

    # Usar o método padrão para o resto
    HealthChecker.print_health_status(
        health, show_dependencies=True, show_features=True
    )

    # Informações adicionais específicas do LLM
    print("\n🤖 Informações dos modelos:")
    print(f"  • Total de modelos disponíveis: {len(list_available_models())}")
    print(f"  • Modelos com suporte ao português: {len(get_portuguese_models())}")

    print("\n📋 Provedores suportados:")
    providers = set()
    for model_info in list_available_models():
        if hasattr(model_info, "provider"):
            providers.add(model_info.provider.value)
    for provider in sorted(providers):
        print(f"  • {provider}")


def setup_logging(level=logging.INFO, format_string=None):
    """
    Configura logging para o módulo LLM.

    Args:
        level: Nível de logging
        format_string: Formato customizado para logs
    """
    return SDKLogger.setup_logging(
        level=level,
        format_string=format_string,
        logger_name="appserver_sdk_python_ai.llm",
    )


__all__ = [
    # Enums
    "ModelType",
    "ModelProvider",
    "ModelCapability",
    "TokenizationMethod",
    "SupportedLanguage",
    # Clientes
    "LLMClient",
    "MockLLMClient",
    "AIService",
    "AsyncAIService",
    "AIConfig",
    "ChatResponse",
    "Message",
    "StreamChunk",
    "Usage",
    # Funções principais
    "get_token_count",
    "get_token_count_with_model",
    "list_available_models",
    "get_model_info",
    "get_portuguese_models",
    "is_model_registered",
    "register_custom_model",
    # Funções avançadas
    "list_models_detailed",
    "get_model_details",
    "get_multilingual_models",
    "register_custom_model_advanced",
    "print_models_summary",
    # Documentação interativa
    "help_llm",
    "docs_llm",
    "search_llm_docs",
    # Cache
    "cache_result",
    "get_cache",
    "clear_cache",
    "get_cache_stats",
    "get_cache_memory_usage",
    # Validation
    "ValidationLevel",
    "validate_model_name",
    "validate_token_count",
    "validate_config",
    "validate_text",
    # Logging
    "LogLevel",
    "OperationType",
    "get_logger",
    "log_function_call",
    # Exceções
    "LLMError",
    "LLMProviderError",
    "LLMAuthenticationError",
    "LLMRateLimitError",
    "LLMModelNotFoundError",
    "LLMNetworkError",
    "LLMTokenLimitError",
    "LLMTimeoutError",
    "LLMValidationError",
    "LLMConfigurationError",
    "LLMInvalidInputError",
    "LLMResponseError",
    "LLMStreamingError",
    "LLMContentFilterError",
    # Utilitários
    "get_version_info",
    "check_dependencies",
    "health_check",
    "print_status",
    "setup_logging",
    # Versão
    "__version__",
]
