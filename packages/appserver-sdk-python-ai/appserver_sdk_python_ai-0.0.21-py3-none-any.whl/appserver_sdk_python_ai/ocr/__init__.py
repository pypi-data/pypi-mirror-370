# appserver_sdk_python_ai/ocr/__init__.py
"""Módulo OCR para extração de texto de imagens.

Este módulo fornece funcionalidades avançadas de OCR (Optical Character Recognition)
para extrair texto de imagens em diversos formatos.

Características:
- Múltiplos engines: Tesseract, EasyOCR, PaddleOCR
- Formatos suportados: JPEG, PNG, GIF, TIFF, BMP, WEBP
- Pré-processamento automático de imagens
- Cache inteligente de resultados
- Processamento em lote
- Seleção automática do melhor engine

Exemplo de uso:
    from appserver_sdk_python_ai.ocr import OCRProcessor, OCRConfig

    # OCR customizado
    config = OCRConfig(engine="tesseract", languages=["pt", "en"])
    processor = OCRProcessor(config)
    resultado = processor.process_image("imagem.png")
"""

import logging
import warnings
from typing import Any

from appserver_sdk_python_ai.ocr.core.config import OCRConfig
from appserver_sdk_python_ai.ocr.core.processor import OCRProcessor
from appserver_sdk_python_ai.ocr.exceptions import (
    OCRCacheError,
    OCRConfigurationError,
    OCREngineError,
    OCRError,
    OCRFormatNotSupportedError,
    OCRImageError,
    OCRLowConfidenceError,
    OCRNetworkError,
    OCRNotAvailableError,
    OCRTimeoutError,
)

# Importar funcionalidades comuns do módulo shared
from appserver_sdk_python_ai.shared import (
    DependencyChecker,
    HealthChecker,
    SDKLogger,
    VersionInfo,
)

__version__ = "1.0.0"
__author__ = "appserver_sdk_python_ai"

__all__ = [
    # Classes principais
    "OCRProcessor",
    "OCRConfig",
    # Exceções
    "OCRError",
    "OCRNotAvailableError",
    "OCREngineError",
    "OCRImageError",
    "OCRFormatNotSupportedError",
    "OCRTimeoutError",
    "OCRLowConfidenceError",
    "OCRCacheError",
    "OCRConfigurationError",
    "OCRNetworkError",
    # Funções utilitárias
    "get_available_ocr_engines",
    "check_ocr_dependencies",
    "get_version_info",
    "health_check",
    "print_status",
    "setup_logging",
    # Constantes
    "OCR_AVAILABLE",
    # Informações do módulo
    "__version__",
    "__author__",
]

# Verificar disponibilidade de bibliotecas de OCR
OCR_LIBRARIES = {
    "tesseract": False,
    "easyocr": False,
    "paddleocr": False,
}

try:
    import PIL
    import pytesseract

    OCR_LIBRARIES["tesseract"] = True
except ImportError:
    pass

try:
    import easyocr

    OCR_LIBRARIES["easyocr"] = True
except ImportError:
    pass

try:
    import paddleocr

    OCR_LIBRARIES["paddleocr"] = True
except ImportError:
    pass

# Verificar se pelo menos uma biblioteca está disponível
OCR_AVAILABLE = any(OCR_LIBRARIES.values())


def get_available_ocr_engines():
    """Retorna lista de engines de OCR disponíveis."""
    return [engine for engine, available in OCR_LIBRARIES.items() if available]


def check_ocr_dependencies():
    """Verifica dependências de OCR e retorna status."""
    return {
        "ocr_available": OCR_AVAILABLE,
        "libraries": OCR_LIBRARIES.copy(),
        "recommended_install": "pip install pytesseract pillow easyocr"
        if not OCR_AVAILABLE
        else None,
    }


def get_version_info():
    """Retorna informações sobre a versão e dependências."""
    return VersionInfo.create_version_info(
        module_name="ocr",
        module_version=__version__,
        dependencies=DependencyChecker.check_dependencies(
            ["pytesseract", "pillow", "easyocr", "paddleocr"]
        ),
        additional_info={
            "ocr_available": OCR_AVAILABLE,
            "available_engines": get_available_ocr_engines(),
        },
    )


def health_check():
    """Verifica a saúde do módulo e suas dependências."""
    dependencies = DependencyChecker.check_dependencies(
        ["pytesseract", "pillow", "easyocr", "paddleocr"]
    )
    features = {
        "tesseract_engine": OCR_LIBRARIES.get("tesseract", False),
        "easyocr_engine": OCR_LIBRARIES.get("easyocr", False),
        "paddleocr_engine": OCR_LIBRARIES.get("paddleocr", False),
        "image_preprocessing": True,
        "batch_processing": True,
    }

    return HealthChecker.create_health_report(
        module_name="ocr",
        version=__version__,
        dependencies=dependencies,
        features=features,
        critical_deps=[],  # Nenhuma dependência é crítica, pois são opcionais
        optional_deps=["pytesseract", "pillow", "easyocr", "paddleocr"],
    )


def print_status():
    """Imprime status do módulo."""
    health = health_check()

    # Adicionar informações específicas do OCR
    print("=" * 60)
    print("MÓDULO OCR - appserver_sdk_python_ai")
    print("=" * 60)
    print(f"Versão: {__version__}")
    print(f"Status: {health['status']}")
    print(f"OCR Disponível: {'✅ Sim' if OCR_AVAILABLE else '❌ Não'}")

    # Usar o método padrão para o resto
    HealthChecker.print_health_status(
        health, show_dependencies=True, show_features=True
    )

    # Informações adicionais específicas do OCR
    print("\n🔍 Engines disponíveis:")
    available_engines = get_available_ocr_engines()
    if available_engines:
        for engine in available_engines:
            print(f"  ✅ {engine.title()}")
    else:
        print("  ❌ Nenhum engine disponível")
        print("  💡 Instale: pip install pytesseract pillow easyocr")


def setup_logging(level=logging.INFO, format_string=None):
    """
    Configura logging para o módulo OCR.

    Args:
        level: Nível de logging
        format_string: Formato customizado para logs
    """
    return SDKLogger.setup_logging(
        level=level,
        format_string=format_string,
        logger_name="appserver_sdk_python_ai.ocr",
    )
