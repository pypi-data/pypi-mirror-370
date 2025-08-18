# appserver_sdk_python_ai/ocr/exceptions/engine.py
"""
Exceções relacionadas aos engines de OCR
=======================================

Define exceções específicas para operações com engines de OCR.
"""

from appserver_sdk_python_ai.ocr.exceptions.base import OCRError


class OCRNotAvailableError(OCRError):
    """Exceção lançada quando nenhuma biblioteca de OCR está disponível."""

    def __init__(self, message: str = "Nenhuma biblioteca de OCR está disponível"):
        super().__init__(message)


class OCREngineError(OCRError):
    """Exceção lançada quando há erro específico do engine de OCR."""

    def __init__(
        self, message: str, engine: str, original_error: Exception | None = None
    ):
        self.original_error = original_error
        super().__init__(message, engine)


class OCRTimeoutError(OCRError):
    """Exceção lançada quando o processamento de OCR excede o timeout."""

    def __init__(self, file_path: str, timeout: int, engine: str | None = None):
        message = f"Timeout de {timeout}s excedido durante processamento de OCR"
        super().__init__(message, engine, file_path)
        self.timeout = timeout
