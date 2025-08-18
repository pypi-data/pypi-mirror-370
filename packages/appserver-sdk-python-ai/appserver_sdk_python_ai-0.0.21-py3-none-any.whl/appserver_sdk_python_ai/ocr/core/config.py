# appserver_sdk_python_ai/ocr/config.py
"""
Configurações para o módulo de OCR
================================

Este módulo contém as configurações padrão e personalizáveis
para o processamento de OCR.
"""

from dataclasses import dataclass, field
from enum import Enum


class OCREngine(Enum):
    """Engines de OCR disponíveis."""

    TESSERACT = "tesseract"
    EASYOCR = "easyocr"
    PADDLEOCR = "paddleocr"
    AUTO = "auto"  # Seleciona automaticamente o melhor disponível


class ImageFormat(Enum):
    """Formatos de imagem suportados."""

    JPEG = "jpeg"
    JPG = "jpg"
    PNG = "png"
    GIF = "gif"
    TIFF = "tiff"
    TIF = "tif"
    BMP = "bmp"
    WEBP = "webp"


@dataclass
class OCRConfig:
    """Configuração para processamento de OCR."""

    # Engine de OCR preferido
    engine: OCREngine = OCREngine.AUTO

    # Idiomas para reconhecimento (códigos ISO)
    languages: list[str] = field(default_factory=lambda: ["por", "eng"])

    # Configurações do Tesseract
    tesseract_config: str = "--oem 3 --psm 6"
    tesseract_timeout: int = 30

    # Configurações do EasyOCR
    easyocr_gpu: bool = False
    easyocr_model_storage_directory: str | None = None

    # Configurações do PaddleOCR
    paddleocr_use_angle_cls: bool = True
    paddleocr_lang: str = "pt"
    paddleocr_use_gpu: bool = False

    # Pré-processamento de imagem
    preprocess_image: bool = True
    resize_factor: float = 2.0  # Fator de redimensionamento
    denoise: bool = True
    enhance_contrast: bool = True

    # Pós-processamento de texto
    clean_text: bool = True
    remove_extra_whitespace: bool = True
    min_confidence: float = 0.5  # Confiança mínima (0-1)

    # Formatos de imagem suportados
    supported_formats: list[ImageFormat] = field(
        default_factory=lambda: [
            ImageFormat.JPEG,
            ImageFormat.JPG,
            ImageFormat.PNG,
            ImageFormat.GIF,
            ImageFormat.TIFF,
            ImageFormat.TIF,
            ImageFormat.BMP,
            ImageFormat.WEBP,
        ]
    )

    # Cache de resultados
    enable_cache: bool = True
    cache_ttl: int = 3600  # TTL em segundos (1 hora)

    # Configurações de processamento em lote
    batch_size: int = 10
    max_workers: int = 4

    # Configurações de timeout
    processing_timeout: int = 60  # Timeout por imagem em segundos

    def get_tesseract_languages(self) -> str:
        """Retorna string de idiomas formatada para Tesseract."""
        return "+".join(self.languages)

    def get_easyocr_languages(self) -> list[str]:
        """Retorna lista de idiomas formatada para EasyOCR."""
        # Mapear códigos ISO para códigos do EasyOCR
        lang_map = {
            "por": "pt",
            "eng": "en",
            "spa": "es",
            "fra": "fr",
            "deu": "de",
            "ita": "it",
        }
        return [lang_map.get(lang, lang) for lang in self.languages]

    def is_format_supported(self, file_extension: str) -> bool:
        """Verifica se o formato de arquivo é suportado."""
        ext = file_extension.lower().lstrip(".")
        return any(fmt.value == ext for fmt in self.supported_formats)


# Configuração padrão global
DEFAULT_OCR_CONFIG = OCRConfig()
