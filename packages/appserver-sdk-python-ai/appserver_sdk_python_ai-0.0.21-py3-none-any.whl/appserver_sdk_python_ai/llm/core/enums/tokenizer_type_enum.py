"""Enum para tipos de tokenizer suportados."""

from __future__ import annotations

from enum import Enum


class TokenizerTypeEnum(str, Enum):
    """Tipos de tokenizer disponíveis na biblioteca."""

    OPENAI = "openai"
    HUGGINGFACE = "huggingface"
    CUSTOM = "custom"
    DEFAULT = "default"

    def requires_external_library(self) -> bool:
        """Verifica se o tipo de tokenizer requer biblioteca externa.

        Returns:
            True se precisar instalar dependências adicionais.
        """
        external_libs = {self.OPENAI, self.HUGGINGFACE}
        return self in external_libs

    def get_required_packages(self) -> list[str]:
        """Retorna lista de pacotes necessários para o tokenizer.

        Returns:
            Lista de nomes de pacotes Python necessários.
        """
        package_map = {
            self.OPENAI: ["tiktoken"],
            self.HUGGINGFACE: ["transformers", "torch"],
            self.CUSTOM: [],
            self.DEFAULT: ["token-count"],
        }
        return package_map.get(self, [])
