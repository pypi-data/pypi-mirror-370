"""Sistema de cache unificado para todos os módulos do SDK."""

import hashlib
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from appserver_sdk_python_ai.shared.exceptions import SharedError

logger = logging.getLogger(__name__)


class CacheError(SharedError):
    """Exceção específica para operações de cache."""

    pass


class BaseCacheBackend(ABC):
    """Interface base para backends de cache."""

    @abstractmethod
    def get(self, key: str) -> Any | None:
        """Recupera valor do cache."""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Armazena valor no cache."""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Remove valor do cache."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Limpa todo o cache."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Verifica se chave existe no cache."""
        pass


class MemoryCacheBackend(BaseCacheBackend):
    """Backend de cache em memória."""

    def __init__(self, max_entries: int = 1000):
        self.max_entries = max_entries
        self._cache: dict[str, dict[str, Any]] = {}

    def get(self, key: str) -> Any | None:
        """Recupera valor do cache."""
        if key not in self._cache:
            return None

        entry = self._cache[key]

        # Verificar expiração
        if entry.get("expires_at") and datetime.now() > datetime.fromisoformat(
            entry["expires_at"]
        ):
            del self._cache[key]
            return None

        # Atualizar último acesso
        entry["last_access"] = datetime.now().isoformat()
        return entry["value"]

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Armazena valor no cache."""
        # Limpar cache se necessário
        if len(self._cache) >= self.max_entries:
            self._cleanup_old_entries()

        expires_at = None
        if ttl:
            expires_at = (datetime.now() + timedelta(seconds=ttl)).isoformat()

        self._cache[key] = {
            "value": value,
            "created_at": datetime.now().isoformat(),
            "last_access": datetime.now().isoformat(),
            "expires_at": expires_at,
            "ttl": ttl,
        }

    def delete(self, key: str) -> bool:
        """Remove valor do cache."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        """Limpa todo o cache."""
        self._cache.clear()

    def exists(self, key: str) -> bool:
        """Verifica se chave existe no cache."""
        return key in self._cache

    def _cleanup_old_entries(self, keep_ratio: float = 0.8):
        """Remove entradas antigas para liberar espaço."""
        if not self._cache:
            return

        # Ordenar por último acesso
        sorted_entries = sorted(self._cache.items(), key=lambda x: x[1]["last_access"])

        # Manter apenas uma porcentagem das entradas
        keep_count = int(len(sorted_entries) * keep_ratio)
        entries_to_keep = sorted_entries[-keep_count:]

        # Reconstruir cache
        self._cache = dict(entries_to_keep)


class FileCacheBackend(BaseCacheBackend):
    """Backend de cache em arquivo."""

    def __init__(self, cache_dir: str = ".sdk_cache", max_size_mb: int = 100):
        self.cache_dir = Path(cache_dir)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.cache_dir.mkdir(exist_ok=True)

        # Arquivo de índice
        self.index_file = self.cache_dir / "cache_index.json"
        self._load_index()

    def _load_index(self):
        """Carrega índice do cache."""
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
        """Salva índice do cache."""
        try:
            with open(self.index_file, "w", encoding="utf-8") as f:
                json.dump(self._index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar índice do cache: {e}")

    def _get_cache_path(self, key: str) -> Path:
        """Retorna caminho do arquivo de cache."""
        # Sanitizar nome do arquivo para Windows
        safe_key = key.replace(":", "_").replace("/", "_").replace("\\", "_")
        safe_key = "".join(c for c in safe_key if c.isalnum() or c in "._-")
        return self.cache_dir / f"{safe_key}.json"

    def get(self, key: str) -> Any | None:
        """Recupera valor do cache."""
        try:
            cache_path = self._get_cache_path(key)

            if not cache_path.exists():
                return None

            with open(cache_path, encoding="utf-8") as f:
                entry = json.load(f)

            # Verificar expiração
            if entry.get("expires_at") and datetime.now() > datetime.fromisoformat(
                entry["expires_at"]
            ):
                self.delete(key)
                return None

            # Atualizar último acesso
            if key in self._index:
                self._index[key]["last_access"] = datetime.now().isoformat()
                self._save_index()

            return entry["value"]

        except Exception as e:
            logger.warning(f"Erro ao recuperar cache para chave {key}: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Armazena valor no cache."""
        try:
            cache_path = self._get_cache_path(key)

            expires_at = None
            if ttl:
                expires_at = (datetime.now() + timedelta(seconds=ttl)).isoformat()

            entry = {
                "value": value,
                "created_at": datetime.now().isoformat(),
                "last_access": datetime.now().isoformat(),
                "expires_at": expires_at,
                "ttl": ttl,
            }

            # Salvar arquivo
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(entry, f, ensure_ascii=False, indent=2)

            # Atualizar índice
            self._index[key] = {
                "created_at": entry["created_at"],
                "last_access": entry["last_access"],
                "expires_at": expires_at,
                "size": cache_path.stat().st_size,
            }

            self._save_index()
            self._cleanup_if_needed()

        except Exception as e:
            logger.error(f"Erro ao armazenar cache para chave {key}: {e}")
            raise CacheError(f"Falha ao armazenar cache: {e}") from e

    def delete(self, key: str) -> bool:
        """Remove valor do cache."""
        try:
            cache_path = self._get_cache_path(key)

            if cache_path.exists():
                cache_path.unlink()

            if key in self._index:
                del self._index[key]
                self._save_index()
                return True

            return False

        except Exception as e:
            logger.warning(f"Erro ao remover cache para chave {key}: {e}")
            return False

    def clear(self) -> None:
        """Limpa todo o cache."""
        try:
            for key in list(self._index.keys()):
                self.delete(key)
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {e}")

    def exists(self, key: str) -> bool:
        """Verifica se chave existe no cache."""
        return key in self._index and self._get_cache_path(key).exists()

    def _cleanup_if_needed(self):
        """Limpa cache se exceder limite de tamanho."""
        try:
            total_size = sum(entry.get("size", 0) for entry in self._index.values())

            if total_size > self.max_size_bytes:
                # Ordenar por último acesso
                sorted_entries = sorted(
                    self._index.items(), key=lambda x: x[1]["last_access"]
                )

                # Remover entradas antigas até ficar abaixo do limite
                current_size = total_size
                for key, entry in sorted_entries:
                    if current_size <= self.max_size_bytes * 0.8:  # 80% do limite
                        break

                    self.delete(key)
                    current_size -= entry.get("size", 0)

        except Exception as e:
            logger.warning(f"Erro durante limpeza do cache: {e}")


class UnifiedCacheManager:
    """Gerenciador de cache unificado para o SDK."""

    def __init__(
        self, backend: BaseCacheBackend | None = None, default_ttl: int = 3600
    ):
        self.backend = backend or MemoryCacheBackend()
        self.default_ttl = default_ttl
        self._key_prefix = "sdk"

    def _make_key(self, key: str, namespace: str | None = None) -> str:
        """Cria chave de cache com namespace."""
        parts = [self._key_prefix]
        if namespace:
            parts.append(namespace)
        parts.append(key)
        return ":".join(parts)

    def get(self, key: str, namespace: str | None = None) -> Any | None:
        """Recupera valor do cache."""
        cache_key = self._make_key(key, namespace)
        return self.backend.get(cache_key)

    def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
        namespace: str | None = None,
    ) -> None:
        """Armazena valor no cache."""
        cache_key = self._make_key(key, namespace)
        ttl = ttl or self.default_ttl
        self.backend.set(cache_key, value, ttl)

    def delete(self, key: str, namespace: str | None = None) -> bool:
        """Remove valor do cache."""
        cache_key = self._make_key(key, namespace)
        return self.backend.delete(cache_key)

    def exists(self, key: str, namespace: str | None = None) -> bool:
        """Verifica se chave existe no cache."""
        cache_key = self._make_key(key, namespace)
        return self.backend.exists(cache_key)

    def clear(self, namespace: str | None = None) -> None:
        """Limpa cache (todo ou por namespace)."""
        if namespace is None:
            self.backend.clear()
        else:
            # Para namespaces específicos, precisaríamos implementar
            # uma funcionalidade de listagem de chaves no backend
            logger.warning("Limpeza por namespace não implementada para este backend")

    def cache_key_from_data(
        self, data: str | dict | list, namespace: str | None = None
    ) -> str:
        """Gera chave de cache a partir de dados."""
        if isinstance(data, str):
            content = data
        else:
            content = json.dumps(data, sort_keys=True, ensure_ascii=False)

        hash_key = hashlib.sha256(content.encode()).hexdigest()[:16]
        return self._make_key(hash_key, namespace)

    def cached(self, ttl: int | None = None, namespace: str | None = None):
        """Decorator para cache de funções."""

        def decorator(func):
            def wrapper(*args, **kwargs):
                # Criar chave baseada na função e argumentos
                func_name = f"{func.__module__}.{func.__name__}"
                args_key = self.cache_key_from_data({"args": args, "kwargs": kwargs})
                cache_key = f"{func_name}:{args_key}"

                # Tentar recuperar do cache
                result = self.get(cache_key, namespace)
                if result is not None:
                    return result

                # Executar função e cachear resultado
                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl, namespace)
                return result

            return wrapper

        return decorator


# Instância global padrão
default_cache = UnifiedCacheManager()
