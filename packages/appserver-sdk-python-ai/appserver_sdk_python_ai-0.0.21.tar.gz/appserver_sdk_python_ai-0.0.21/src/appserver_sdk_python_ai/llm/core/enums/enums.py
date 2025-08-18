"""Enumerações para modelos de tokenização."""

from __future__ import annotations

from enum import Enum


class ModelType(str, Enum):
    """Tipos de modelos de IA."""

    CHAT = "chat"
    COMPLETION = "completion"
    EMBEDDING = "embedding"
    IMAGE = "image"
    AUDIO = "audio"
    MULTIMODAL = "multimodal"


class ModelProvider(str, Enum):
    """Provedores de modelos de IA."""

    OPENAI = "openai"
    HUGGINGFACE = "huggingface"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    COHERE = "cohere"
    CUSTOM = "custom"


class ModelCapability(str, Enum):
    """Capacidades dos modelos."""

    TEXT_GENERATION = "text_generation"
    TEXT_EMBEDDING = "text_embedding"
    IMAGE_GENERATION = "image_generation"
    IMAGE_UNDERSTANDING = "image_understanding"
    AUDIO_TRANSCRIPTION = "audio_transcription"
    AUDIO_GENERATION = "audio_generation"
    CODE_GENERATION = "code_generation"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    QUESTION_ANSWERING = "question_answering"


class SupportedLanguage(str, Enum):
    """Idiomas suportados pelos modelos."""

    PORTUGUESE = "pt"
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    RUSSIAN = "ru"
    MULTILINGUAL = "multilingual"


class TokenizationMethod(str, Enum):
    """Métodos de tokenização."""

    TIKTOKEN = "tiktoken"
    HUGGINGFACE = "huggingface"
    SENTENCEPIECE = "sentencepiece"
    WORDPIECE = "wordpiece"
    BPE = "bpe"
    FALLBACK = "fallback"


class TokenizerTypeEnum(Enum):
    """Tipos de tokenizadores disponíveis."""

    OPENAI = "openai"
    HUGGINGFACE = "huggingface"
    CUSTOM = "custom"
    DEFAULT = "default"


class OpenAIModelEnum(Enum):
    """Modelos OpenAI disponíveis."""

    GPT_4 = "gpt-4"
    GPT_4O = "gpt-4o"
    GPT_3_5_TURBO = "gpt-3.5-turbo"

    def get_max_tokens(self) -> int:
        """Retorna limite máximo de tokens."""
        limits = {
            "gpt-4": 8192,
            "gpt-4o": 128000,
            "gpt-3.5-turbo": 4096,
        }
        return limits.get(self.value, 4096)

    def get_encoding_name(self) -> str:
        """Retorna nome do encoding."""
        return "cl100k_base"


class HuggingFaceModelEnum(Enum):
    """Modelos HuggingFace disponíveis."""

    BERT_BASE = "bert-base-uncased"
    ROBERTA_BASE = "roberta-base"

    def get_max_sequence_length(self) -> int:
        """Retorna comprimento máximo da sequência."""
        return 512

    @classmethod
    def get_portuguese_models(cls) -> list[HuggingFaceModelEnum]:
        """Retorna modelos adequados para português."""
        return [cls.BERT_BASE]
