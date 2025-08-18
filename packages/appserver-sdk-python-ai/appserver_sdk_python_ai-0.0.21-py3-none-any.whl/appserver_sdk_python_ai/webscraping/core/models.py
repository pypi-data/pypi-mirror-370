# appserver_sdk_python_ai/webscraping/core/models.py
"""
Modelos de dados para o módulo de webscraping.
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any


class ScrapingStatus(Enum):
    """Status do scraping."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    CACHED = "cached"
    RATE_LIMITED = "rate_limited"


@dataclass
class ScrapingResult:
    """Resultado de uma operação de scraping."""

    url: str
    title: str
    content: str
    metadata: dict[str, Any]
    success: bool
    status: ScrapingStatus = ScrapingStatus.SUCCESS
    error: str | None = None
    processing_time: float = 0.0
    content_length: int = 0
    timestamp: str | None = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

        if self.content_length == 0 and self.content:
            self.content_length = len(self.content)

        if not self.success and self.status == ScrapingStatus.SUCCESS:
            self.status = ScrapingStatus.FAILED

    def to_dict(self) -> dict[str, Any]:
        """Converte o resultado para dicionário."""
        result_dict = asdict(self)
        result_dict["status"] = self.status.value
        return result_dict

    def to_json(self) -> str:
        """Converte o resultado para JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def save_to_file(self, filepath: str, format: str = "json"):
        """
        Salva o resultado em arquivo.

        Args:
            filepath: Caminho do arquivo
            format: Formato ('json' ou 'content')
        """
        if format == "json":
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(self.to_json())
        elif format == "content":
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(self.content)
        else:
            raise ValueError("Formato deve ser 'json' ou 'content'")


@dataclass
class BatchScrapingResult:
    """Resultado de scraping em lote."""

    results: list[ScrapingResult]
    total_urls: int
    successful: int
    failed: int
    start_time: str
    end_time: str
    total_processing_time: float

    def __post_init__(self):
        if not hasattr(self, "failed"):
            self.failed = self.total_urls - self.successful

    @property
    def success_rate(self) -> float:
        """Taxa de sucesso em porcentagem."""
        if self.total_urls == 0:
            return 0.0
        return (self.successful / self.total_urls) * 100

    @property
    def average_processing_time(self) -> float:
        """Tempo médio de processamento por URL."""
        if self.total_urls == 0:
            return 0.0
        return self.total_processing_time / self.total_urls

    def get_failed_results(self) -> list[ScrapingResult]:
        """Retorna apenas os resultados que falharam."""
        return [r for r in self.results if not r.success]

    def get_successful_results(self) -> list[ScrapingResult]:
        """Retorna apenas os resultados bem-sucedidos."""
        return [r for r in self.results if r.success]

    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionário."""
        return {
            "total_urls": self.total_urls,
            "successful": self.successful,
            "failed": self.failed,
            "success_rate": self.success_rate,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "total_processing_time": self.total_processing_time,
            "average_processing_time": self.average_processing_time,
            "results": [r.to_dict() for r in self.results],
        }

    def to_json(self) -> str:
        """Converte para JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def save_summary(self, filepath: str):
        """Salva resumo em arquivo."""
        summary = {
            "total_urls": self.total_urls,
            "successful": self.successful,
            "failed": self.failed,
            "success_rate": f"{self.success_rate:.2f}%",
            "start_time": self.start_time,
            "end_time": self.end_time,
            "total_processing_time": f"{self.total_processing_time:.2f}s",
            "average_processing_time": f"{self.average_processing_time:.2f}s",
            "failed_urls": [r.url for r in self.get_failed_results()],
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)


@dataclass
class WebPageMetadata:
    """Metadados extraídos de uma página web."""

    url: str
    title: str | None = None
    description: str | None = None
    author: str | None = None
    keywords: list[str] | None = None
    language: str | None = None
    published_date: str | None = None
    modified_date: str | None = None
    canonical_url: str | None = None

    # Métricas de conteúdo
    word_count: int = 0
    char_count: int = 0
    reading_time: int = 0  # em minutos

    # Open Graph / Twitter Card
    og_title: str | None = None
    og_description: str | None = None
    og_image: str | None = None
    og_type: str | None = None

    # Dados técnicos
    content_type: str | None = None
    charset: str | None = None
    status_code: int = 200
    response_time: float = 0.0

    def calculate_reading_time(self, words_per_minute: int = 200) -> int:
        """Calcula tempo de leitura estimado."""
        if self.word_count == 0:
            return 0
        return max(1, round(self.word_count / words_per_minute))

    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionário."""
        return asdict(self)


@dataclass
class CacheEntry:
    """Entrada do cache."""

    url: str
    content: str
    timestamp: str
    headers: dict[str, str]
    metadata: dict[str, Any] | None = None
    ttl: int = 3600

    def is_expired(self) -> bool:
        """Verifica se a entrada do cache expirou."""
        try:
            cache_time = datetime.fromisoformat(self.timestamp)
            return datetime.now() - cache_time > timedelta(seconds=self.ttl)
        except Exception:
            return True

    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionário."""
        return asdict(self)

    def to_json(self) -> str:
        """Converte para JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
