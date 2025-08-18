# appserver_sdk_python_ai/webscraping/utils/cache.py
"""
Sistema de cache para operações de web scraping.
"""

import hashlib
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from appserver_sdk_python_ai.webscraping.core.models import CacheEntry
from appserver_sdk_python_ai.webscraping.exceptions import CacheError

logger = logging.getLogger(__name__)


class CacheManager:
    """Gerenciador de cache para requisições de web scraping."""

    def __init__(self, cache_dir: str = ".webscraping_cache", max_size_mb: int = 100):
        """
        Inicializa o gerenciador de cache.

        Args:
            cache_dir: Diretório para armazenar cache
            max_size_mb: Tamanho máximo do cache em MB
        """
        self.cache_dir = Path(cache_dir)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.cache_dir.mkdir(exist_ok=True)

        # Arquivo de índice do cache
        self.index_file = self.cache_dir / "cache_index.json"
        self._load_index()

    def _load_index(self):
        """Carrega o índice do cache."""
        try:
            if self.index_file.exists():
                with open(self.index_file, encoding="utf-8") as f:
                    self._index = json.load(f)
            else:
                self._index = {}
        except Exception as e:
            logger.warning(f"Erro ao carregar índice do cache: {e}")
            self._index = {}

    def _save_index(self):
        """Salva o índice do cache."""
        try:
            with open(self.index_file, "w", encoding="utf-8") as f:
                json.dump(self._index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar índice do cache: {e}")

    def _get_cache_key(self, url: str, headers: dict[str, str]) -> str:
        """
        Gera chave de cache baseada na URL e headers relevantes.

        Args:
            url: URL da requisição
            headers: Headers da requisição

        Returns:
            str: Chave de cache
        """
        # Headers relevantes para cache (excluir headers voláteis)
        relevant_headers = {
            k: v
            for k, v in headers.items()
            if k.lower()
            not in ["user-agent", "accept-encoding", "connection", "cache-control"]
        }

        cache_string = f"{url}_{json.dumps(sorted(relevant_headers.items()))}"
        return hashlib.sha256(cache_string.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Retorna o caminho do arquivo de cache."""
        return self.cache_dir / f"{cache_key}.json"

    def get(self, url: str, headers: dict[str, str], ttl: int) -> str | None:
        """
        Recupera conteúdo do cache se válido.

        Args:
            url: URL da requisição
            headers: Headers da requisição
            ttl: Time-to-live em segundos

        Returns:
            Optional[str]: Conteúdo em cache ou None se não encontrado/expirado
        """
        try:
            cache_key = self._get_cache_key(url, headers)
            cache_path = self._get_cache_path(cache_key)

            if not cache_path.exists():
                return None

            # Carregar entrada do cache
            with open(cache_path, encoding="utf-8") as f:
                cache_data = json.load(f)

            cache_entry = CacheEntry(**cache_data)
            cache_entry.ttl = ttl  # Usar TTL atual

            # Verificar se expirou
            if cache_entry.is_expired():
                logger.debug(f"Cache expirado para {url}")
                self._remove_cache_entry(cache_key)
                return None

            # Atualizar estatísticas
            self._update_access_time(cache_key)

            logger.info(f"Cache hit para: {url}")
            return cache_entry.content

        except Exception as e:
            logger.warning(f"Erro ao recuperar cache para {url}: {e}")
            return None

    def set(
        self,
        url: str,
        headers: dict[str, str],
        content: str,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Armazena conteúdo no cache.

        Args:
            url: URL da requisição
            headers: Headers da requisição
            content: Conteúdo a ser cacheado
            metadata: Metadados adicionais
        """
        try:
            cache_key = self._get_cache_key(url, headers)
            cache_path = self._get_cache_path(cache_key)

            # Criar entrada do cache
            cache_entry = CacheEntry(
                url=url,
                content=content,
                timestamp=datetime.now().isoformat(),
                headers=headers,
                metadata=metadata or {},
            )

            # Salvar no disco
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(cache_entry.to_dict(), f, ensure_ascii=False, indent=2)

            # Atualizar índice
            self._index[cache_key] = {
                "url": url,
                "timestamp": cache_entry.timestamp,
                "size": len(content),
                "last_access": cache_entry.timestamp,
            }

            self._save_index()

            # Verificar limite de tamanho
            self._cleanup_if_needed()

            logger.debug(f"Cache armazenado para: {url}")

        except Exception as e:
            logger.error(f"Erro ao armazenar cache para {url}: {e}")
            raise CacheError(f"Falha ao armazenar cache: {e}") from e

    def _update_access_time(self, cache_key: str):
        """Atualiza o tempo de último acesso."""
        if cache_key in self._index:
            self._index[cache_key]["last_access"] = datetime.now().isoformat()
            self._save_index()

    def _remove_cache_entry(self, cache_key: str):
        """Remove entrada do cache."""
        try:
            cache_path = self._get_cache_path(cache_key)
            if cache_path.exists():
                cache_path.unlink()

            if cache_key in self._index:
                del self._index[cache_key]
                self._save_index()

        except Exception as e:
            logger.warning(f"Erro ao remover entrada do cache: {e}")

    def _cleanup_if_needed(self):
        """Limpa cache se exceder limite de tamanho."""
        current_size = self.get_cache_size()

        if current_size > self.max_size_bytes:
            logger.info(
                f"Cache excedeu limite ({current_size / 1024 / 1024:.2f}MB), iniciando limpeza..."
            )
            self._cleanup_old_entries(
                target_size=self.max_size_bytes * 0.8
            )  # Limpar para 80% do limite

    def _cleanup_old_entries(self, target_size: int):
        """
        Remove entradas antigas até atingir tamanho alvo.

        Args:
            target_size: Tamanho alvo em bytes
        """
        # Ordenar por último acesso (mais antigos primeiro)
        entries = sorted(self._index.items(), key=lambda x: x[1]["last_access"])

        current_size = self.get_cache_size()

        for cache_key, entry_info in entries:
            if current_size <= target_size:
                break

            entry_size = entry_info.get("size", 0)
            self._remove_cache_entry(cache_key)
            current_size -= entry_size

            logger.debug(f"Removida entrada antiga do cache: {entry_info['url']}")

        logger.info(
            f"Limpeza concluída. Tamanho atual: {current_size / 1024 / 1024:.2f}MB"
        )

    def get_cache_size(self) -> int:
        """Retorna o tamanho atual do cache em bytes."""
        total_size = 0

        for cache_key in self._index:
            cache_path = self._get_cache_path(cache_key)
            if cache_path.exists():
                total_size += cache_path.stat().st_size

        return total_size

    def get_cache_stats(self) -> dict[str, Any]:
        """Retorna estatísticas do cache."""
        total_entries = len(self._index)
        total_size = self.get_cache_size()

        # Contar entradas por idade
        now = datetime.now()
        age_groups = {"1h": 0, "1d": 0, "1w": 0, "older": 0}

        for entry_info in self._index.values():
            try:
                timestamp = datetime.fromisoformat(entry_info["timestamp"])
                age = now - timestamp

                if age < timedelta(hours=1):
                    age_groups["1h"] += 1
                elif age < timedelta(days=1):
                    age_groups["1d"] += 1
                elif age < timedelta(weeks=1):
                    age_groups["1w"] += 1
                else:
                    age_groups["older"] += 1
            except Exception:
                age_groups["older"] += 1

        return {
            "total_entries": total_entries,
            "total_size_mb": total_size / 1024 / 1024,
            "max_size_mb": self.max_size_bytes / 1024 / 1024,
            "usage_percent": (total_size / self.max_size_bytes) * 100,
            "age_distribution": age_groups,
            "cache_dir": str(self.cache_dir),
        }

    def clear_expired(self, ttl: int = 3600):
        """
        Remove todas as entradas expiradas.

        Args:
            ttl: Time-to-live em segundos para considerar expiração
        """
        expired_keys = []
        now = datetime.now()

        for cache_key, entry_info in self._index.items():
            try:
                timestamp = datetime.fromisoformat(entry_info["timestamp"])
                if now - timestamp > timedelta(seconds=ttl):
                    expired_keys.append(cache_key)
            except Exception:
                expired_keys.append(cache_key)

        for cache_key in expired_keys:
            self._remove_cache_entry(cache_key)

        logger.info(f"Removidas {len(expired_keys)} entradas expiradas do cache")

    def clear(self):
        """Limpa todo o cache."""
        try:
            # Remover todos os arquivos de cache
            for cache_file in self.cache_dir.glob("*.json"):
                if cache_file.name != "cache_index.json":
                    cache_file.unlink()

            # Limpar índice
            self._index = {}
            self._save_index()

            logger.info("Cache completamente limpo")

        except Exception as e:
            logger.error(f"Erro ao limpar cache: {e}")
            raise CacheError(f"Falha ao limpar cache: {e}") from e

    def has_url(self, url: str, headers: dict[str, str] | None = None) -> bool:
        """
        Verifica se uma URL está no cache.

        Args:
            url: URL a verificar
            headers: Headers da requisição (opcional)

        Returns:
            bool: True se a URL estiver no cache
        """
        if headers is None:
            headers = {}

        cache_key = self._get_cache_key(url, headers)
        return cache_key in self._index and self._get_cache_path(cache_key).exists()

    def get_cached_urls(self) -> list[str]:
        """
        Retorna lista de URLs em cache.

        Returns:
            List[str]: Lista de URLs
        """
        return [entry_info["url"] for entry_info in self._index.values()]

    def export_cache_info(self, filepath: str):
        """
        Exporta informações do cache para arquivo JSON.

        Args:
            filepath: Caminho do arquivo de saída
        """
        cache_info = {"stats": self.get_cache_stats(), "entries": []}

        for cache_key, entry_info in self._index.items():
            cache_info["entries"].append(  # type: ignore
                {
                    "cache_key": cache_key,
                    "url": entry_info["url"],
                    "timestamp": entry_info["timestamp"],
                    "size": entry_info["size"],
                    "last_access": entry_info.get(
                        "last_access", entry_info["timestamp"]
                    ),
                }
            )

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(cache_info, f, ensure_ascii=False, indent=2)

        logger.info(f"Informações do cache exportadas para: {filepath}")


class MemoryCache:
    """Cache em memória para uso temporário."""

    def __init__(self, max_entries: int = 100):
        """
        Inicializa cache em memória.

        Args:
            max_entries: Número máximo de entradas
        """
        self.max_entries = max_entries
        self._cache: dict[str, Any] = {}
        self._access_times: dict[str, float] = {}

    def get(self, key: str) -> Any | None:
        """Recupera valor do cache."""
        if key in self._cache:
            self._access_times[key] = time.time()
            return self._cache[key]
        return None

    def set(self, key: str, value: Any):
        """Armazena valor no cache."""
        # Remover entrada mais antiga se atingir limite
        if len(self._cache) >= self.max_entries and key not in self._cache:
            oldest_key = min(
                self._access_times.keys(), key=lambda k: self._access_times[k]
            )
            del self._cache[oldest_key]
            del self._access_times[oldest_key]

        self._cache[key] = value
        self._access_times[key] = time.time()

    def clear(self):
        """Limpa cache."""
        self._cache.clear()
        self._access_times.clear()

    def size(self) -> int:
        """Retorna número de entradas."""
        return len(self._cache)

    def keys(self) -> list[str]:
        """Retorna lista de chaves."""
        return list(self._cache.keys())
