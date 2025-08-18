"""Sistema de validação robusta para o módulo LLM.

Este módulo implementa validadores para prevenir erros em runtime,
validando entradas, configurações e parâmetros do sistema.
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any


class ValidationLevel(Enum):
    """Níveis de validação."""

    STRICT = "strict"  # Validação rigorosa, falha em qualquer erro
    MODERATE = "moderate"  # Validação moderada, permite alguns avisos
    LENIENT = "lenient"  # Validação permissiva, apenas erros críticos


@dataclass
class ValidationResult:
    """Resultado de uma validação."""

    is_valid: bool
    errors: list[str]
    warnings: list[str]
    suggestions: list[str]

    def __post_init__(self):
        """Inicializa listas vazias se None."""
        self.errors = self.errors or []
        self.warnings = self.warnings or []
        self.suggestions = self.suggestions or []

    def add_error(self, message: str) -> None:
        """Adiciona um erro."""
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        """Adiciona um aviso."""
        self.warnings.append(message)

    def add_suggestion(self, message: str) -> None:
        """Adiciona uma sugestão."""
        self.suggestions.append(message)

    def merge(self, other: "ValidationResult") -> "ValidationResult":
        """Combina com outro resultado de validação."""
        return ValidationResult(
            is_valid=self.is_valid and other.is_valid,
            errors=self.errors + other.errors,
            warnings=self.warnings + other.warnings,
            suggestions=self.suggestions + other.suggestions,
        )

    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionário."""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "suggestions": self.suggestions,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
        }


class BaseValidator:
    """Classe base para validadores."""

    def __init__(self, level: ValidationLevel = ValidationLevel.MODERATE):
        self.level = level
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def validate(
        self, value: Any, context: dict[str, Any] | None = None
    ) -> ValidationResult:
        """Método principal de validação - deve ser implementado pelas subclasses."""
        raise NotImplementedError("Subclasses devem implementar o método validate")

    def _create_result(self, is_valid: bool = True) -> ValidationResult:
        """Cria um resultado de validação inicial."""
        return ValidationResult(
            is_valid=is_valid, errors=[], warnings=[], suggestions=[]
        )


class ModelNameValidator(BaseValidator):
    """Validador para nomes de modelos."""

    # Padrões válidos para nomes de modelos
    VALID_PATTERNS = [
        r"^gpt-[0-9]+(\.[0-9]+)?(-[a-z0-9-]+)?$",  # GPT models
        r"^text-[a-z0-9-]+$",  # OpenAI text models
        r"^[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+$",  # HuggingFace format
        r"^[a-z0-9-]+$",  # Simple names
        r"^[a-zA-Z0-9_.-]+$",  # General pattern
    ]

    KNOWN_PROVIDERS = {
        "openai": [r"^(gpt|text|davinci|curie|babbage|ada)-"],
        "huggingface": [r"^[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+$"],
        "anthropic": [r"^claude-"],
        "google": [r"^(palm|bard|gemini)-"],
        "meta": [r"^(llama|opt)-"],
        "microsoft": [r"^(turing|dialoGPT)-"],
    }

    def validate(
        self, model_name: Any, context: dict[str, Any] | None = None
    ) -> ValidationResult:
        """Valida nome de modelo."""
        result = self._create_result()

        # Verificação de tipo
        if not isinstance(model_name, str):
            result.add_error(
                f"Nome do modelo deve ser string, recebido: {type(model_name).__name__}"
            )
            return result

        # Verificação de vazio
        if not model_name.strip():
            result.add_error("Nome do modelo não pode estar vazio")
            return result

        model_name = model_name.strip()

        # Verificação de comprimento
        if len(model_name) > 200:
            result.add_error(
                f"Nome do modelo muito longo: {len(model_name)} caracteres (máximo: 200)"
            )

        if len(model_name) < 2:
            result.add_error(
                f"Nome do modelo muito curto: {len(model_name)} caracteres (mínimo: 2)"
            )

        # Verificação de caracteres inválidos
        if re.search(r'[<>:"|?*\\]', model_name):
            result.add_error(
                'Nome do modelo contém caracteres inválidos: < > : " | ? * \\'
            )

        # Verificação de padrões válidos
        is_valid_pattern = any(
            re.match(pattern, model_name) for pattern in self.VALID_PATTERNS
        )

        if not is_valid_pattern and self.level == ValidationLevel.STRICT:
            result.add_error(
                f"Nome do modelo '{model_name}' não segue padrões conhecidos"
            )
            result.add_suggestion(
                "Use formatos como: 'gpt-4', 'text-davinci-003', 'organization/model-name'"
            )
        elif not is_valid_pattern:
            result.add_warning(
                f"Nome do modelo '{model_name}' pode não seguir convenções padrão"
            )

        # Sugestões baseadas no provedor
        provider_detected = self._detect_provider(model_name)
        if provider_detected and context and context.get("expected_provider"):
            expected = context["expected_provider"].lower()
            if provider_detected != expected:
                result.add_warning(
                    f"Modelo parece ser do provedor '{provider_detected}', mas esperado '{expected}'"
                )

        return result

    def _detect_provider(self, model_name: str) -> str | None:
        """Detecta o provedor baseado no nome do modelo."""
        for provider, patterns in self.KNOWN_PROVIDERS.items():
            if any(re.search(pattern, model_name) for pattern in patterns):
                return provider
        return None


class TokenCountValidator(BaseValidator):
    """Validador para contagem de tokens."""

    def validate(
        self, token_count: Any, context: dict[str, Any] | None = None
    ) -> ValidationResult:
        """Valida contagem de tokens."""
        result = self._create_result()

        # Verificação de tipo
        if not isinstance(token_count, int | float):
            result.add_error(
                f"Contagem de tokens deve ser numérica, recebido: {type(token_count).__name__}"
            )
            return result

        # Conversão para int se for float
        if isinstance(token_count, float):
            if not token_count.is_integer():
                result.add_warning(
                    f"Contagem de tokens convertida de float para int: {token_count} -> {int(token_count)}"
                )
            token_count = int(token_count)

        # Verificação de valores válidos
        if token_count < 0:
            result.add_error(f"Contagem de tokens não pode ser negativa: {token_count}")

        if (
            token_count == 0
            and context
            and context.get("text")
            and context["text"].strip()
        ):
            result.add_warning("Contagem de tokens é zero para texto não vazio")

        # Verificação de limites razoáveis
        max_reasonable = context.get("max_tokens", 1000000) if context else 1000000
        if token_count > max_reasonable:
            result.add_warning(
                f"Contagem de tokens muito alta: {token_count} (máximo esperado: {max_reasonable})"
            )

        # Sugestões de otimização
        if token_count > 50000:
            result.add_suggestion(
                "Considere dividir textos muito longos para melhor performance"
            )

        return result


class ConfigValidator(BaseValidator):
    """Validador para configurações do LLM."""

    VALID_CONFIG_KEYS = {
        "timeout": (int, float),
        "max_retries": int,
        "max_tokens": int,
        "temperature": (int, float),
        "top_p": (int, float),
        "frequency_penalty": (int, float),
        "presence_penalty": (int, float),
        "api_key": str,
        "base_url": str,
        "model": str,
    }

    def validate(
        self, config: Any, context: dict[str, Any] | None = None
    ) -> ValidationResult:
        """Valida configuração do LLM."""
        result = self._create_result()

        # Verificação de tipo
        if not isinstance(config, dict):
            result.add_error(
                f"Configuração deve ser um dicionário, recebido: {type(config).__name__}"
            )
            return result

        # Validação de chaves e valores
        for key, value in config.items():
            key_result = self._validate_config_key(key, value)
            result = result.merge(key_result)

        # Validações específicas
        result = result.merge(self._validate_temperature(config.get("temperature")))
        result = result.merge(self._validate_token_limits(config.get("max_tokens")))
        result = result.merge(self._validate_penalties(config))

        return result

    def _validate_config_key(self, key: str, value: Any) -> ValidationResult:
        """Valida uma chave específica da configuração."""
        result = self._create_result()

        if key not in self.VALID_CONFIG_KEYS:
            if self.level == ValidationLevel.STRICT:
                result.add_error(f"Chave de configuração desconhecida: '{key}'")
            else:
                result.add_warning(f"Chave de configuração não reconhecida: '{key}'")
            return result

        expected_types = self.VALID_CONFIG_KEYS[key]
        if not isinstance(expected_types, tuple):
            expected_types = (expected_types,)

        if not isinstance(value, expected_types):
            type_names = " ou ".join(t.__name__ for t in expected_types)
            result.add_error(
                f"Tipo inválido para '{key}': esperado {type_names}, recebido {type(value).__name__}"
            )

        return result

    def _validate_temperature(self, temperature: Any) -> ValidationResult:
        """Valida parâmetro de temperatura."""
        result = self._create_result()

        if temperature is None:
            return result

        if not isinstance(temperature, int | float):
            result.add_error(
                f"Temperature deve ser numérica, recebido: {type(temperature).__name__}"
            )
            return result

        if temperature < 0 or temperature > 2:
            result.add_error(
                f"Temperature deve estar entre 0 e 2, recebido: {temperature}"
            )
        elif temperature > 1.5:
            result.add_warning(
                f"Temperature alta ({temperature}) pode gerar respostas inconsistentes"
            )
        elif temperature < 0.1:
            result.add_warning(
                f"Temperature baixa ({temperature}) pode gerar respostas repetitivas"
            )

        return result

    def _validate_token_limits(self, max_tokens: Any) -> ValidationResult:
        """Valida limites de tokens."""
        result = self._create_result()

        if max_tokens is None:
            return result

        if not isinstance(max_tokens, int):
            result.add_error(
                f"max_tokens deve ser inteiro, recebido: {type(max_tokens).__name__}"
            )
            return result

        if max_tokens <= 0:
            result.add_error(f"max_tokens deve ser positivo, recebido: {max_tokens}")
        elif max_tokens > 200000:
            result.add_warning(
                f"max_tokens muito alto ({max_tokens}), pode causar custos elevados"
            )
        elif max_tokens < 10:
            result.add_warning(
                f"max_tokens muito baixo ({max_tokens}), pode truncar respostas"
            )

        return result

    def _validate_penalties(self, config: dict[str, Any]) -> ValidationResult:
        """Valida parâmetros de penalidade."""
        result = self._create_result()

        for penalty_key in ["frequency_penalty", "presence_penalty"]:
            penalty = config.get(penalty_key)
            if penalty is None:
                continue

            if not isinstance(penalty, int | float):
                result.add_error(
                    f"{penalty_key} deve ser numérico, recebido: {type(penalty).__name__}"
                )
                continue

            if penalty < -2 or penalty > 2:
                result.add_error(
                    f"{penalty_key} deve estar entre -2 e 2, recebido: {penalty}"
                )

        return result


class TextValidator(BaseValidator):
    """Validador para textos de entrada."""

    def validate(
        self, text: Any, context: dict[str, Any] | None = None
    ) -> ValidationResult:
        """Valida texto de entrada."""
        result = self._create_result()

        # Verificação de tipo
        if not isinstance(text, str):
            result.add_error(f"Texto deve ser string, recebido: {type(text).__name__}")
            return result

        # Verificação de comprimento
        if len(text) == 0:
            result.add_warning("Texto vazio fornecido")
        elif len(text) > 1000000:  # 1MB de texto
            result.add_error(
                f"Texto muito longo: {len(text)} caracteres (máximo: 1,000,000)"
            )
        elif len(text) > 100000:  # 100KB
            result.add_warning(
                f"Texto longo: {len(text)} caracteres, pode afetar performance"
            )

        # Verificação de caracteres de controle
        control_chars = [c for c in text if ord(c) < 32 and c not in "\n\r\t"]
        if control_chars and self.level != ValidationLevel.LENIENT:
            result.add_warning(
                f"Texto contém {len(control_chars)} caracteres de controle"
            )

        # Verificação de encoding
        try:
            text.encode("utf-8")
        except UnicodeEncodeError as e:
            result.add_error(f"Erro de encoding UTF-8: {e}")

        # Sugestões
        if len(text.strip()) != len(text):
            result.add_suggestion(
                "Considere remover espaços em branco no início/fim do texto"
            )

        return result


class CompositeValidator:
    """Validador composto que combina múltiplos validadores."""

    def __init__(self, validators: list[BaseValidator]):
        self.validators = validators
        self.logger = logging.getLogger(f"{__name__}.CompositeValidator")

    def validate(
        self, value: Any, context: dict[str, Any] | None = None
    ) -> ValidationResult:
        """Executa todos os validadores e combina os resultados."""
        combined_result = ValidationResult(
            is_valid=True, errors=[], warnings=[], suggestions=[]
        )

        for validator in self.validators:
            try:
                result = validator.validate(value, context)
                combined_result = combined_result.merge(result)
            except Exception as e:
                self.logger.error(
                    f"Erro no validador {validator.__class__.__name__}: {e}"
                )
                combined_result.add_error(f"Erro interno de validação: {e}")

        return combined_result


# Instâncias globais dos validadores
model_name_validator = ModelNameValidator()
token_count_validator = TokenCountValidator()
config_validator = ConfigValidator()
text_validator = TextValidator()


def validate_model_name(
    model_name: str, level: ValidationLevel = ValidationLevel.MODERATE
) -> ValidationResult:
    """Valida nome de modelo."""
    validator = ModelNameValidator(level)
    return validator.validate(model_name)


def validate_token_count(
    token_count: int, context: dict[str, Any] | None = None
) -> ValidationResult:
    """Valida contagem de tokens."""
    return token_count_validator.validate(token_count, context)


def validate_config(
    config: dict[str, Any], level: ValidationLevel = ValidationLevel.MODERATE
) -> ValidationResult:
    """Valida configuração do LLM."""
    validator = ConfigValidator(level)
    return validator.validate(config)


def validate_text(
    text: str, level: ValidationLevel = ValidationLevel.MODERATE
) -> ValidationResult:
    """Valida texto de entrada."""
    validator = TextValidator(level)
    return validator.validate(text)


def validate_all(
    data: dict[str, Any], level: ValidationLevel = ValidationLevel.MODERATE
) -> dict[str, ValidationResult]:
    """Valida múltiplos tipos de dados de uma vez."""
    results = {}

    if "model_name" in data:
        results["model_name"] = validate_model_name(data["model_name"], level)

    if "token_count" in data:
        results["token_count"] = validate_token_count(data["token_count"])

    if "config" in data:
        results["config"] = validate_config(data["config"], level)

    if "text" in data:
        results["text"] = validate_text(data["text"], level)

    return results
