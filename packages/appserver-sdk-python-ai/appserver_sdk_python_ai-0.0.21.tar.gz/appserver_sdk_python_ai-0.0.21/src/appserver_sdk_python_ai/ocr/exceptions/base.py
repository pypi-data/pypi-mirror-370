# appserver_sdk_python_ai/ocr/exceptions/base.py
"""
Exceção base para o módulo de OCR
===============================

Define a exceção base para todas as operações de OCR.
"""


class OCRError(Exception):
    """Exceção base para erros de OCR."""

    def __init__(
        self,
        message: str,
        engine: str | None = None,
        file_path: str | None = None,
    ):
        self.message = message
        self.engine = engine
        self.file_path = file_path
        super().__init__(self.message)

    def __str__(self) -> str:
        parts = [self.message]
        if self.engine:
            parts.append(f"Engine: {self.engine}")
        if self.file_path:
            parts.append(f"Arquivo: {self.file_path}")
        return " | ".join(parts)
