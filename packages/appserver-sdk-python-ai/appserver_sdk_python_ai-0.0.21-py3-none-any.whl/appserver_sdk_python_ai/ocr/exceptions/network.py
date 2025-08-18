# appserver_sdk_python_ai/ocr/exceptions/network.py
"""
Exceções de rede para OCR
========================

Define exceções relacionadas à rede durante operações de OCR.
"""

from appserver_sdk_python_ai.ocr.exceptions.base import OCRError


class OCRNetworkError(OCRError):
    """Exceção lançada quando há erro de rede durante operações de OCR."""

    def __init__(self, message: str, url: str | None = None):
        super().__init__(message)
        self.url = url
