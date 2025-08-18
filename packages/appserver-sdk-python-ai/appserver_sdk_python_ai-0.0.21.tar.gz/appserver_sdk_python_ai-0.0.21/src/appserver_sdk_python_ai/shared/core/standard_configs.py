"""Configurações padronizadas para todos os módulos do SDK."""

from appserver_sdk_python_ai.shared.core.config import BaseConfig
from appserver_sdk_python_ai.shared.core.validation import (
    ChoiceValidator,
    RangeValidator,
    TypeValidator,
    ValidationRule,
    ValidationSchema,
)


class NetworkStandardConfig(BaseConfig):
    """Configuração padronizada para funcionalidades de rede."""

    def __init__(self, **kwargs):
        # Extrair apenas os parâmetros compatíveis com BaseConfig
        base_params = {
            "default_timeout": kwargs.get("default_timeout", 30),
            "max_retries": kwargs.get("max_retries", 3),
            "retry_delay": kwargs.get("retry_delay", 1.0),
            "user_agent": kwargs.get("user_agent", "AppServer-SDK-Python/1.0"),
        }

        # Configurações específicas de rede (não passadas para BaseConfig)
        self.backoff_factor = kwargs.get("backoff_factor", 2.0)
        self.verify_ssl = kwargs.get("verify_ssl", True)
        self.rate_limit = kwargs.get("rate_limit", None)
        self.rate_limit_window = kwargs.get("rate_limit_window", 60)
        self.headers = kwargs.get("headers", {})

        super().__init__(**base_params)

    def get_validation_schema(self) -> ValidationSchema:
        """Retorna schema de validação para configurações de rede."""
        return ValidationSchema(
            [
                ValidationRule(
                    "default_timeout",
                    [TypeValidator(int), RangeValidator(1, 300)],
                    default=30,
                ),
                ValidationRule(
                    "max_retries",
                    [TypeValidator(int), RangeValidator(0, 10)],
                    default=3,
                ),
                ValidationRule(
                    "retry_delay",
                    [TypeValidator((int, float)), RangeValidator(0, 60)],
                    default=1.0,
                ),
                ValidationRule(
                    "backoff_factor",
                    [TypeValidator((int, float)), RangeValidator(1, 10)],
                    default=2.0,
                ),
                ValidationRule("user_agent", [TypeValidator(str)], required=False),
                ValidationRule("verify_ssl", [TypeValidator(bool)], default=True),
                ValidationRule(
                    "rate_limit",
                    [TypeValidator(int), RangeValidator(1, 10000)],
                    required=False,
                ),
                ValidationRule(
                    "rate_limit_window",
                    [TypeValidator(int), RangeValidator(1, 3600)],
                    default=60,
                ),
                ValidationRule("headers", [TypeValidator(dict)], default={}),
            ]
        )


class CacheStandardConfig(BaseConfig):
    """Configuração padronizada para funcionalidades de cache."""

    def __init__(self, **kwargs):
        # Extrair apenas os parâmetros compatíveis com BaseConfig
        base_params = {
            "enable_cache": kwargs.get("enable_cache", True),
            "cache_ttl": kwargs.get("cache_ttl", 3600),
        }

        # Configurações específicas de cache (não passadas para BaseConfig)
        self.cache_backend = kwargs.get("cache_backend", "memory")
        self.max_cache_size = kwargs.get("max_cache_size", 1000)
        self.cache_dir = kwargs.get("cache_dir", ".sdk_cache")
        self.max_cache_size_mb = kwargs.get("max_cache_size_mb", 100)

        super().__init__(**base_params)

    def get_validation_schema(self) -> ValidationSchema:
        """Retorna schema de validação para configurações de cache."""
        return ValidationSchema(
            [
                ValidationRule("enable_cache", [TypeValidator(bool)], default=True),
                ValidationRule(
                    "cache_backend",
                    [TypeValidator(str), ChoiceValidator(["memory", "file"])],
                    default="memory",
                ),
                ValidationRule(
                    "cache_ttl",
                    [TypeValidator(int), RangeValidator(1, 86400)],
                    default=3600,
                ),
                ValidationRule(
                    "max_cache_size",
                    [TypeValidator(int), RangeValidator(1, 100000)],
                    default=1000,
                ),
                ValidationRule("cache_dir", [TypeValidator(str)], default=".sdk_cache"),
                ValidationRule(
                    "max_cache_size_mb",
                    [TypeValidator(int), RangeValidator(1, 10000)],
                    default=100,
                ),
            ]
        )


class ProcessingStandardConfig(BaseConfig):
    """Configuração padronizada para funcionalidades de processamento."""

    def __init__(self, **kwargs):
        # Extrair apenas os parâmetros compatíveis com BaseConfig
        base_params = {}

        # Configurações específicas de processamento (não passadas para BaseConfig)
        self.max_file_size_mb = kwargs.get("max_file_size_mb", 100)
        self.supported_formats = kwargs.get("supported_formats", [])
        self.enable_preprocessing = kwargs.get("enable_preprocessing", True)
        self.enable_postprocessing = kwargs.get("enable_postprocessing", True)
        self.batch_size = kwargs.get("batch_size", 10)
        self.parallel_processing = kwargs.get("parallel_processing", False)
        self.max_workers = kwargs.get("max_workers", 4)

        super().__init__(**base_params)

    def get_validation_schema(self) -> ValidationSchema:
        """Retorna schema de validação para configurações de processamento."""
        return ValidationSchema(
            [
                ValidationRule(
                    "max_file_size_mb",
                    [TypeValidator(int), RangeValidator(1, 1000)],
                    default=100,
                ),
                ValidationRule("supported_formats", [TypeValidator(list)], default=[]),
                ValidationRule(
                    "enable_preprocessing", [TypeValidator(bool)], default=True
                ),
                ValidationRule(
                    "enable_postprocessing", [TypeValidator(bool)], default=True
                ),
                ValidationRule(
                    "batch_size",
                    [TypeValidator(int), RangeValidator(1, 1000)],
                    default=10,
                ),
                ValidationRule(
                    "parallel_processing", [TypeValidator(bool)], default=False
                ),
                ValidationRule(
                    "max_workers",
                    [TypeValidator(int), RangeValidator(1, 32)],
                    default=4,
                ),
            ]
        )


class SecurityStandardConfig(BaseConfig):
    """Configuração padronizada para funcionalidades de segurança."""

    def __init__(self, **kwargs):
        # Extrair apenas os parâmetros compatíveis com BaseConfig
        base_params = {}

        # Configurações específicas de segurança (não passadas para BaseConfig)
        self.verify_ssl = kwargs.get("verify_ssl", True)
        self.api_key = kwargs.get("api_key", None)
        self.api_secret = kwargs.get("api_secret", None)
        self.allowed_domains = kwargs.get("allowed_domains", [])
        self.rate_limit = kwargs.get("rate_limit", None)
        self.enable_logging = kwargs.get("enable_logging", True)
        self.log_sensitive_data = kwargs.get("log_sensitive_data", False)
        self.encryption_enabled = kwargs.get("encryption_enabled", False)

        super().__init__(**base_params)

    def get_validation_schema(self) -> ValidationSchema:
        """Retorna schema de validação para configurações de segurança."""
        return ValidationSchema(
            [
                ValidationRule("verify_ssl", [TypeValidator(bool)], default=True),
                ValidationRule("api_key", [TypeValidator(str)], required=False),
                ValidationRule("api_secret", [TypeValidator(str)], required=False),
                ValidationRule("allowed_domains", [TypeValidator(list)], default=[]),
                ValidationRule(
                    "rate_limit",
                    [TypeValidator(int), RangeValidator(1, 10000)],
                    required=False,
                ),
                ValidationRule("enable_logging", [TypeValidator(bool)], default=True),
                ValidationRule(
                    "log_sensitive_data", [TypeValidator(bool)], default=False
                ),
                ValidationRule(
                    "encryption_enabled", [TypeValidator(bool)], default=False
                ),
            ]
        )


class EngineStandardConfig(BaseConfig):
    """Configuração padronizada para engines/provedores."""

    def __init__(self, **kwargs):
        # Extrair apenas os parâmetros compatíveis com BaseConfig
        base_params = {}

        # Configurações específicas de engines (não passadas para BaseConfig)
        self.preferred_engines = kwargs.get("preferred_engines", [])
        self.fallback_enabled = kwargs.get("fallback_enabled", True)
        self.engine_timeout = kwargs.get("engine_timeout", 30)
        self.auto_initialize = kwargs.get("auto_initialize", True)
        self.engine_configs = kwargs.get("engine_configs", {})

        super().__init__(**base_params)

    def get_validation_schema(self) -> ValidationSchema:
        """Retorna schema de validação para configurações de engines."""
        return ValidationSchema(
            [
                ValidationRule("preferred_engines", [TypeValidator(list)], default=[]),
                ValidationRule("fallback_enabled", [TypeValidator(bool)], default=True),
                ValidationRule(
                    "engine_timeout",
                    [TypeValidator(int), RangeValidator(1, 300)],
                    default=30,
                ),
                ValidationRule("auto_initialize", [TypeValidator(bool)], default=True),
                ValidationRule("engine_configs", [TypeValidator(dict)], default={}),
            ]
        )


class UnifiedModuleConfig(BaseConfig):
    """Configuração unificada que combina todas as configurações padronizadas."""

    def __init__(self, **kwargs):
        # Extrair configurações específicas
        network_config = kwargs.pop("network", {})
        cache_config = kwargs.pop("cache", {})
        processing_config = kwargs.pop("processing", {})
        security_config = kwargs.pop("security", {})
        engine_config = kwargs.pop("engines", {})

        # Configurações específicas (não passadas para BaseConfig)
        self.module_name = kwargs.pop("module_name", "unknown")
        self.version = kwargs.pop("version", "1.0.0")
        self.debug = kwargs.pop("debug", False)
        self.network = NetworkStandardConfig(**network_config)
        self.cache = CacheStandardConfig(**cache_config)
        self.processing = ProcessingStandardConfig(**processing_config)
        self.security = SecurityStandardConfig(**security_config)
        self.engines = EngineStandardConfig(**engine_config)

        # Passar apenas parâmetros compatíveis para BaseConfig
        super().__init__(**kwargs)

    def get_validation_schema(self) -> ValidationSchema:
        """Retorna schema de validação para configuração unificada."""
        return ValidationSchema(
            [
                ValidationRule("module_name", [TypeValidator(str)], default="unknown"),
                ValidationRule("version", [TypeValidator(str)], default="1.0.0"),
                ValidationRule("debug", [TypeValidator(bool)], default=False),
            ]
        )

    def validate_all(self) -> None:
        """Valida todas as configurações."""
        # Validar configuração principal
        schema = self.get_validation_schema()
        schema.validate_and_raise(self.to_dict())

        # Validar sub-configurações
        if hasattr(self.network, "get_validation_schema"):
            network_schema = self.network.get_validation_schema()
            network_schema.validate_and_raise(self.network.to_dict())

        if hasattr(self.cache, "get_validation_schema"):
            cache_schema = self.cache.get_validation_schema()
            cache_schema.validate_and_raise(self.cache.to_dict())

        if hasattr(self.processing, "get_validation_schema"):
            processing_schema = self.processing.get_validation_schema()
            processing_schema.validate_and_raise(self.processing.to_dict())

        if hasattr(self.security, "get_validation_schema"):
            security_schema = self.security.get_validation_schema()
            security_schema.validate_and_raise(self.security.to_dict())

        if hasattr(self.engines, "get_validation_schema"):
            engines_schema = self.engines.get_validation_schema()
            engines_schema.validate_and_raise(self.engines.to_dict())


def create_module_config(module_name: str, **kwargs) -> UnifiedModuleConfig:
    """Cria configuração padronizada para um módulo."""
    config_data = {"module_name": module_name}
    config_data.update(kwargs)

    config = UnifiedModuleConfig(**config_data)
    config.validate_all()

    return config


# Configurações pré-definidas para módulos específicos
def create_webscraping_config(**kwargs) -> UnifiedModuleConfig:
    """Cria configuração otimizada para web scraping."""
    defaults = {
        "network": {
            "timeout": 30,
            "max_retries": 3,
            "user_agent": "AppServer-WebScraping-SDK/1.0",
            "verify_ssl": True,
        },
        "cache": {
            "enable_cache": True,
            "cache_backend": "file",
            "cache_ttl": 3600,
            "max_cache_size_mb": 500,
        },
        "processing": {
            "max_file_size_mb": 50,
            "supported_formats": [".html", ".xml", ".json"],
            "batch_size": 5,
        },
        "security": {"verify_ssl": True, "rate_limit": 100, "allowed_domains": []},
    }

    # Mesclar com configurações fornecidas
    for key, value in kwargs.items():
        if (
            key in defaults
            and isinstance(defaults[key], dict)
            and isinstance(value, dict)
        ):
            defaults[key].update(value)  # type: ignore[attr-defined]
        else:
            defaults[key] = value

    return create_module_config("webscraping", **defaults)


def create_ocr_config(**kwargs) -> UnifiedModuleConfig:
    """Cria configuração otimizada para OCR."""
    defaults = {
        "processing": {
            "max_file_size_mb": 100,
            "supported_formats": [".jpg", ".jpeg", ".png", ".bmp", ".tiff"],
            "enable_preprocessing": True,
            "batch_size": 10,
            "parallel_processing": True,
            "max_workers": 4,
        },
        "cache": {
            "enable_cache": True,
            "cache_backend": "file",
            "cache_ttl": 7200,
            "max_cache_size_mb": 1000,
        },
        "engines": {
            "preferred_engines": ["tesseract", "easyocr", "paddleocr"],
            "fallback_enabled": True,
            "auto_initialize": True,
        },
    }

    # Mesclar com configurações fornecidas
    for key, value in kwargs.items():
        if (
            key in defaults
            and isinstance(defaults[key], dict)
            and isinstance(value, dict)
        ):
            defaults[key].update(value)  # type: ignore[attr-defined]
        else:
            defaults[key] = value

    return create_module_config("ocr", **defaults)


def create_llm_config(**kwargs) -> UnifiedModuleConfig:
    """Cria configuração otimizada para LLM."""
    defaults = {
        "network": {
            "timeout": 60,
            "max_retries": 3,
            "rate_limit": 60,
            "rate_limit_window": 60,
        },
        "cache": {
            "enable_cache": True,
            "cache_backend": "file",
            "cache_ttl": 3600,
            "max_cache_size_mb": 200,
        },
        "security": {
            "verify_ssl": True,
            "log_sensitive_data": False,
            "encryption_enabled": True,
        },
        "engines": {
            "preferred_engines": ["openai", "anthropic", "local"],
            "fallback_enabled": True,
            "engine_timeout": 60,
        },
    }

    # Mesclar com configurações fornecidas
    for key, value in kwargs.items():
        if (
            key in defaults
            and isinstance(defaults[key], dict)
            and isinstance(value, dict)
        ):
            defaults[key].update(value)  # type: ignore[attr-defined]
        else:
            defaults[key] = value

    return create_module_config("llm", **defaults)
