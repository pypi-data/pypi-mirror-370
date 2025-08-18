"""Configurações base comuns para todos os módulos do SDK."""

import os
from dataclasses import dataclass, field
from typing import Any


@dataclass
class BaseConfig:
    """Configuração base para todos os módulos."""

    # Configurações de logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Configurações de timeout
    default_timeout: int = 30

    # Configurações de retry
    max_retries: int = 3
    retry_delay: float = 1.0

    # Configurações de cache
    enable_cache: bool = True
    cache_ttl: int = 3600  # 1 hora

    # User agent padrão
    user_agent: str = "AppServer-SDK-Python-AI/1.0.0"

    # Headers padrão
    default_headers: dict[str, str] = field(
        default_factory=lambda: {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
    )

    def __post_init__(self):
        """Pós-processamento após inicialização."""
        # Adicionar User-Agent aos headers se não existir
        if "User-Agent" not in self.default_headers:
            self.default_headers["User-Agent"] = self.user_agent

    @classmethod
    def from_env(cls, prefix: str = "SDK") -> "BaseConfig":
        """
        Cria configuração a partir de variáveis de ambiente.

        Args:
            prefix: Prefixo para as variáveis de ambiente

        Returns:
            Instância de configuração
        """
        config = cls()

        # Mapear variáveis de ambiente
        env_mappings = {
            f"{prefix}_LOG_LEVEL": "log_level",
            f"{prefix}_LOG_FORMAT": "log_format",
            f"{prefix}_DEFAULT_TIMEOUT": "default_timeout",
            f"{prefix}_MAX_RETRIES": "max_retries",
            f"{prefix}_RETRY_DELAY": "retry_delay",
            f"{prefix}_ENABLE_CACHE": "enable_cache",
            f"{prefix}_CACHE_TTL": "cache_ttl",
            f"{prefix}_USER_AGENT": "user_agent",
        }

        for env_var, attr_name in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # Converter tipos apropriados
                if attr_name in ["default_timeout", "max_retries", "cache_ttl"]:
                    setattr(config, attr_name, int(env_value))
                elif attr_name == "retry_delay":
                    setattr(config, attr_name, float(env_value))
                elif attr_name == "enable_cache":
                    setattr(
                        config, attr_name, env_value.lower() in ["true", "1", "yes"]
                    )
                else:
                    setattr(config, attr_name, env_value)

        return config

    def to_dict(self) -> dict[str, Any]:
        """Converte configuração para dicionário."""
        return {
            "log_level": self.log_level,
            "log_format": self.log_format,
            "default_timeout": self.default_timeout,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "enable_cache": self.enable_cache,
            "cache_ttl": self.cache_ttl,
            "user_agent": self.user_agent,
            "default_headers": self.default_headers.copy(),
        }

    def update(self, **kwargs):
        """Atualiza configuração com novos valores."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Configuração '{key}' não é válida")


class ConfigManager:
    """Gerenciador de configurações global."""

    _instances: dict[str, BaseConfig] = {}

    @classmethod
    def get_config(cls, module_name: str, config_class=BaseConfig) -> BaseConfig:
        """
        Obtém ou cria configuração para um módulo.

        Args:
            module_name: Nome do módulo
            config_class: Classe de configuração a usar

        Returns:
            Instância de configuração
        """
        if module_name not in cls._instances:
            cls._instances[module_name] = config_class.from_env(module_name.upper())
        return cls._instances[module_name]

    @classmethod
    def set_config(cls, module_name: str, config: BaseConfig):
        """Define configuração para um módulo."""
        cls._instances[module_name] = config

    @classmethod
    def reset_config(cls, module_name: str | None = None):
        """Reseta configuração(ões)."""
        if module_name:
            cls._instances.pop(module_name, None)
        else:
            cls._instances.clear()
