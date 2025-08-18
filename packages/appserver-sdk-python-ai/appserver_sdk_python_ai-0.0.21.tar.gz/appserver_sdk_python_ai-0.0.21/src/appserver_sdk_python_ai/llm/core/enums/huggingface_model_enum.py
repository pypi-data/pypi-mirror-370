"""Enums para modelos HuggingFace suportados na biblioteca."""

from __future__ import annotations

from enum import Enum


class HuggingFaceModelEnum(str, Enum):
    """Modelos HuggingFace suportados para contagem de tokens."""

    # Modelos Sentence Transformers populares
    SENTENCE_TRANSFORMERS_ALL_MINILM_L6_V2 = "sentence-transformers/all-MiniLM-L6-v2"
    SENTENCE_TRANSFORMERS_ALL_MPNET_BASE_V2 = "sentence-transformers/all-mpnet-base-v2"
    SENTENCE_TRANSFORMERS_MULTI_QA_MPNET = (
        "sentence-transformers/multi-qa-mpnet-base-dot-v1"
    )
    SENTENCE_TRANSFORMERS_ALL_DISTILROBERTA_V1 = (
        "sentence-transformers/all-distilroberta-v1"
    )

    # Modelos BERT e variações
    BERT_BASE_UNCASED = "bert-base-uncased"
    BERT_BASE_CASED = "bert-base-cased"
    BERT_LARGE_UNCASED = "bert-large-uncased"
    BERT_LARGE_CASED = "bert-large-cased"

    # Modelos RoBERTa
    ROBERTA_BASE = "roberta-base"
    ROBERTA_LARGE = "roberta-large"

    # Modelos DistilBERT (mais leves)
    DISTILBERT_BASE_UNCASED = "distilbert-base-uncased"
    DISTILBERT_BASE_CASED = "distilbert-base-cased"

    # Modelos multilíngues
    BERT_BASE_MULTILINGUAL_UNCASED = "bert-base-multilingual-uncased"
    BERT_BASE_MULTILINGUAL_CASED = "bert-base-multilingual-cased"
    DISTILBERT_BASE_MULTILINGUAL_CASED = "distilbert-base-multilingual-cased"

    # Modelos para português
    NEURALMIND_BERT_BASE_PORTUGUESE_CASED = "neuralmind/bert-base-portuguese-cased"
    NEURALMIND_BERT_LARGE_PORTUGUESE_CASED = "neuralmind/bert-large-portuguese-cased"

    def get_max_sequence_length(self) -> int:
        """Retorna o comprimento máximo de sequência do modelo.

        Returns:
            Número máximo de tokens na sequência.
        """
        max_length_map = {
            # Sentence Transformers
            self.SENTENCE_TRANSFORMERS_ALL_MINILM_L6_V2: 256,
            self.SENTENCE_TRANSFORMERS_ALL_MPNET_BASE_V2: 384,
            self.SENTENCE_TRANSFORMERS_MULTI_QA_MPNET: 512,
            self.SENTENCE_TRANSFORMERS_ALL_DISTILROBERTA_V1: 512,
            # BERT models
            self.BERT_BASE_UNCASED: 512,
            self.BERT_BASE_CASED: 512,
            self.BERT_LARGE_UNCASED: 512,
            self.BERT_LARGE_CASED: 512,
            # RoBERTa models
            self.ROBERTA_BASE: 512,
            self.ROBERTA_LARGE: 512,
            # DistilBERT models
            self.DISTILBERT_BASE_UNCASED: 512,
            self.DISTILBERT_BASE_CASED: 512,
            # Multilingual models
            self.BERT_BASE_MULTILINGUAL_UNCASED: 512,
            self.BERT_BASE_MULTILINGUAL_CASED: 512,
            self.DISTILBERT_BASE_MULTILINGUAL_CASED: 512,
            # Portuguese models
            self.NEURALMIND_BERT_BASE_PORTUGUESE_CASED: 512,
            self.NEURALMIND_BERT_LARGE_PORTUGUESE_CASED: 512,
        }
        return max_length_map.get(self, 512)

    def is_sentence_transformer(self) -> bool:
        """Verifica se o modelo é um Sentence Transformer.

        Returns:
            True se for um modelo Sentence Transformer.
        """
        return "sentence-transformers" in self.value

    def is_multilingual(self) -> bool:
        """Verifica se o modelo suporta múltiplos idiomas.

        Returns:
            True se for um modelo multilíngue.
        """
        multilingual_keywords = ["multilingual", "portuguese", "neuralmind"]
        return any(keyword in self.value.lower() for keyword in multilingual_keywords)

    @classmethod
    def is_huggingface_model(cls, model_name: str) -> bool:
        """Verifica se um nome de modelo é um modelo HuggingFace conhecido.

        Args:
            model_name: Nome do modelo a verificar.

        Returns:
            True se for um modelo HuggingFace conhecido.
        """
        return model_name in [model.value for model in cls]

    @classmethod
    def get_portuguese_models(cls) -> list[HuggingFaceModelEnum]:
        """Retorna lista de modelos adequados para português.

        Returns:
            Lista de modelos que funcionam bem com português.
        """
        return [
            cls.NEURALMIND_BERT_BASE_PORTUGUESE_CASED,
            cls.NEURALMIND_BERT_LARGE_PORTUGUESE_CASED,
            cls.BERT_BASE_MULTILINGUAL_UNCASED,
            cls.BERT_BASE_MULTILINGUAL_CASED,
            cls.DISTILBERT_BASE_MULTILINGUAL_CASED,
            cls.SENTENCE_TRANSFORMERS_ALL_MPNET_BASE_V2,  # Funciona bem com PT
        ]
