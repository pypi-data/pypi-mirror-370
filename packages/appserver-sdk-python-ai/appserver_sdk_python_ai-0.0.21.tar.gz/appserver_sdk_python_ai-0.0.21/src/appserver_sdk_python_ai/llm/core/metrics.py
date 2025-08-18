"""Sistema de métricas para o módulo LLM.

Este módulo fornece um sistema abrangente de coleta, armazenamento e
exportação de métricas para visibilidade de uso do módulo LLM.

Exemplo de uso:
    >>> from appserver_sdk_python_ai.llm.core.metrics import get_metrics_collector
    >>> collector = get_metrics_collector()
    >>> collector.record_operation('token_count', duration_ms=150.5)
    >>> metrics = collector.get_metrics_summary()
"""

import json
import threading
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import psutil


class MetricType(Enum):
    """Tipos de métricas disponíveis."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class OperationStatus(Enum):
    """Status de operações."""

    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class MetricEntry:
    """Entrada individual de métrica."""

    name: str
    value: float
    metric_type: MetricType
    timestamp: float
    labels: dict[str, str]
    operation_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionário."""
        return {
            "name": self.name,
            "value": self.value,
            "type": self.metric_type.value,
            "timestamp": self.timestamp,
            "labels": self.labels,
            "operation_id": self.operation_id,
        }


@dataclass
class OperationMetrics:
    """Métricas de uma operação específica."""

    operation_type: str
    operation_id: str
    start_time: float
    end_time: float | None = None
    status: OperationStatus = OperationStatus.SUCCESS
    duration_ms: float | None = None
    memory_usage_mb: float | None = None
    token_count: int | None = None
    model_name: str | None = None
    provider: str | None = None
    cache_hit: bool | None = None
    error_message: str | None = None
    metadata: dict[str, Any] | None = None

    def __post_init__(self):
        if self.end_time and self.duration_ms is None:
            self.duration_ms = (self.end_time - self.start_time) * 1000

    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionário."""
        return asdict(self)


class SystemMetrics:
    """Coleta métricas do sistema."""

    @staticmethod
    def get_memory_usage() -> dict[str, float]:
        """Retorna uso de memória do processo atual."""
        process = psutil.Process()
        memory_info = process.memory_info()

        return {
            "rss_mb": memory_info.rss / 1024 / 1024,
            "vms_mb": memory_info.vms / 1024 / 1024,
            "percent": process.memory_percent(),
        }

    @staticmethod
    def get_cpu_usage() -> dict[str, float]:
        """Retorna uso de CPU."""
        return {
            "percent": psutil.cpu_percent(interval=0.1),
            "count": psutil.cpu_count(),
        }

    @staticmethod
    def get_disk_usage(path: str = ".") -> dict[str, float]:
        """Retorna uso de disco."""
        usage = psutil.disk_usage(path)

        return {
            "total_gb": usage.total / 1024 / 1024 / 1024,
            "used_gb": usage.used / 1024 / 1024 / 1024,
            "free_gb": usage.free / 1024 / 1024 / 1024,
            "percent": (usage.used / usage.total) * 100,
        }


class MetricsCollector:
    """Coletor principal de métricas."""

    def __init__(self, retention_days: int = 30, max_entries: int = 10000):
        self.retention_days = retention_days
        self.max_entries = max_entries
        self._metrics: deque[MetricEntry] = deque(maxlen=max_entries)
        self._operations: dict[str, OperationMetrics] = {}
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._lock = threading.RLock()
        self._start_time = time.time()

        # Estatísticas agregadas
        self._operation_stats: dict[str, dict[str, float]] = defaultdict(
            lambda: {
                "count": 0,
                "total_duration_ms": 0,
                "success_count": 0,
                "error_count": 0,
                "avg_duration_ms": 0,
            }
        )

    def record_metric(
        self,
        name: str,
        value: float,
        metric_type: MetricType,
        labels: dict[str, str] | None = None,
        operation_id: str | None = None,
    ) -> None:
        """Registra uma métrica."""
        with self._lock:
            labels = labels or {}
            timestamp = time.time()

            entry = MetricEntry(
                name=name,
                value=value,
                metric_type=metric_type,
                timestamp=timestamp,
                labels=labels,
                operation_id=operation_id,
            )

            self._metrics.append(entry)

            # Atualiza agregações
            if metric_type == MetricType.COUNTER:
                self._counters[name] += value
            elif metric_type == MetricType.GAUGE:
                self._gauges[name] = value
            elif metric_type == MetricType.HISTOGRAM:
                self._histograms[name].append(value)

            # Limpa dados antigos
            self._cleanup_old_metrics()

    def start_operation(
        self,
        operation_type: str,
        operation_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> OperationMetrics:
        """Inicia o rastreamento de uma operação."""
        with self._lock:
            operation = OperationMetrics(
                operation_type=operation_type,
                operation_id=operation_id,
                start_time=time.time(),
                metadata=metadata or {},
            )

            self._operations[operation_id] = operation
            return operation

    def end_operation(
        self,
        operation_id: str,
        status: OperationStatus = OperationStatus.SUCCESS,
        error_message: str | None = None,
        additional_metrics: dict[str, Any] | None = None,
    ) -> OperationMetrics | None:
        """Finaliza o rastreamento de uma operação."""
        with self._lock:
            if operation_id not in self._operations:
                return None

            operation = self._operations[operation_id]
            operation.end_time = time.time()
            operation.status = status
            operation.error_message = error_message

            if additional_metrics:
                for key, value in additional_metrics.items():
                    if hasattr(operation, key):
                        setattr(operation, key, value)

            # Atualiza estatísticas agregadas
            stats = self._operation_stats[operation.operation_type]
            stats["count"] += 1

            if operation.duration_ms:
                stats["total_duration_ms"] += float(operation.duration_ms)
                stats["avg_duration_ms"] = stats["total_duration_ms"] / stats["count"]

            if status == OperationStatus.SUCCESS:
                stats["success_count"] += 1
            else:
                stats["error_count"] += 1

            # Registra métricas da operação
            if operation.duration_ms:
                self.record_metric(
                    "operation_duration_ms",
                    operation.duration_ms,
                    MetricType.HISTOGRAM,
                    labels={
                        "operation_type": operation.operation_type,
                        "status": status.value,
                    },
                    operation_id=operation_id,
                )

            # Remove da lista de operações ativas
            del self._operations[operation_id]

            return operation

    def record_operation(
        self,
        operation_type: str,
        duration_ms: float,
        status: OperationStatus = OperationStatus.SUCCESS,
        **kwargs,
    ) -> None:
        """Registra uma operação completa."""
        operation_id = f"{operation_type}_{int(time.time() * 1000)}"

        operation = self.start_operation(operation_type, operation_id, kwargs)
        operation.duration_ms = duration_ms
        self.end_operation(operation_id, status, additional_metrics=kwargs)

    def increment_counter(
        self, name: str, value: float = 1.0, labels: dict[str, str] | None = None
    ) -> None:
        """Incrementa um contador."""
        self.record_metric(name, value, MetricType.COUNTER, labels)

    def set_gauge(
        self, name: str, value: float, labels: dict[str, str] | None = None
    ) -> None:
        """Define o valor de um gauge."""
        self.record_metric(name, value, MetricType.GAUGE, labels)

    def record_histogram(
        self, name: str, value: float, labels: dict[str, str] | None = None
    ) -> None:
        """Registra um valor em histograma."""
        self.record_metric(name, value, MetricType.HISTOGRAM, labels)

    def record_timer(
        self, name: str, duration_ms: float, labels: dict[str, str] | None = None
    ) -> None:
        """Registra um tempo de execução."""
        self.record_metric(name, duration_ms, MetricType.TIMER, labels)

    def get_counter(self, name: str) -> float:
        """Retorna o valor atual de um contador."""
        with self._lock:
            return self._counters.get(name, 0.0)

    def get_gauge(self, name: str) -> float | None:
        """Retorna o valor atual de um gauge."""
        with self._lock:
            return self._gauges.get(name)

    def get_histogram_stats(self, name: str) -> dict[str, float]:
        """Retorna estatísticas de um histograma."""
        with self._lock:
            values = self._histograms.get(name, [])
            if not values:
                return {}

            sorted_values = sorted(values)
            count = len(sorted_values)

            return {
                "count": count,
                "min": min(sorted_values),
                "max": max(sorted_values),
                "mean": sum(sorted_values) / count,
                "p50": sorted_values[int(count * 0.5)],
                "p90": sorted_values[int(count * 0.9)],
                "p95": sorted_values[int(count * 0.95)],
                "p99": sorted_values[int(count * 0.99)]
                if count > 1
                else sorted_values[0],
            }

    def get_active_operations(self) -> list[OperationMetrics]:
        """Retorna operações ativas."""
        with self._lock:
            return list(self._operations.values())

    def get_operation_stats(self) -> dict[str, dict[str, Any]]:
        """Retorna estatísticas agregadas por tipo de operação."""
        with self._lock:
            return dict(self._operation_stats)

    def get_system_metrics(self) -> dict[str, Any]:
        """Retorna métricas do sistema."""
        return {
            "memory": SystemMetrics.get_memory_usage(),
            "cpu": SystemMetrics.get_cpu_usage(),
            "disk": SystemMetrics.get_disk_usage(),
            "uptime_seconds": time.time() - self._start_time,
        }

    def get_metrics_summary(self, include_system: bool = True) -> dict[str, Any]:
        """Retorna resumo completo das métricas."""
        with self._lock:
            summary = {
                "timestamp": datetime.now().isoformat(),
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    name: self.get_histogram_stats(name)
                    for name in self._histograms.keys()
                },
                "operation_stats": self.get_operation_stats(),
                "active_operations": len(self._operations),
                "total_metrics": len(self._metrics),
            }

            if include_system:
                summary["system"] = self.get_system_metrics()

            return summary

    def export_metrics(
        self, format_type: str = "json", file_path: str | None = None
    ) -> str | None:
        """Exporta métricas em formato especificado."""
        summary = self.get_metrics_summary()

        if format_type.lower() == "json":
            data = json.dumps(summary, indent=2, ensure_ascii=False)
        elif format_type.lower() == "csv":
            # Converte para formato CSV simplificado
            data = self._to_csv(summary)
        elif format_type.lower() == "prometheus":
            data = self._to_prometheus(summary)
        else:
            raise ValueError(f"Formato não suportado: {format_type}")

        if file_path:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(data)
            return None

        return data

    def _to_csv(self, summary: dict[str, Any]) -> str:
        """Converte métricas para formato CSV."""
        lines = []
        lines.append("metric_type,name,value,timestamp")

        # Contadores
        for name, value in summary["counters"].items():
            lines.append(f"counter,{name},{value},{summary['timestamp']}")

        # Gauges
        for name, value in summary["gauges"].items():
            lines.append(f"gauge,{name},{value},{summary['timestamp']}")

        return "\n".join(lines)

    def _to_prometheus(self, summary: dict[str, Any]) -> str:
        """Converte métricas para formato Prometheus."""
        lines = []

        # Contadores
        for name, value in summary["counters"].items():
            lines.append(f"# TYPE {name} counter")
            lines.append(f"{name} {value}")

        # Gauges
        for name, value in summary["gauges"].items():
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name} {value}")

        return "\n".join(lines)

    def _cleanup_old_metrics(self) -> None:
        """Remove métricas antigas baseado na retenção configurada."""
        if self.retention_days <= 0:
            return

        cutoff_time = time.time() - (self.retention_days * 24 * 3600)

        # Remove métricas antigas
        while self._metrics and self._metrics[0].timestamp < cutoff_time:
            self._metrics.popleft()

        # Limpa histogramas muito grandes
        for name, values in self._histograms.items():
            if len(values) > 1000:  # Mantém apenas os últimos 1000 valores
                self._histograms[name] = values[-1000:]

    def clear_metrics(self) -> None:
        """Limpa todas as métricas."""
        with self._lock:
            self._metrics.clear()
            self._operations.clear()
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            self._operation_stats.clear()


# Instância global do coletor de métricas
_metrics_collector: MetricsCollector | None = None
_metrics_lock = threading.Lock()


def get_metrics_collector() -> MetricsCollector:
    """Retorna a instância global do coletor de métricas."""
    global _metrics_collector

    if _metrics_collector is None:
        with _metrics_lock:
            if _metrics_collector is None:
                _metrics_collector = MetricsCollector()

    return _metrics_collector


def record_operation_metric(
    operation_type: str,
    duration_ms: float,
    status: OperationStatus = OperationStatus.SUCCESS,
    **kwargs,
) -> None:
    """Função utilitária para registrar métricas de operação."""
    collector = get_metrics_collector()
    collector.record_operation(operation_type, duration_ms, status, **kwargs)


def increment_counter(
    name: str, value: float = 1.0, labels: dict[str, str] | None = None
) -> None:
    """Função utilitária para incrementar contador."""
    collector = get_metrics_collector()
    collector.increment_counter(name, value, labels)


def set_gauge(name: str, value: float, labels: dict[str, str] | None = None) -> None:
    """Função utilitária para definir gauge."""
    collector = get_metrics_collector()
    collector.set_gauge(name, value, labels)


def get_metrics_summary(include_system: bool = True) -> dict[str, Any]:
    """Função utilitária para obter resumo das métricas."""
    collector = get_metrics_collector()
    return collector.get_metrics_summary(include_system)


def export_metrics(
    format_type: str = "json", file_path: str | None = None
) -> str | None:
    """Função utilitária para exportar métricas."""
    collector = get_metrics_collector()
    return collector.export_metrics(format_type, file_path)
