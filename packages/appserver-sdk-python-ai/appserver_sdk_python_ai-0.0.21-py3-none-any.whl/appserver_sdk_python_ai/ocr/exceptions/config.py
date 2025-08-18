# appserver_sdk_python_ai/ocr/exceptions/config.py
"""
Exceções de configuração para OCR
================================

Define exceções relacionadas à configuração durante OCR.
"""

from appserver_sdk_python_ai.ocr.exceptions.base import OCRError


class OCRConfigurationError(OCRError):
    """Exceção lançada quando há erro na configuração do OCR."""

    def __init__(self, message: str, config_key: str | None = None):
        super().__init__(message)
        self.config_key = config_key
