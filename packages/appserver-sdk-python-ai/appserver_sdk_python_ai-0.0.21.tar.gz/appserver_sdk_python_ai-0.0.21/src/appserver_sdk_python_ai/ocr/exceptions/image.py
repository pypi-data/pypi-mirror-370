# appserver_sdk_python_ai/ocr/exceptions/image.py
"""
Exceções relacionadas ao processamento de imagens para OCR
=========================================================

Define exceções específicas para processamento de imagens durante OCR.
"""

from appserver_sdk_python_ai.ocr.exceptions.base import OCRError


class OCRImageError(OCRError):
    """Exceção lançada quando há erro no processamento da imagem."""

    def __init__(
        self, message: str, file_path: str, original_error: Exception | None = None
    ):
        self.original_error = original_error
        super().__init__(message, file_path=file_path)


class OCRFormatNotSupportedError(OCRError):
    """Exceção lançada quando o formato de arquivo não é suportado."""

    def __init__(self, file_path: str, format_detected: str):
        message = f"Formato '{format_detected}' não é suportado para OCR"
        super().__init__(message, file_path=file_path)
        self.format_detected = format_detected


class OCRLowConfidenceError(OCRError):
    """Exceção lançada quando a confiança do OCR está abaixo do mínimo."""

    def __init__(
        self,
        file_path: str,
        confidence: float,
        min_confidence: float,
        engine: str | None = None,
    ):
        message = f"Confiança do OCR ({confidence:.2f}) abaixo do mínimo ({min_confidence:.2f})"
        super().__init__(message, engine, file_path)
        self.confidence = confidence
        self.min_confidence = min_confidence
