"""Módulo shared com funcionalidades comuns para todos os módulos do SDK."""

# Core functionality
# New unified systems
from appserver_sdk_python_ai.shared.core.cache import (
    CacheError,
    FileCacheBackend,
    MemoryCacheBackend,
    UnifiedCacheManager,
    default_cache,
)
from appserver_sdk_python_ai.shared.core.config import BaseConfig, ConfigManager
from appserver_sdk_python_ai.shared.core.engines import (
    BaseEngine,
    EngineError,
    EngineInitializationError,
    EngineManager,
    EngineNotFoundError,
    EngineRegistry,
    EngineStatus,
    default_engine_manager,
    default_engine_registry,
)
from appserver_sdk_python_ai.shared.core.logging import SDKLogger
from appserver_sdk_python_ai.shared.core.network import (
    AsyncHTTPClient,
    HTTPClient,
    NetworkConfig,
    NetworkError,
    NetworkUtils,
    RateLimiter,
    RateLimitError,
    TimeoutError,
    URLBuilder,
    default_http_client,
    default_network_config,
)

# Standard configurations
from appserver_sdk_python_ai.shared.core.standard_configs import (
    CacheStandardConfig,
    EngineStandardConfig,
    NetworkStandardConfig,
    ProcessingStandardConfig,
    SecurityStandardConfig,
    UnifiedModuleConfig,
    create_llm_config,
    create_module_config,
    create_ocr_config,
    create_webscraping_config,
)
from appserver_sdk_python_ai.shared.core.validation import (
    COMMON_VALIDATORS,
    ChoiceValidator,
    CustomValidator,
    DataValidator,
    EmailValidator,
    LengthValidator,
    RangeValidator,
    RegexValidator,
    TypeValidator,
    URLValidator,
    ValidationRule,
    ValidationSchema,
)

# Exceptions
from appserver_sdk_python_ai.shared.exceptions import (
    ConfigurationError,
    LoggingError,
    SharedError,
    UtilityError,
    ValidationError,
)

# Common utilities
from appserver_sdk_python_ai.shared.utils.common import (
    DependencyChecker,
    HealthChecker,
    VersionInfo,
)

# Processing utilities
from appserver_sdk_python_ai.shared.utils.processing import (
    DataProcessor,
    FileProcessor,
    ImageProcessor,
    ProcessingError,
    TextProcessor,
    data_processor,
    file_processor,
    image_processor,
    text_processor,
)

__version__ = "1.0.0"

__all__ = [
    # Core
    "BaseConfig",
    "ConfigManager",
    "SDKLogger",
    # Cache System
    "UnifiedCacheManager",
    "MemoryCacheBackend",
    "FileCacheBackend",
    "CacheError",
    "default_cache",
    # Validation System
    "DataValidator",
    "ValidationSchema",
    "ValidationRule",
    "TypeValidator",
    "RangeValidator",
    "LengthValidator",
    "RegexValidator",
    "URLValidator",
    "EmailValidator",
    "ChoiceValidator",
    "CustomValidator",
    "COMMON_VALIDATORS",
    # Network System
    "HTTPClient",
    "AsyncHTTPClient",
    "NetworkConfig",
    "RateLimiter",
    "URLBuilder",
    "NetworkUtils",
    "NetworkError",
    "RateLimitError",
    "TimeoutError",
    "default_http_client",
    "default_network_config",
    # Engine Management
    "BaseEngine",
    "EngineRegistry",
    "EngineManager",
    "EngineStatus",
    "EngineError",
    "EngineNotFoundError",
    "EngineInitializationError",
    "default_engine_registry",
    "default_engine_manager",
    # Processing Utilities
    "TextProcessor",
    "ImageProcessor",
    "FileProcessor",
    "DataProcessor",
    "ProcessingError",
    "text_processor",
    "file_processor",
    "data_processor",
    "image_processor",
    # Exceptions
    "ConfigurationError",
    "LoggingError",
    "SharedError",
    "UtilityError",
    "ValidationError",
    # Common Utils
    "DependencyChecker",
    "HealthChecker",
    "VersionInfo",
    # Standard configurations
    "NetworkStandardConfig",
    "CacheStandardConfig",
    "ProcessingStandardConfig",
    "SecurityStandardConfig",
    "EngineStandardConfig",
    "UnifiedModuleConfig",
    "create_module_config",
    "create_webscraping_config",
    "create_ocr_config",
    "create_llm_config",
]
