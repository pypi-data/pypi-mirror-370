"""Utilitários de processamento unificados para todos os módulos do SDK."""

import hashlib
import logging
import mimetypes
import os
import re
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

try:
    from PIL import Image, ImageEnhance, ImageFilter

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None  # type: ignore[assignment]
    ImageEnhance = None  # type: ignore[assignment]
    ImageFilter = None  # type: ignore[assignment]

from appserver_sdk_python_ai.shared.exceptions import SharedError

logger = logging.getLogger(__name__)


class ProcessingError(SharedError):
    """Exceção para erros de processamento."""

    pass


class TextProcessor:
    """Processador de texto unificado."""

    @staticmethod
    def clean_text(
        text: str,
        remove_extra_whitespace: bool = True,
        remove_special_chars: bool = False,
        normalize_unicode: bool = True,
    ) -> str:
        """Limpa e normaliza texto."""
        if not isinstance(text, str):
            raise ProcessingError("Entrada deve ser uma string")

        # Normalizar unicode
        if normalize_unicode:
            import unicodedata

            text = unicodedata.normalize("NFKC", text)

        # Remover caracteres especiais
        if remove_special_chars:
            text = re.sub(r"[^\w\s]", "", text)

        # Remover espaços extras
        if remove_extra_whitespace:
            text = re.sub(r"\s+", " ", text).strip()

        return text

    @staticmethod
    def extract_sentences(text: str) -> list[str]:
        """Extrai sentenças do texto."""
        # Padrão simples para divisão de sentenças
        sentences = re.split(r"[.!?]+", text)
        return [s.strip() for s in sentences if s.strip()]

    @staticmethod
    def extract_words(text: str, min_length: int = 1) -> list[str]:
        """Extrai palavras do texto."""
        words = re.findall(r"\b\w+\b", text.lower())
        return [word for word in words if len(word) >= min_length]

    @staticmethod
    def remove_html_tags(text: str) -> str:
        """Remove tags HTML do texto."""
        clean = re.compile("<.*?>")
        return re.sub(clean, "", text)

    @staticmethod
    def extract_urls(text: str) -> list[str]:
        """Extrai URLs do texto."""
        url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        return re.findall(url_pattern, text)

    @staticmethod
    def extract_emails(text: str) -> list[str]:
        """Extrai emails do texto."""
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        return re.findall(email_pattern, text)

    @staticmethod
    def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
        """Trunca texto mantendo palavras inteiras."""
        if len(text) <= max_length:
            return text

        # Encontrar último espaço antes do limite
        truncated = text[: max_length - len(suffix)]
        last_space = truncated.rfind(" ")

        if last_space > 0:
            truncated = truncated[:last_space]

        return truncated + suffix

    @staticmethod
    def calculate_text_hash(text: str, algorithm: str = "sha256") -> str:
        """Calcula hash do texto."""
        if algorithm == "md5":
            return hashlib.md5(text.encode()).hexdigest()
        elif algorithm == "sha1":
            return hashlib.sha1(text.encode()).hexdigest()
        elif algorithm == "sha256":
            return hashlib.sha256(text.encode()).hexdigest()
        else:
            raise ProcessingError(f"Algoritmo de hash não suportado: {algorithm}")


class ImageProcessor:
    """Processador de imagens unificado."""

    SUPPORTED_FORMATS = [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"]

    def __init__(self):
        if not PIL_AVAILABLE:
            raise ProcessingError("PIL/Pillow não está instalado")

    @staticmethod
    def is_image_file(file_path: str | Path) -> bool:
        """Verifica se arquivo é uma imagem suportada."""
        path = Path(file_path)
        return path.suffix.lower() in ImageProcessor.SUPPORTED_FORMATS

    @staticmethod
    def get_image_info(image_path: str | Path) -> dict[str, Any]:
        """Obtém informações da imagem."""
        if not PIL_AVAILABLE:
            raise ProcessingError("PIL/Pillow não está instalado")

        try:
            with Image.open(image_path) as img:
                return {
                    "format": img.format,
                    "mode": img.mode,
                    "size": img.size,
                    "width": img.width,
                    "height": img.height,
                    "has_transparency": img.mode in ("RGBA", "LA")
                    or "transparency" in img.info,
                }
        except Exception as e:
            raise ProcessingError(f"Erro ao obter informações da imagem: {e}") from e

    @staticmethod
    def resize_image(
        image_path: str | Path,
        output_path: str | Path,
        size: tuple[int, int],
        maintain_aspect_ratio: bool = True,
        quality: int = 95,
    ) -> None:
        """Redimensiona imagem."""
        if not PIL_AVAILABLE:
            raise ProcessingError("PIL/Pillow não está instalado")

        try:
            with Image.open(image_path) as img:
                if maintain_aspect_ratio:
                    img.thumbnail(size, Image.Resampling.LANCZOS)
                else:
                    img = img.resize(size, Image.Resampling.LANCZOS)

                # Salvar com qualidade especificada
                save_kwargs = {"quality": quality, "optimize": True}
                if img.format == "PNG":
                    save_kwargs = {"optimize": True}

                img.save(output_path, **save_kwargs)

        except Exception as e:
            raise ProcessingError(f"Erro ao redimensionar imagem: {e}") from e

    @staticmethod
    def enhance_image(
        image_path: str | Path,
        output_path: str | Path,
        brightness: float = 1.0,
        contrast: float = 1.0,
        sharpness: float = 1.0,
    ) -> None:
        """Aplica melhorias na imagem."""
        if not PIL_AVAILABLE:
            raise ProcessingError("PIL/Pillow não está instalado")

        try:
            with Image.open(image_path) as img:
                # Aplicar melhorias
                if brightness != 1.0:
                    brightness_enhancer = ImageEnhance.Brightness(img)
                    img = brightness_enhancer.enhance(brightness)

                if contrast != 1.0:
                    contrast_enhancer = ImageEnhance.Contrast(img)
                    img = contrast_enhancer.enhance(contrast)

                if sharpness != 1.0:
                    sharpness_enhancer = ImageEnhance.Sharpness(img)
                    img = sharpness_enhancer.enhance(sharpness)

                img.save(output_path)

        except Exception as e:
            raise ProcessingError(f"Erro ao melhorar imagem: {e}") from e

    @staticmethod
    def convert_format(
        image_path: str | Path,
        output_path: str | Path,
        target_format: str = "JPEG",
        quality: int = 95,
    ) -> None:
        """Converte formato da imagem."""
        if not PIL_AVAILABLE:
            raise ProcessingError("PIL/Pillow não está instalado")

        try:
            with Image.open(image_path) as img:
                # Converter para RGB se necessário (para JPEG)
                if target_format.upper() == "JPEG" and img.mode in ("RGBA", "LA"):
                    # Criar fundo branco
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    background.paste(
                        img, mask=img.split()[-1] if img.mode == "RGBA" else None
                    )
                    img = background

                save_kwargs = {}
                if target_format.upper() == "JPEG":
                    save_kwargs = {"quality": quality, "optimize": True}
                elif target_format.upper() == "PNG":
                    save_kwargs = {"optimize": True}

                img.save(output_path, format=target_format, **save_kwargs)

        except Exception as e:
            raise ProcessingError(f"Erro ao converter formato da imagem: {e}") from e

    @staticmethod
    def apply_filters(
        image_path: str | Path, output_path: str | Path, filters: list[str]
    ) -> None:
        """Aplica filtros na imagem."""
        if not PIL_AVAILABLE:
            raise ProcessingError("PIL/Pillow não está instalado")

        filter_map = {
            "blur": ImageFilter.BLUR,
            "detail": ImageFilter.DETAIL,
            "edge_enhance": ImageFilter.EDGE_ENHANCE,
            "edge_enhance_more": ImageFilter.EDGE_ENHANCE_MORE,
            "emboss": ImageFilter.EMBOSS,
            "find_edges": ImageFilter.FIND_EDGES,
            "sharpen": ImageFilter.SHARPEN,
            "smooth": ImageFilter.SMOOTH,
            "smooth_more": ImageFilter.SMOOTH_MORE,
        }

        try:
            with Image.open(image_path) as img:
                for filter_name in filters:
                    if filter_name in filter_map:
                        img = img.filter(filter_map[filter_name])
                    else:
                        logger.warning(f"Filtro desconhecido: {filter_name}")

                img.save(output_path)

        except Exception as e:
            raise ProcessingError(f"Erro ao aplicar filtros: {e}") from e


class FileProcessor:
    """Processador de arquivos unificado."""

    @staticmethod
    def get_file_info(file_path: str | Path) -> dict[str, Any]:
        """Obtém informações do arquivo."""
        path = Path(file_path)

        if not path.exists():
            raise ProcessingError(f"Arquivo não encontrado: {file_path}")

        stat = path.stat()
        mime_type, encoding = mimetypes.guess_type(str(path))

        return {
            "name": path.name,
            "stem": path.stem,
            "suffix": path.suffix,
            "size": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "mime_type": mime_type,
            "encoding": encoding,
            "is_text": mime_type and mime_type.startswith("text/"),
            "is_image": mime_type and mime_type.startswith("image/"),
            "is_binary": not (mime_type and mime_type.startswith("text/")),
        }

    @staticmethod
    def calculate_file_hash(
        file_path: str | Path, algorithm: str = "sha256", chunk_size: int = 8192
    ) -> str:
        """Calcula hash do arquivo."""
        if algorithm == "md5":
            hasher = hashlib.md5()
        elif algorithm == "sha1":
            hasher = hashlib.sha1()
        elif algorithm == "sha256":
            hasher = hashlib.sha256()
        else:
            raise ProcessingError(f"Algoritmo de hash não suportado: {algorithm}")

        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(chunk_size):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            raise ProcessingError(f"Erro ao calcular hash do arquivo: {e}") from e

    @staticmethod
    def read_file_safely(
        file_path: str | Path, max_size_mb: int = 100, encoding: str = "utf-8"
    ) -> str:
        """Lê arquivo de texto com segurança."""
        path = Path(file_path)

        if not path.exists():
            raise ProcessingError(f"Arquivo não encontrado: {file_path}")

        # Verificar tamanho
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > max_size_mb:
            raise ProcessingError(
                f"Arquivo muito grande: {size_mb:.2f}MB (máximo: {max_size_mb}MB)"
            )

        try:
            with open(path, encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            # Tentar com encoding diferente
            try:
                with open(path, encoding="latin-1") as f:
                    return f.read()
            except Exception as e:
                raise ProcessingError(f"Erro ao ler arquivo: {e}") from e
        except Exception as e:
            raise ProcessingError(f"Erro ao ler arquivo: {e}") from e

    @staticmethod
    def create_temp_file(
        content: str | bytes, suffix: str = ".tmp", prefix: str = "sdk_"
    ) -> str:
        """Cria arquivo temporário."""
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb" if isinstance(content, bytes) else "w",
                suffix=suffix,
                prefix=prefix,
                delete=False,
            ) as f:
                f.write(content)
                return f.name
        except Exception as e:
            raise ProcessingError(f"Erro ao criar arquivo temporário: {e}") from e

    @staticmethod
    def cleanup_temp_files(file_paths: list[str]) -> None:
        """Remove arquivos temporários."""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except Exception as e:
                logger.warning(f"Erro ao remover arquivo temporário {file_path}: {e}")


class DataProcessor:
    """Processador de dados genérico."""

    @staticmethod
    def flatten_dict(data: dict[str, Any], separator: str = ".") -> dict[str, Any]:
        """Achata dicionário aninhado."""

        def _flatten(obj, parent_key="") -> dict[str, Any]:
            items: list[tuple[str, Any]] = []
            if isinstance(obj, dict):
                for k, v in obj.items():
                    new_key = f"{parent_key}{separator}{k}" if parent_key else k
                    items.extend(_flatten(v, new_key).items())
            else:
                return {parent_key: obj}
            return dict(items)

        return _flatten(data)

    @staticmethod
    def unflatten_dict(data: dict[str, Any], separator: str = ".") -> dict[str, Any]:
        """Reconstrói dicionário aninhado."""
        result: dict[str, Any] = {}
        for key, value in data.items():
            keys = key.split(separator)
            d = result
            for k in keys[:-1]:
                if k not in d:
                    d[k] = {}
                d = d[k]
            d[keys[-1]] = value
        return result

    @staticmethod
    def merge_dicts(
        dict1: dict[str, Any], dict2: dict[str, Any], deep: bool = True
    ) -> dict[str, Any]:
        """Mescla dois dicionários."""
        if not deep:
            result = dict1.copy()
            result.update(dict2)
            return result

        result = dict1.copy()
        for key, value in dict2.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = DataProcessor.merge_dicts(result[key], value, deep=True)
            else:
                result[key] = value
        return result

    @staticmethod
    def filter_dict(
        data: dict[str, Any],
        include_keys: list[str] | None = None,
        exclude_keys: list[str] | None = None,
    ) -> dict[str, Any]:
        """Filtra dicionário por chaves."""
        if include_keys:
            return {k: v for k, v in data.items() if k in include_keys}

        if exclude_keys:
            return {k: v for k, v in data.items() if k not in exclude_keys}

        return data.copy()

    @staticmethod
    def sanitize_data(
        data: Any, remove_none: bool = True, remove_empty: bool = False
    ) -> Any:
        """Sanitiza dados removendo valores nulos/vazios."""
        if isinstance(data, dict):
            dict_result: dict[str, Any] = {}
            for k, v in data.items():
                sanitized_value = DataProcessor.sanitize_data(
                    v, remove_none, remove_empty
                )

                if remove_none and sanitized_value is None:
                    continue

                if (
                    remove_empty
                    and not sanitized_value
                    and sanitized_value != 0
                    and sanitized_value is not False
                ):
                    continue

                dict_result[k] = sanitized_value
            return dict_result

        elif isinstance(data, list):
            list_result: list[Any] = []
            for item in data:
                sanitized_item = DataProcessor.sanitize_data(
                    item, remove_none, remove_empty
                )

                if remove_none and sanitized_item is None:
                    continue

                if (
                    remove_empty
                    and not sanitized_item
                    and sanitized_item != 0
                    and sanitized_item is not False
                ):
                    continue

                list_result.append(sanitized_item)
            return list_result

        return data

    @staticmethod
    def chunk_list(data: list[Any], chunk_size: int) -> list[list[Any]]:
        """Divide lista em chunks."""
        return [data[i : i + chunk_size] for i in range(0, len(data), chunk_size)]

    @staticmethod
    def deduplicate_list(
        data: list[Any], key_func: Callable[[Any], Any] | None = None
    ) -> list[Any]:
        """Remove duplicatas de lista."""
        if key_func:
            seen = set()
            dedup_result: list[Any] = []
            for item in data:
                key = key_func(item)
                if key not in seen:
                    seen.add(key)
                    dedup_result.append(item)
            return dedup_result
        else:
            return list(dict.fromkeys(data))  # Preserva ordem


# Instâncias globais
text_processor = TextProcessor()
file_processor = FileProcessor()
data_processor = DataProcessor()

# Criar instância de image_processor apenas se PIL estiver disponível
image_processor = ImageProcessor() if PIL_AVAILABLE else None
