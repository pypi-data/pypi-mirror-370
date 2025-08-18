"""Sistema de gerenciamento de engines/provedores unificado."""

import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from enum import Enum
from typing import Any

from appserver_sdk_python_ai.shared.exceptions import SharedError

logger = logging.getLogger(__name__)


class EngineError(SharedError):
    """Exceção para erros de engine."""

    pass


class EngineNotFoundError(EngineError):
    """Exceção quando engine não é encontrada."""

    pass


class EngineInitializationError(EngineError):
    """Exceção para erros de inicialização de engine."""

    pass


class EngineStatus(Enum):
    """Status de uma engine."""

    UNKNOWN = "unknown"
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    INITIALIZING = "initializing"
    READY = "ready"
    ERROR = "error"


class BaseEngine(ABC):
    """Interface base para engines."""

    def __init__(self, name: str, config: dict[str, Any] | None = None):
        self.name = name
        self.config = config or {}
        self._status = EngineStatus.UNKNOWN
        self._error_message: str | None = None
        self._initialized = False

    @property
    def status(self) -> EngineStatus:
        """Status atual da engine."""
        return self._status

    @property
    def error_message(self) -> str | None:
        """Mensagem de erro se houver."""
        return self._error_message

    @property
    def is_ready(self) -> bool:
        """Verifica se a engine está pronta para uso."""
        return self._status == EngineStatus.READY

    @property
    def is_available(self) -> bool:
        """Verifica se a engine está disponível."""
        return self._status in [EngineStatus.AVAILABLE, EngineStatus.READY]

    @abstractmethod
    def check_availability(self) -> bool:
        """Verifica se a engine está disponível no sistema."""
        pass

    @abstractmethod
    def initialize(self) -> None:
        """Inicializa a engine."""
        pass

    @abstractmethod
    def get_version(self) -> str | None:
        """Retorna versão da engine."""
        pass

    @abstractmethod
    def get_capabilities(self) -> list[str]:
        """Retorna lista de capacidades da engine."""
        pass

    @abstractmethod
    def validate_config(self) -> None:
        """Valida configuração da engine."""
        pass

    def setup(self) -> None:
        """Configura a engine (verifica disponibilidade e inicializa)."""
        try:
            self._status = EngineStatus.INITIALIZING
            self._error_message = None

            # Validar configuração
            self.validate_config()

            # Verificar disponibilidade
            if not self.check_availability():
                self._status = EngineStatus.UNAVAILABLE
                self._error_message = f"Engine {self.name} não está disponível"
                return

            self._status = EngineStatus.AVAILABLE

            # Inicializar
            self.initialize()

            self._status = EngineStatus.READY
            self._initialized = True

            logger.info(f"Engine {self.name} inicializada com sucesso")

        except Exception as e:
            self._status = EngineStatus.ERROR
            self._error_message = str(e)
            logger.error(f"Erro ao inicializar engine {self.name}: {e}")
            raise EngineInitializationError(
                f"Falha ao inicializar {self.name}: {e}"
            ) from e

    def reset(self) -> None:
        """Reseta a engine."""
        self._status = EngineStatus.UNKNOWN
        self._error_message = None
        self._initialized = False

    def get_info(self) -> dict[str, Any]:
        """Retorna informações da engine."""
        return {
            "name": self.name,
            "status": self.status.value,
            "version": self.get_version(),
            "capabilities": self.get_capabilities(),
            "error_message": self.error_message,
            "is_ready": self.is_ready,
            "config": self.config,
        }


class EngineRegistry:
    """Registro de engines disponíveis."""

    def __init__(self) -> None:
        self._engines: dict[str, type[BaseEngine]] = {}
        self._instances: dict[str, BaseEngine] = {}
        self._default_engine: str | None = None

    def register(self, engine_class: type[BaseEngine], name: str | None = None) -> None:
        """Registra uma classe de engine."""
        engine_name = name or engine_class.__name__.lower().replace("engine", "")
        self._engines[engine_name] = engine_class
        logger.debug(f"Engine {engine_name} registrada")

    def unregister(self, name: str) -> None:
        """Remove engine do registro."""
        if name in self._engines:
            del self._engines[name]

        if name in self._instances:
            del self._instances[name]

        if self._default_engine == name:
            self._default_engine = None

        logger.debug(f"Engine {name} removida do registro")

    def get_available_engines(self) -> list[str]:
        """Retorna lista de engines registradas."""
        return list(self._engines.keys())

    def is_registered(self, name: str) -> bool:
        """Verifica se engine está registrada."""
        return name in self._engines

    def create_engine(
        self, name: str, config: dict[str, Any] | None = None
    ) -> BaseEngine:
        """Cria instância de engine."""
        if name not in self._engines:
            raise EngineNotFoundError(f"Engine '{name}' não está registrada")

        engine_class = self._engines[name]
        return engine_class(name, config)

    def get_engine(
        self,
        name: str,
        config: dict[str, Any] | None = None,
        force_recreate: bool = False,
    ) -> BaseEngine:
        """Obtém instância de engine (singleton por nome)."""
        if force_recreate or name not in self._instances:
            self._instances[name] = self.create_engine(name, config)

        return self._instances[name]

    def set_default_engine(self, name: str) -> None:
        """Define engine padrão."""
        if not self.is_registered(name):
            raise EngineNotFoundError(f"Engine '{name}' não está registrada")

        self._default_engine = name
        logger.info(f"Engine padrão definida como: {name}")

    def get_default_engine(self) -> BaseEngine | None:
        """Retorna engine padrão."""
        if not self._default_engine:
            return None

        return self.get_engine(self._default_engine)

    def get_engine_info(self, name: str) -> dict[str, Any]:
        """Retorna informações de uma engine."""
        if name not in self._engines:
            raise EngineNotFoundError(f"Engine '{name}' não está registrada")

        # Se já tiver instância, retorna info dela
        if name in self._instances:
            return self._instances[name].get_info()

        # Senão, cria instância temporária para obter info
        temp_engine = self.create_engine(name)
        try:
            temp_engine.setup()
        except Exception:
            pass  # Ignora erros para obter info básica

        return temp_engine.get_info()

    def get_all_engines_info(self) -> dict[str, dict[str, Any]]:
        """Retorna informações de todas as engines."""
        info = {}
        for name in self._engines:
            try:
                info[name] = self.get_engine_info(name)
            except Exception as e:
                info[name] = {
                    "name": name,
                    "status": EngineStatus.ERROR.value,
                    "error_message": str(e),
                }
        return info

    def check_engines_availability(self) -> dict[str, bool]:
        """Verifica disponibilidade de todas as engines."""
        availability = {}
        for name in self._engines:
            try:
                engine = self.create_engine(name)
                availability[name] = engine.check_availability()
            except Exception:
                availability[name] = False
        return availability

    def initialize_all_engines(
        self, configs: dict[str, dict[str, Any]] | None = None
    ) -> dict[str, bool]:
        """Inicializa todas as engines disponíveis."""
        configs = configs or {}
        results = {}

        for name in self._engines:
            try:
                config = configs.get(name, {})
                engine = self.get_engine(name, config, force_recreate=True)
                engine.setup()
                results[name] = True
                logger.info(f"Engine {name} inicializada com sucesso")
            except Exception as e:
                results[name] = False
                logger.error(f"Falha ao inicializar engine {name}: {e}")

        return results


class EngineManager:
    """Gerenciador de engines com seleção automática."""

    def __init__(self, registry: EngineRegistry | None = None) -> None:
        self.registry = registry or EngineRegistry()
        self._preferred_engines: list[str] = []
        self._fallback_enabled = True

    def set_preferred_engines(self, engines: list[str]) -> None:
        """Define ordem de preferência das engines."""
        # Validar se engines estão registradas
        for engine in engines:
            if not self.registry.is_registered(engine):
                raise EngineNotFoundError(f"Engine '{engine}' não está registrada")

        self._preferred_engines = engines
        logger.info(f"Ordem de preferência definida: {engines}")

    def enable_fallback(self, enabled: bool = True) -> None:
        """Habilita/desabilita fallback automático."""
        self._fallback_enabled = enabled

    def get_best_engine(
        self,
        capabilities: list[str] | None = None,
        config: dict[str, Any] | None = None,
    ) -> BaseEngine:
        """Retorna a melhor engine disponível."""
        # Tentar engines preferidas primeiro
        for engine_name in self._preferred_engines:
            try:
                engine = self.registry.get_engine(engine_name, config)

                if not engine.is_ready:
                    engine.setup()

                # Verificar capacidades se especificadas
                if capabilities:
                    engine_capabilities = engine.get_capabilities()
                    if not all(cap in engine_capabilities for cap in capabilities):
                        continue

                logger.info(f"Usando engine preferida: {engine_name}")
                return engine

            except Exception as e:
                logger.warning(f"Engine preferida {engine_name} falhou: {e}")
                continue

        # Se fallback estiver habilitado, tentar outras engines
        if self._fallback_enabled:
            available_engines = self.registry.get_available_engines()

            for engine_name in available_engines:
                if engine_name in self._preferred_engines:
                    continue  # Já tentou

                try:
                    engine = self.registry.get_engine(engine_name, config)

                    if not engine.is_ready:
                        engine.setup()

                    # Verificar capacidades se especificadas
                    if capabilities:
                        engine_capabilities = engine.get_capabilities()
                        if not all(cap in engine_capabilities for cap in capabilities):
                            continue

                    logger.info(f"Usando engine de fallback: {engine_name}")
                    return engine

                except Exception as e:
                    logger.warning(f"Engine de fallback {engine_name} falhou: {e}")
                    continue

        # Nenhuma engine disponível
        raise EngineError("Nenhuma engine disponível")

    def execute_with_fallback(
        self,
        operation: Callable[[BaseEngine], Any],
        capabilities: list[str] | None = None,
        config: dict[str, Any] | None = None,
    ) -> Any:
        """Executa operação com fallback automático entre engines."""
        last_exception = None

        # Lista de engines para tentar
        engines_to_try = self._preferred_engines.copy()

        if self._fallback_enabled:
            all_engines = self.registry.get_available_engines()
            for engine_name_fallback in all_engines:
                if engine_name_fallback not in engines_to_try:
                    engines_to_try.append(engine_name_fallback)

        for engine_name in engines_to_try:
            try:
                engine = self.registry.get_engine(engine_name, config)

                if not engine.is_ready:
                    engine.setup()

                # Verificar capacidades se especificadas
                if capabilities:
                    engine_capabilities = engine.get_capabilities()
                    if not all(cap in engine_capabilities for cap in capabilities):
                        continue

                # Executar operação
                result = operation(engine)
                logger.info(f"Operação executada com sucesso usando {engine_name}")
                return result

            except Exception as e:
                last_exception = e
                logger.warning(f"Operação falhou com engine {engine_name}: {e}")
                continue

        # Se chegou aqui, todas as engines falharam
        raise EngineError(
            f"Operação falhou em todas as engines. Último erro: {last_exception}"
        ) from last_exception

    def get_status_report(self) -> dict[str, Any]:
        """Retorna relatório de status das engines."""
        return {
            "preferred_engines": self._preferred_engines,
            "fallback_enabled": self._fallback_enabled,
            "engines_info": self.registry.get_all_engines_info(),
            "availability": self.registry.check_engines_availability(),
        }


# Instância global padrão
default_engine_registry = EngineRegistry()
default_engine_manager = EngineManager(default_engine_registry)
