"""Enums para modelos OpenAI suportados na biblioteca."""

from __future__ import annotations

from enum import Enum


class OpenAIModelEnum(str, Enum):
    """Modelos OpenAI suportados para contagem de tokens."""

    # Modelos GPT
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_3_5_TURBO = "gpt-3.5-turbo"

    # Modelos de Embedding
    TEXT_EMBEDDING_ADA_002 = "text-embedding-ada-002"
    TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"
    TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"

    # Modelos mais antigos (para compatibilidade)
    TEXT_DAVINCI_003 = "text-davinci-003"
    TEXT_CURIE_001 = "text-curie-001"

    def get_encoding_name(self) -> str:
        """Retorna o nome do encoding tiktoken apropriado para o modelo.

        Returns:
            Nome do encoding para usar com tiktoken.
        """
        encoding_map = {
            self.GPT_4O: "o200k_base",
            self.GPT_4O_MINI: "o200k_base",
            self.GPT_4: "cl100k_base",
            self.GPT_4_TURBO: "cl100k_base",
            self.GPT_3_5_TURBO: "cl100k_base",
            self.TEXT_EMBEDDING_ADA_002: "cl100k_base",
            self.TEXT_EMBEDDING_3_SMALL: "cl100k_base",
            self.TEXT_EMBEDDING_3_LARGE: "cl100k_base",
            self.TEXT_DAVINCI_003: "p50k_base",
            self.TEXT_CURIE_001: "p50k_base",
        }
        return encoding_map.get(self, "cl100k_base")

    def get_max_tokens(self) -> int:
        """Retorna o limite máximo de tokens do modelo.

        Returns:
            Número máximo de tokens suportados pelo modelo.
        """
        max_tokens_map = {
            self.GPT_4O: 128_000,
            self.GPT_4O_MINI: 128_000,
            self.GPT_4: 8_192,
            self.GPT_4_TURBO: 128_000,
            self.GPT_3_5_TURBO: 4_096,
            self.TEXT_EMBEDDING_ADA_002: 8_191,
            self.TEXT_EMBEDDING_3_SMALL: 8_191,
            self.TEXT_EMBEDDING_3_LARGE: 8_191,
            self.TEXT_DAVINCI_003: 4_097,
            self.TEXT_CURIE_001: 2_049,
        }
        return max_tokens_map.get(self, 4_096)

    @classmethod
    def is_openai_model(cls, model_name: str) -> bool:
        """Verifica se um nome de modelo é um modelo OpenAI conhecido.

        Args:
            model_name: Nome do modelo a verificar.

        Returns:
            True se for um modelo OpenAI conhecido.
        """
        return model_name in [model.value for model in cls]
