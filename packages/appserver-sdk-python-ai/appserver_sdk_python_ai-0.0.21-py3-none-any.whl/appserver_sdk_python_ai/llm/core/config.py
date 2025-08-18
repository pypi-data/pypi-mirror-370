# appserver_sdk_python_ai/llm/core/config.py
"""
Sistema de configuração centralizada para o módulo LLM
=====================================================

Este módulo fornece um sistema de configuração centralizada que facilita
a manutenção e personalização do comportamento do módulo LLM.

Exemplo de uso:
    >>> from appserver_sdk_python_ai.llm.core.config import get_config, update_config
    >>> config = get_config()
    >>> config.cache.default_ttl
    300
    >>> update_config({'cache': {'default_ttl': 600}})
"""

import json
import os
import threading
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

# Configurações padrão para LLM
DEFAULT_LLM_CONFIG = {
    "timeout": 30.0,
    "max_retries": 3,
    "retry_delay": 1.0,
    "max_tokens": 4096,
    "temperature": 0.7,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
}


class LLMConfig:
    """Classe de configuração para LLM."""

    def __init__(self, **kwargs):
        """Inicializa a configuração com valores padrão e customizações."""
        self.config = DEFAULT_LLM_CONFIG.copy()
        self.config.update(kwargs)

    def get(self, key: str, default: Any = None) -> Any:
        """Obtém um valor de configuração."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Define um valor de configuração."""
        self.config[key] = value

    def update(self, config_dict: dict[str, Any]) -> None:
        """Atualiza múltiplos valores de configuração."""
        self.config.update(config_dict)

    def to_dict(self) -> dict[str, Any]:
        """Retorna a configuração como dicionário."""
        return dict(self.config)

    @property
    def timeout(self) -> float:
        """Timeout para requisições."""
        return float(self.config["timeout"])

    @property
    def max_retries(self) -> int:
        """Número máximo de tentativas."""
        return int(self.config["max_retries"])

    @property
    def max_tokens(self) -> int:
        """Número máximo de tokens."""
        return int(self.config["max_tokens"])

    @property
    def temperature(self) -> float:
        """Temperatura para geração."""
        return float(self.config["temperature"])


class ConfigSource(Enum):
    """Fontes de configuração disponíveis."""

    DEFAULT = "default"
    FILE = "file"
    ENVIRONMENT = "environment"
    RUNTIME = "runtime"


@dataclass
class CacheConfig:
    """Configurações do sistema de cache."""

    enabled: bool = True
    default_ttl: int = 300  # 5 minutos
    max_size: int = 1000
    cleanup_interval: int = 3600  # 1 hora
    memory_threshold_mb: float = 100.0


@dataclass
class ValidationConfig:
    """Configurações do sistema de validação."""

    enabled: bool = True
    strict_mode: bool = False
    max_text_length: int = 100000
    max_model_name_length: int = 100
    allowed_model_patterns: list[str] = field(
        default_factory=lambda: [
            r"^gpt-.*",
            r"^claude-.*",
            r"^llama-.*",
            r"^mistral-.*",
        ]
    )


@dataclass
class LoggingConfig:
    """Configurações do sistema de logging."""

    enabled: bool = True
    level: str = "INFO"
    log_dir: str = "logs"
    max_file_size_mb: int = 10
    backup_count: int = 5
    json_format: bool = True
    console_output: bool = True
    performance_logging: bool = True


@dataclass
class MetricsConfig:
    """Configuração para métricas."""

    enabled: bool = True
    collection_interval: int = 60  # segundos
    retention_days: int = 30
    export_format: str = "json"  # json, csv, prometheus
    export_interval_minutes: int = 60
    max_entries: int = 10000
    include_system_metrics: bool = True
    include_performance_metrics: bool = True


@dataclass
class CentralizedLLMConfig:
    """Configuração centralizada para todo o módulo LLM."""

    llm: LLMConfig = field(default_factory=LLMConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    metrics: MetricsConfig = field(default_factory=MetricsConfig)
    debug_mode: bool = False
    environment: str = "production"

    def __post_init__(self):
        # Ajustes automáticos baseados no ambiente
        if self.environment == "development":
            self.debug_mode = True
            self.logging.level = "DEBUG"
            self.logging.console_output = True
        elif self.environment == "testing":
            self.cache.enabled = False
            self.metrics.enabled = False
            self.logging.level = "WARNING"

    def to_dict(self) -> dict[str, Any]:
        """Converte a configuração para dicionário."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CentralizedLLMConfig":
        """Cria configuração a partir de dicionário."""
        cache_data = data.get("cache", {})
        validation_data = data.get("validation", {})
        logging_data = data.get("logging", {})
        metrics_data = data.get("metrics", {})

        return cls(
            cache=CacheConfig(**cache_data),
            validation=ValidationConfig(**validation_data),
            logging=LoggingConfig(**logging_data),
            metrics=MetricsConfig(**metrics_data),
            debug_mode=data.get("debug_mode", False),
            environment=data.get("environment", "production"),
        )


class ConfigManager:
    """Gerenciador de configuração centralizada."""

    def __init__(self):
        self._config: CentralizedLLMConfig | None = None
        self._config_sources: dict[ConfigSource, dict[str, Any]] = {}
        self._lock = threading.RLock()
        self._config_file_path: Path | None = None
        self._load_default_config()

    def _load_default_config(self) -> None:
        """Carrega configuração padrão."""
        default_config = {
            "llm": LLMConfig().to_dict(),
            "cache": asdict(CacheConfig()),
            "validation": asdict(ValidationConfig()),
            "logging": asdict(LoggingConfig()),
            "metrics": asdict(MetricsConfig()),
            "debug_mode": False,
            "environment": "production",
        }
        self._config_sources[ConfigSource.DEFAULT] = default_config
        self._rebuild_config()

    def _load_from_file(self, file_path: Path) -> dict[str, Any]:
        """Carrega configuração de arquivo."""
        if not file_path.exists():
            return {}

        try:
            with open(file_path, encoding="utf-8") as f:
                if file_path.suffix.lower() == ".json":
                    data: dict[str, Any] = json.load(f)
                    return data
                else:
                    raise ValueError(
                        f"Formato de arquivo não suportado: {file_path.suffix}"
                    )
        except Exception as e:
            raise RuntimeError(
                f"Erro ao carregar configuração de {file_path}: {e}"
            ) from e

    def _load_from_environment(self) -> dict[str, Any]:
        """Carrega configuração de variáveis de ambiente."""
        env_config = {}

        # Mapeamento de variáveis de ambiente para configuração
        env_mappings = {
            "LLM_TIMEOUT": ("llm", "timeout", float),
            "LLM_MAX_RETRIES": ("llm", "max_retries", int),
            "LLM_MAX_TOKENS": ("llm", "max_tokens", int),
            "LLM_TEMPERATURE": ("llm", "temperature", float),
            "LLM_CACHE_ENABLED": ("cache", "enabled", bool),
            "LLM_CACHE_TTL": ("cache", "default_ttl", int),
            "LLM_CACHE_MAX_SIZE": ("cache", "max_size", int),
            "LLM_VALIDATION_ENABLED": ("validation", "enabled", bool),
            "LLM_VALIDATION_STRICT": ("validation", "strict_mode", bool),
            "LLM_LOG_LEVEL": ("logging", "level", str),
            "LLM_LOG_DIR": ("logging", "log_dir", str),
            "LLM_METRICS_ENABLED": ("metrics", "enabled", bool),
            "LLM_DEBUG_MODE": ("debug_mode", None, bool),
            "LLM_ENVIRONMENT": ("environment", None, str),
        }

        for env_var, (section, key, value_type) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    # Converte o valor para o tipo apropriado
                    converted_value: Any
                    if value_type is bool:
                        converted_value = value.lower() in ("true", "1", "yes", "on")
                    elif value_type is int:
                        converted_value = int(value)
                    else:
                        converted_value = value

                    # Estrutura o dicionário de configuração
                    if key is None:
                        env_config[section] = converted_value
                    else:
                        if section not in env_config:
                            env_config[section] = {}
                        env_config[section][key] = converted_value

                except (ValueError, TypeError) as e:
                    print(f"Aviso: Valor inválido para {env_var}: {value} ({e})")

        return env_config

    def _merge_configs(self, *configs: dict[str, Any]) -> dict[str, Any]:
        """Mescla múltiplas configurações com precedência."""
        result: dict[str, Any] = {}

        for config in configs:
            for key, value in config.items():
                if (
                    isinstance(value, dict)
                    and key in result
                    and isinstance(result[key], dict)
                ):
                    result[key] = self._merge_configs(result[key], value)
                else:
                    result[key] = value

        return result

    def _rebuild_config(self) -> None:
        """Reconstrói a configuração mesclando todas as fontes."""
        # Ordem de precedência: DEFAULT < FILE < ENVIRONMENT < RUNTIME
        merged_config = self._merge_configs(
            self._config_sources.get(ConfigSource.DEFAULT, {}),
            self._config_sources.get(ConfigSource.FILE, {}),
            self._config_sources.get(ConfigSource.ENVIRONMENT, {}),
            self._config_sources.get(ConfigSource.RUNTIME, {}),
        )

        self._config = CentralizedLLMConfig.from_dict(merged_config)

    def load_from_file(self, file_path: str | Path) -> None:
        """Carrega configuração de arquivo."""
        with self._lock:
            file_path = Path(file_path)
            self._config_file_path = file_path

            try:
                file_config = self._load_from_file(file_path)
                self._config_sources[ConfigSource.FILE] = file_config
                self._rebuild_config()
            except Exception as e:
                print(f"Erro ao carregar configuração de arquivo: {e}")

    def load_from_environment(self) -> None:
        """Carrega configuração de variáveis de ambiente."""
        with self._lock:
            env_config = self._load_from_environment()
            self._config_sources[ConfigSource.ENVIRONMENT] = env_config
            self._rebuild_config()

    def update_config(self, updates: dict[str, Any]) -> None:
        """Atualiza configuração em runtime."""
        with self._lock:
            current_runtime = self._config_sources.get(ConfigSource.RUNTIME, {})
            updated_runtime = self._merge_configs(current_runtime, updates)
            self._config_sources[ConfigSource.RUNTIME] = updated_runtime
            self._rebuild_config()

    def get_config(self) -> CentralizedLLMConfig:
        """Retorna a configuração atual."""
        with self._lock:
            if self._config is None:
                self._rebuild_config()
            assert self._config is not None
            return self._config

    def reset_to_defaults(self) -> None:
        """Reseta configuração para valores padrão."""
        with self._lock:
            self._config_sources = {
                ConfigSource.DEFAULT: self._config_sources[ConfigSource.DEFAULT]
            }
            self._rebuild_config()

    def save_to_file(self, file_path: str | Path) -> None:
        """Salva configuração atual em arquivo."""
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with self._lock:
            config = self.get_config()
            config_dict = config.to_dict()

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False, default=str)

    def get_config_summary(self) -> dict[str, Any]:
        """Retorna resumo da configuração atual."""
        with self._lock:
            config = self.get_config()
            return {
                "environment": config.environment,
                "debug_mode": config.debug_mode,
                "cache_enabled": config.cache.enabled,
                "validation_enabled": config.validation.enabled,
                "logging_enabled": config.logging.enabled,
                "metrics_enabled": config.metrics.enabled,
                "config_sources": [
                    source.value for source in self._config_sources.keys()
                ],
                "config_file": str(self._config_file_path)
                if self._config_file_path
                else None,
            }


# Instância global do gerenciador de configuração
_config_manager = ConfigManager()


def get_centralized_config() -> CentralizedLLMConfig:
    """Retorna a configuração centralizada atual do módulo LLM."""
    return _config_manager.get_config()


def update_centralized_config(updates: dict[str, Any]) -> None:
    """Atualiza configuração centralizada em runtime."""
    _config_manager.update_config(updates)


def load_config_from_file(file_path: str | Path) -> None:
    """Carrega configuração de arquivo."""
    _config_manager.load_from_file(file_path)


def load_config_from_environment() -> None:
    """Carrega configuração de variáveis de ambiente."""
    _config_manager.load_from_environment()


def save_config_to_file(file_path: str | Path) -> None:
    """Salva configuração atual em arquivo."""
    _config_manager.save_to_file(file_path)


def reset_config() -> None:
    """Reseta configuração para valores padrão."""
    _config_manager.reset_to_defaults()


def get_config_summary() -> dict[str, Any]:
    """Retorna resumo da configuração atual."""
    return _config_manager.get_config_summary()


# Carrega configuração de variáveis de ambiente na inicialização
load_config_from_environment()
