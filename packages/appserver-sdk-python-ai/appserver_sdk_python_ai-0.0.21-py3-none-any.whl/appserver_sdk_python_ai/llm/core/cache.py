"""Sistema de cache para o módulo LLM.

Este módulo implementa um sistema de cache em memória para melhorar a performance
das operações de tokenização e listagem de modelos.
"""

import threading
import time
from collections import OrderedDict
from dataclasses import dataclass
from functools import wraps
from typing import Any


@dataclass
class CacheEntry:
    """Entrada do cache com timestamp e dados."""

    value: Any
    timestamp: float
    access_count: int = 0
    last_access: float = 0.0

    def __post_init__(self):
        """Inicializa o timestamp de último acesso."""
        if self.last_access == 0.0:
            self.last_access = self.timestamp

    def is_expired(self, ttl: float) -> bool:
        """Verifica se a entrada expirou."""
        return time.time() - self.timestamp > ttl

    def touch(self):
        """Atualiza o timestamp de último acesso e incrementa contador."""
        self.last_access = time.time()
        self.access_count += 1


class LRUCache:
    """Cache LRU (Least Recently Used) thread-safe."""

    def __init__(self, max_size: int = 1000, default_ttl: float = 3600.0):
        """
        Inicializa o cache LRU.

        Args:
            max_size: Tamanho máximo do cache
            default_ttl: TTL padrão em segundos (1 hora)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    def get(self, key: str, default: Any = None) -> Any:
        """Obtém um valor do cache."""
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return default

            entry = self._cache[key]

            # Verifica se expirou
            if entry.is_expired(self.default_ttl):
                del self._cache[key]
                self._misses += 1
                return default

            # Move para o final (mais recente)
            self._cache.move_to_end(key)
            entry.touch()
            self._hits += 1
            return entry.value

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        """Define um valor no cache."""
        with self._lock:
            current_time = time.time()

            if key in self._cache:
                # Atualiza entrada existente
                self._cache[key] = CacheEntry(value, current_time)
                self._cache.move_to_end(key)
            else:
                # Nova entrada
                if len(self._cache) >= self.max_size:
                    # Remove o item menos recentemente usado
                    self._cache.popitem(last=False)
                    self._evictions += 1

                self._cache[key] = CacheEntry(value, current_time)

    def delete(self, key: str) -> bool:
        """Remove uma entrada do cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        """Limpa todo o cache."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            self._evictions = 0

    def cleanup_expired(self) -> int:
        """Remove entradas expiradas e retorna o número removido."""
        with self._lock:
            current_time = time.time()
            expired_keys = [
                key
                for key, entry in self._cache.items()
                if current_time - entry.timestamp > self.default_ttl
            ]

            for key in expired_keys:
                del self._cache[key]

            return len(expired_keys)

    def get_stats(self) -> dict[str, int | float]:
        """Retorna estatísticas do cache."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (
                (self._hits / total_requests * 100) if total_requests > 0 else 0.0
            )

            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "evictions": self._evictions,
                "hit_rate": hit_rate,
                "total_requests": total_requests,
            }

    def get_memory_usage(self) -> dict[str, Any]:
        """Retorna informações sobre uso de memória."""
        with self._lock:
            import sys

            total_size = sys.getsizeof(self._cache)
            for key, entry in self._cache.items():
                total_size += sys.getsizeof(key) + sys.getsizeof(entry)

            return {
                "total_bytes": total_size,
                "total_mb": total_size / (1024 * 1024),
                "entries": len(self._cache),
                "avg_size_per_entry": total_size / len(self._cache)
                if self._cache
                else 0,
            }


# Cache global para o módulo LLM
_global_cache = LRUCache(max_size=1000, default_ttl=3600.0)


def get_cache() -> LRUCache:
    """Retorna a instância global do cache."""
    return _global_cache


def cache_result(key_prefix: str = "", ttl: float | None = None):
    """Decorator para cache automático de resultados de funções."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Gera chave do cache
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"

            # Tenta obter do cache
            cached_result = _global_cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Executa função e armazena resultado
            result = func(*args, **kwargs)
            _global_cache.set(cache_key, result, ttl)
            return result

        # Adiciona método para limpar cache específico da função
        wrapper.clear_cache = lambda: _clear_function_cache(
            f"{key_prefix}:{func.__name__}"
        )
        return wrapper

    return decorator


def _clear_function_cache(prefix: str) -> int:
    """Limpa entradas do cache que começam com o prefixo especificado."""
    with _global_cache._lock:
        keys_to_remove = [
            key for key in _global_cache._cache.keys() if key.startswith(prefix)
        ]

        for key in keys_to_remove:
            del _global_cache._cache[key]

        return len(keys_to_remove)


def clear_cache(pattern: str | None = None) -> int:
    """Limpa o cache global ou entradas que correspondem ao padrão."""
    if pattern is None:
        _global_cache.clear()
        return 0
    else:
        return _clear_function_cache(pattern)


def get_cache_stats() -> dict[str, int | float]:
    """Retorna estatísticas do cache global."""
    return _global_cache.get_stats()


def cleanup_expired_cache() -> int:
    """Remove entradas expiradas do cache global."""
    return _global_cache.cleanup_expired()


def get_cache_memory_usage() -> dict[str, float]:
    """Retorna informações sobre o uso de memória do cache global."""
    return _global_cache.get_memory_usage()
