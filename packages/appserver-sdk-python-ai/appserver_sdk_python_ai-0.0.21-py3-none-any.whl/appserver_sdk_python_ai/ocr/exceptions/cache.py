# appserver_sdk_python_ai/ocr/exceptions/cache.py
"""
Exceções de cache para OCR
=========================

Define exceções relacionadas ao sistema de cache durante OCR.
"""

from appserver_sdk_python_ai.ocr.exceptions.base import OCRError


class OCRCacheError(OCRError):
    """Exceção lançada quando há erro no sistema de cache do OCR."""

    def __init__(self, message: str, cache_path: str | None = None):
        super().__init__(message)
        self.cache_path = cache_path
