"""Core do módulo LLM com funcionalidades avançadas.

Este módulo contém as funcionalidades centrais do sistema LLM:
- Configuração do sistema
- Sistema de cache LRU thread-safe
- Sistema de validação robusta
- Sistema de logging estruturado
"""

from appserver_sdk_python_ai.llm.core import config
from appserver_sdk_python_ai.llm.core.cache import (
    CacheEntry,
    LRUCache,
    cache_result,
    clear_cache,
    get_cache,
    get_cache_memory_usage,
    get_cache_stats,
)
from appserver_sdk_python_ai.llm.core.config import DEFAULT_LLM_CONFIG, LLMConfig
from appserver_sdk_python_ai.llm.core.logging_config import (
    LLMLogger,
    LogContext,
    LogLevel,
    OperationType,
    PerformanceFormatter,
    StructuredFormatter,
    get_logger,
    log_function_call,
)
from appserver_sdk_python_ai.llm.core.metrics import (
    MetricsCollector,
    MetricType,
    OperationStatus,
    SystemMetrics,
    export_metrics,
    get_metrics_collector,
    get_metrics_summary,
    increment_counter,
    record_operation_metric,
    set_gauge,
)
from appserver_sdk_python_ai.llm.core.validation import (
    BaseValidator,
    CompositeValidator,
    ConfigValidator,
    ModelNameValidator,
    TextValidator,
    TokenCountValidator,
    ValidationLevel,
    ValidationResult,
    validate_config,
    validate_model_name,
    validate_text,
    validate_token_count,
)

__all__ = [
    # Config
    "config",
    "LLMConfig",
    "DEFAULT_LLM_CONFIG",
    # Cache
    "CacheEntry",
    "LRUCache",
    "cache_result",
    "get_cache",
    "clear_cache",
    "get_cache_stats",
    "get_cache_memory_usage",
    # Validation
    "ValidationLevel",
    "ValidationResult",
    "BaseValidator",
    "ModelNameValidator",
    "TokenCountValidator",
    "ConfigValidator",
    "TextValidator",
    "CompositeValidator",
    "validate_model_name",
    "validate_token_count",
    "validate_config",
    "validate_text",
    # Logging
    "LogLevel",
    "OperationType",
    "LogContext",
    "StructuredFormatter",
    "PerformanceFormatter",
    "LLMLogger",
    "get_logger",
    "log_function_call",
    # Metrics
    "MetricType",
    "OperationStatus",
    "MetricsCollector",
    "SystemMetrics",
    "get_metrics_collector",
    "record_operation_metric",
    "increment_counter",
    "set_gauge",
    "get_metrics_summary",
    "export_metrics",
]
