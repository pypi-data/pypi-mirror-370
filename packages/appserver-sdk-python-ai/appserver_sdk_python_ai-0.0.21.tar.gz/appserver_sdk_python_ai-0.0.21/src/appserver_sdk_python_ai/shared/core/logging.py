"""Sistema de logging comum para todos os módulos do SDK."""

import logging
import sys
from types import FrameType


class SDKLogger:
    """Logger configurável para o SDK."""

    DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    SIMPLE_FORMAT = "%(levelname)s: %(message)s"
    DETAILED_FORMAT = (
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    )

    @staticmethod
    def setup_logging(
        level: int = logging.INFO,
        format_string: str | None = None,
        logger_name: str | None = None,
    ) -> logging.Logger:
        """
        Configura logging para um módulo.

        Args:
            level: Nível de logging (logging.DEBUG, INFO, WARNING, ERROR, CRITICAL)
            format_string: Formato customizado para logs
            logger_name: Nome do logger (padrão: nome do módulo chamador)

        Returns:
            Logger configurado
        """
        if format_string is None:
            format_string = SDKLogger.DEFAULT_FORMAT

        # Configurar handler se não existir
        root_logger = logging.getLogger()
        if not root_logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter(format_string))
            root_logger.addHandler(handler)
            root_logger.setLevel(level)

        # Retornar logger específico do módulo
        if logger_name:
            logger = logging.getLogger(logger_name)
        else:
            # Tentar detectar o nome do módulo chamador
            import inspect

            frame = inspect.currentframe()
            try:
                caller_frame: FrameType | None = frame.f_back if frame else None
                if caller_frame:
                    caller_module = caller_frame.f_globals.get("__name__", "sdk")
                    logger = logging.getLogger(caller_module)
                else:
                    logger = logging.getLogger("sdk")
            finally:
                del frame

        logger.setLevel(level)
        return logger

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Obtém um logger com nome específico."""
        return logging.getLogger(name)

    @staticmethod
    def set_level(level: int, logger_name: str | None = None):
        """Define o nível de logging."""
        if logger_name:
            logging.getLogger(logger_name).setLevel(level)
        else:
            logging.getLogger().setLevel(level)

    @staticmethod
    def disable_logging(logger_name: str | None = None):
        """Desabilita logging."""
        if logger_name:
            logging.getLogger(logger_name).disabled = True
        else:
            logging.disable(logging.CRITICAL)

    @staticmethod
    def enable_logging(logger_name: str | None = None):
        """Habilita logging."""
        if logger_name:
            logging.getLogger(logger_name).disabled = False
        else:
            logging.disable(logging.NOTSET)
