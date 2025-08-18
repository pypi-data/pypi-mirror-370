# appserver_sdk_python_ai/ocr/exceptions/__init__.py
"""
Exceções específicas para o módulo de OCR
========================================

Este módulo define exceções customizadas para operações de OCR.
"""

from appserver_sdk_python_ai.ocr.exceptions.base import OCRError
from appserver_sdk_python_ai.ocr.exceptions.cache import OCRCacheError
from appserver_sdk_python_ai.ocr.exceptions.config import OCRConfigurationError
from appserver_sdk_python_ai.ocr.exceptions.engine import (
    OCREngineError,
    OCRNotAvailableError,
    OCRTimeoutError,
)
from appserver_sdk_python_ai.ocr.exceptions.image import (
    OCRFormatNotSupportedError,
    OCRImageError,
    OCRLowConfidenceError,
)
from appserver_sdk_python_ai.ocr.exceptions.network import OCRNetworkError

__all__ = [
    "OCRError",
    "OCRNotAvailableError",
    "OCREngineError",
    "OCRTimeoutError",
    "OCRImageError",
    "OCRFormatNotSupportedError",
    "OCRLowConfidenceError",
    "OCRCacheError",
    "OCRConfigurationError",
    "OCRNetworkError",
]
