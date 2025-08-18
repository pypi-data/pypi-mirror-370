"""Sistema de logging estruturado para o módulo LLM.

Este módulo implementa logging estruturado com formatação JSON,
contexto de operações e métricas de performance.
"""

import json
import logging
import logging.handlers
import threading
import time
import traceback
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class LogLevel(Enum):
    """Níveis de log personalizados."""

    TRACE = 5
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class OperationType(Enum):
    """Tipos de operações para logging."""

    TOKEN_COUNT = "token_count"
    MODEL_LOAD = "model_load"
    MODEL_REGISTER = "model_register"
    CACHE_ACCESS = "cache_access"
    VALIDATION = "validation"
    API_CALL = "api_call"
    FILE_OPERATION = "file_operation"
    CONFIGURATION = "configuration"
    ERROR_HANDLING = "error_handling"


@dataclass
class LogContext:
    """Contexto de logging estruturado."""

    operation_id: str
    operation_type: OperationType
    user_id: str | None = None
    session_id: str | None = None
    model_name: str | None = None
    provider: str | None = None
    start_time: float | None = None
    metadata: dict[str, Any] | None = None

    def __post_init__(self):
        if self.start_time is None:
            self.start_time = time.time()
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionário, excluindo valores None."""
        data = asdict(self)
        return {k: v for k, v in data.items() if v is not None}


class StructuredFormatter(logging.Formatter):
    """Formatador de log estruturado em JSON."""

    def __init__(self, include_trace: bool = False):
        super().__init__()
        self.include_trace = include_trace

    def format(self, record: logging.LogRecord) -> str:
        """Formata o registro de log como JSON estruturado."""
        # Dados básicos do log
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread_id": threading.get_ident(),
            "process_id": record.process,
        }

        # Adiciona contexto se disponível
        if hasattr(record, "context") and record.context:
            if isinstance(record.context, LogContext):
                log_data["context"] = record.context.to_dict()
            else:
                log_data["context"] = record.context

        # Adiciona métricas se disponíveis
        if hasattr(record, "metrics") and record.metrics:
            log_data["metrics"] = record.metrics

        # Adiciona dados extras
        for key, _value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "getMessage",
                "context",
                "metrics",
            ]:
                if "extra" not in log_data:
                    log_data["extra"] = {}
                if hasattr(record, key) and isinstance(log_data["extra"], dict):
                    log_data["extra"][key] = getattr(record, key)

        # Adiciona stack trace para erros
        if record.exc_info and self.include_trace:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info),
            }

        return json.dumps(log_data, ensure_ascii=False, default=str)


class PerformanceFormatter(logging.Formatter):
    """Formatador focado em métricas de performance."""

    def format(self, record: logging.LogRecord) -> str:
        """Formata logs de performance."""
        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S.%f")[:-3]

        # Extrai métricas se disponíveis
        metrics = getattr(record, "metrics", {})
        context = getattr(record, "context", {})

        if isinstance(context, LogContext):
            context_str = f"[{context.operation_type.value}:{context.operation_id[:8]}]"
        else:
            context_str = "[unknown]"

        # Formata métricas principais
        metrics_str = ""
        if metrics:
            duration = metrics.get("duration_ms", 0)
            memory = metrics.get("memory_mb", 0)
            tokens = metrics.get("token_count", 0)

            parts = []
            if duration > 0:
                parts.append(f"{duration:.2f}ms")
            if memory > 0:
                parts.append(f"{memory:.2f}MB")
            if tokens > 0:
                parts.append(f"{tokens}tok")

            if parts:
                metrics_str = f" ({', '.join(parts)})"

        return f"{timestamp} {record.levelname:8} {context_str} {record.getMessage()}{metrics_str}"


class LLMLogger:
    """Logger especializado para o módulo LLM."""

    def __init__(self, name: str = "llm", level: LogLevel = LogLevel.INFO):
        self.name = name
        self.level = level
        self.logger = logging.getLogger(f"appserver_sdk.{name}")
        self.logger.setLevel(level.value)
        self._context_stack = threading.local()
        self._setup_handlers()

    def _setup_handlers(self):
        """Configura handlers de logging."""
        # Remove handlers existentes
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # Handler para console (desenvolvimento)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = PerformanceFormatter()
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # Handler para arquivo estruturado
        log_dir = Path.cwd() / "logs"
        log_dir.mkdir(exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / f"{self.name}.jsonl",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = StructuredFormatter(include_trace=True)
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Handler para erros críticos
        error_handler = logging.handlers.RotatingFileHandler(
            log_dir / f"{self.name}_errors.jsonl",
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        self.logger.addHandler(error_handler)

    def _get_context_stack(self) -> list[LogContext]:
        """Obtém a pilha de contextos da thread atual."""
        if not hasattr(self._context_stack, "stack"):
            self._context_stack.stack = []
        return list(self._context_stack.stack)

    def _get_current_context(self) -> LogContext | None:
        """Obtém o contexto atual da thread."""
        stack = self._get_context_stack()
        return stack[-1] if stack else None

    @contextmanager
    def operation_context(
        self,
        operation_type: OperationType,
        operation_id: str | None = None,
        **kwargs,
    ):
        """Context manager para operações com logging automático."""
        import uuid

        if operation_id is None:
            operation_id = str(uuid.uuid4())

        context = LogContext(
            operation_id=operation_id, operation_type=operation_type, **kwargs
        )

        stack = self._get_context_stack()
        stack.append(context)

        start_time = time.time()

        try:
            self.info(f"Iniciando operação {operation_type.value}", context=context)
            yield context

            duration = (time.time() - start_time) * 1000
            self.info(
                f"Operação {operation_type.value} concluída",
                context=context,
                metrics={"duration_ms": duration, "status": "success"},
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self.error(
                f"Operação {operation_type.value} falhou: {e}",
                context=context,
                metrics={"duration_ms": duration, "status": "error"},
                exc_info=True,
            )
            raise
        finally:
            stack.pop()

    def _log(
        self,
        level: int,
        message: str,
        context: LogContext | None = None,
        metrics: dict[str, Any] | None = None,
        **kwargs,
    ):
        """Método interno de logging."""
        if context is None:
            context = self._get_current_context()

        # Cria record personalizado
        record = self.logger.makeRecord(
            self.logger.name,
            level,
            "",
            0,
            message,
            (),
            None,
            func=kwargs.get("func"),
            extra=kwargs.get("extra"),
        )

        # Adiciona contexto e métricas
        record.context = context
        record.metrics = metrics or {}

        # Adiciona informações extras
        for key, value in kwargs.items():
            if key not in ["func", "extra", "exc_info"]:
                setattr(record, key, value)

        self.logger.handle(record)

    def trace(self, message: str, **kwargs):
        """Log de trace (nível mais baixo)."""
        self._log(LogLevel.TRACE.value, message, **kwargs)

    def debug(self, message: str, **kwargs):
        """Log de debug."""
        self._log(LogLevel.DEBUG.value, message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log de informação."""
        self._log(LogLevel.INFO.value, message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log de aviso."""
        self._log(LogLevel.WARNING.value, message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log de erro."""
        self._log(LogLevel.ERROR.value, message, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log crítico."""
        self._log(LogLevel.CRITICAL.value, message, **kwargs)

    def log_performance(
        self,
        operation: str,
        duration_ms: float,
        additional_metrics: dict[str, Any] | None = None,
    ):
        """Log específico para métricas de performance."""
        metrics = {"duration_ms": duration_ms}
        if additional_metrics:
            metrics.update(additional_metrics)

        level = LogLevel.INFO.value
        if duration_ms > 5000:  # > 5 segundos
            level = LogLevel.WARNING.value
        elif duration_ms > 10000:  # > 10 segundos
            level = LogLevel.ERROR.value

        self._log(level, f"Performance: {operation}", metrics=metrics)

    def log_token_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int = 0,
        cost_estimate: float | None = None,
    ):
        """Log específico para uso de tokens."""
        metrics: dict[str, int | float] = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
        }

        if cost_estimate is not None:
            metrics["cost_estimate_usd"] = cost_estimate

        context = LogContext(
            operation_id=f"token_usage_{int(time.time())}",
            operation_type=OperationType.TOKEN_COUNT,
            model_name=model,
        )

        self.info(f"Uso de tokens - {model}", context=context, metrics=metrics)

    def log_cache_stats(self, cache_stats: dict[str, Any]):
        """Log específico para estatísticas de cache."""
        context = LogContext(
            operation_id=f"cache_stats_{int(time.time())}",
            operation_type=OperationType.CACHE_ACCESS,
        )

        self.info("Estatísticas de cache", context=context, metrics=cache_stats)

    def log_validation_result(
        self,
        validation_type: str,
        is_valid: bool,
        errors: list[str],
        warnings: list[str],
    ):
        """Log específico para resultados de validação."""
        context = LogContext(
            operation_id=f"validation_{int(time.time())}",
            operation_type=OperationType.VALIDATION,
        )

        metrics = {
            "is_valid": is_valid,
            "error_count": len(errors),
            "warning_count": len(warnings),
        }

        level = LogLevel.ERROR.value if not is_valid else LogLevel.INFO.value
        message = f"Validação {validation_type}: {'✓' if is_valid else '✗'}"

        if errors:
            message += (
                f" (Erros: {', '.join(errors[:3])}{'...' if len(errors) > 3 else ''})"
            )

        self._log(level, message, context=context, metrics=metrics)


# Logger global para o módulo LLM
_global_logger = LLMLogger()


def get_logger(name: str | None = None) -> LLMLogger:
    """Obtém uma instância do logger LLM."""
    if name:
        return LLMLogger(name)
    return _global_logger


def configure_logging(
    level: LogLevel = LogLevel.INFO,
    log_dir: Path | None = None,
    enable_console: bool = True,
    enable_file: bool = True,
):
    """Configura o sistema de logging global."""
    global _global_logger

    # Recria o logger com nova configuração
    _global_logger = LLMLogger(level=level)

    if log_dir:
        # Atualiza diretório de logs
        log_dir.mkdir(exist_ok=True)
        # Reconfigurar handlers seria necessário aqui

    return _global_logger


# Decorador para logging automático de funções
def log_function_call(
    operation_type: OperationType = OperationType.API_CALL,
    log_args: bool = False,
    log_result: bool = False,
):
    """Decorator para logging automático de chamadas de função."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger()

            with logger.operation_context(operation_type, func.__name__) as context:
                if log_args:
                    context.metadata["args"] = str(args)[:200]  # Limita tamanho
                    context.metadata["kwargs"] = {
                        k: str(v)[:100] for k, v in kwargs.items()
                    }

                time.time()
                try:
                    result = func(*args, **kwargs)

                    if log_result and result is not None:
                        context.metadata["result_type"] = type(result).__name__
                        if hasattr(result, "__len__"):
                            context.metadata["result_size"] = len(result)

                    return result

                except Exception as e:
                    logger.error(f"Erro em {func.__name__}: {e}", exc_info=True)
                    raise

        return wrapper

    return decorator
