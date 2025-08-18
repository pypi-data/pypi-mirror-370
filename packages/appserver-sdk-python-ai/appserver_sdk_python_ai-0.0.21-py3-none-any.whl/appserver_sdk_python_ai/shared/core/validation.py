"""Sistema de validação unificado para todos os módulos do SDK."""

import re
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any
from urllib.parse import urlparse

from appserver_sdk_python_ai.shared.exceptions import ValidationError


class BaseValidator(ABC):
    """Interface base para validadores."""

    @abstractmethod
    def validate(self, value: Any) -> bool:
        """Valida um valor."""
        pass

    @abstractmethod
    def get_error_message(self, value: Any) -> str:
        """Retorna mensagem de erro para valor inválido."""
        pass


class TypeValidator(BaseValidator):
    """Validador de tipo."""

    def __init__(
        self, expected_type: type | tuple[type, ...], allow_none: bool = False
    ):
        self.expected_type = expected_type
        self.allow_none = allow_none

    def validate(self, value: Any) -> bool:
        """Valida se o valor é do tipo esperado."""
        if value is None:
            return self.allow_none
        return isinstance(value, self.expected_type)

    def get_error_message(self, value: Any) -> str:
        """Retorna mensagem de erro."""
        if isinstance(self.expected_type, tuple):
            type_names = [t.__name__ for t in self.expected_type]
            expected_str = " ou ".join(type_names)
        else:
            expected_str = self.expected_type.__name__
        return f"Esperado tipo {expected_str}, recebido {type(value).__name__}"


class RangeValidator(BaseValidator):
    """Validador de intervalo numérico."""

    def __init__(
        self,
        min_value: int | float | None = None,
        max_value: int | float | None = None,
    ):
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value: Any) -> bool:
        """Valida se o valor está no intervalo."""
        if not isinstance(value, int | float):
            return False

        if self.min_value is not None and value < self.min_value:
            return False

        if self.max_value is not None and value > self.max_value:
            return False

        return True

    def get_error_message(self, value: Any) -> str:
        """Retorna mensagem de erro."""
        if self.min_value is not None and self.max_value is not None:
            return f"Valor deve estar entre {self.min_value} e {self.max_value}, recebido {value}"
        elif self.min_value is not None:
            return f"Valor deve ser maior ou igual a {self.min_value}, recebido {value}"
        elif self.max_value is not None:
            return f"Valor deve ser menor ou igual a {self.max_value}, recebido {value}"
        return f"Valor inválido: {value}"


class LengthValidator(BaseValidator):
    """Validador de comprimento para strings e listas."""

    def __init__(self, min_length: int | None = None, max_length: int | None = None):
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, value: Any) -> bool:
        """Valida o comprimento do valor."""
        if not hasattr(value, "__len__"):
            return False

        length = len(value)

        if self.min_length is not None and length < self.min_length:
            return False

        if self.max_length is not None and length > self.max_length:
            return False

        return True

    def get_error_message(self, value: Any) -> str:
        """Retorna mensagem de erro."""
        length = len(value) if hasattr(value, "__len__") else 0

        if self.min_length is not None and self.max_length is not None:
            return f"Comprimento deve estar entre {self.min_length} e {self.max_length}, recebido {length}"
        elif self.min_length is not None:
            return f"Comprimento deve ser maior ou igual a {self.min_length}, recebido {length}"
        elif self.max_length is not None:
            return f"Comprimento deve ser menor ou igual a {self.max_length}, recebido {length}"
        return f"Comprimento inválido: {length}"


class RegexValidator(BaseValidator):
    """Validador de expressão regular."""

    def __init__(self, pattern: str, flags: int = 0):
        self.pattern = pattern
        self.regex = re.compile(pattern, flags)

    def validate(self, value: Any) -> bool:
        """Valida se o valor corresponde ao padrão."""
        if not isinstance(value, str):
            return False
        return bool(self.regex.match(value))

    def get_error_message(self, value: Any) -> str:
        """Retorna mensagem de erro."""
        return f"Valor '{value}' não corresponde ao padrão esperado: {self.pattern}"


class URLValidator(BaseValidator):
    """Validador de URL."""

    def __init__(
        self, require_scheme: bool = True, allowed_schemes: list[str] | None = None
    ):
        self.require_scheme = require_scheme
        self.allowed_schemes = allowed_schemes or ["http", "https"]

    def validate(self, value: Any) -> bool:
        """Valida se o valor é uma URL válida."""
        if not isinstance(value, str):
            return False

        try:
            parsed = urlparse(value)

            if self.require_scheme and not parsed.scheme:
                return False

            if parsed.scheme and parsed.scheme not in self.allowed_schemes:
                return False

            return bool(parsed.netloc or not self.require_scheme)

        except Exception:
            return False

    def get_error_message(self, value: Any) -> str:
        """Retorna mensagem de erro."""
        return f"URL inválida: {value}. Esquemas permitidos: {', '.join(self.allowed_schemes)}"


class EmailValidator(BaseValidator):
    """Validador de email."""

    def __init__(self):
        # Padrão básico de email
        self.pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        self.regex = re.compile(self.pattern)

    def validate(self, value: Any) -> bool:
        """Valida se o valor é um email válido."""
        if not isinstance(value, str):
            return False
        return bool(self.regex.match(value))

    def get_error_message(self, value: Any) -> str:
        """Retorna mensagem de erro."""
        return f"Email inválido: {value}"


class ChoiceValidator(BaseValidator):
    """Validador de escolhas."""

    def __init__(self, choices: list[Any]):
        self.choices = choices

    def validate(self, value: Any) -> bool:
        """Valida se o valor está nas escolhas permitidas."""
        return value in self.choices

    def get_error_message(self, value: Any) -> str:
        """Retorna mensagem de erro."""
        return f"Valor '{value}' não está nas opções permitidas: {self.choices}"


class CustomValidator(BaseValidator):
    """Validador customizado usando função."""

    def __init__(self, validator_func: Callable[[Any], bool], error_message: str):
        self.validator_func = validator_func
        self.error_message = error_message

    def validate(self, value: Any) -> bool:
        """Valida usando função customizada."""
        try:
            return self.validator_func(value)
        except Exception:
            return False

    def get_error_message(self, value: Any) -> str:
        """Retorna mensagem de erro."""
        return self.error_message.format(value=value)


class ValidationRule:
    """Regra de validação para um campo."""

    def __init__(
        self,
        field_name: str,
        validators: list[BaseValidator],
        required: bool = True,
        default: Any = None,
    ):
        self.field_name = field_name
        self.validators = validators
        self.required = required
        self.default = default

    def validate(self, value: Any) -> list[str]:
        """Valida valor contra todas as regras."""
        errors = []

        # Verificar se é obrigatório
        if value is None:
            if self.required:
                errors.append(f"Campo '{self.field_name}' é obrigatório")
            return errors

        # Aplicar validadores
        for validator in self.validators:
            if not validator.validate(value):
                errors.append(
                    f"Campo '{self.field_name}': {validator.get_error_message(value)}"
                )

        return errors


class ValidationSchema:
    """Schema de validação para objetos."""

    def __init__(self, rules: list[ValidationRule]):
        self.rules = {rule.field_name: rule for rule in rules}

    def validate(
        self, data: dict[str, Any], strict: bool = False
    ) -> dict[str, list[str]]:
        """Valida dados contra o schema."""
        errors = {}
        validated_data = {}

        # Validar campos definidos no schema
        for field_name, rule in self.rules.items():
            value = data.get(field_name)

            # Usar valor padrão se não fornecido
            if value is None and rule.default is not None:
                value = rule.default
                validated_data[field_name] = value

            field_errors = rule.validate(value)
            if field_errors:
                errors[field_name] = field_errors
            elif value is not None:
                validated_data[field_name] = value

        # Em modo estrito, verificar campos extras
        if strict:
            extra_fields = set(data.keys()) - set(self.rules.keys())
            if extra_fields:
                errors["_extra_fields"] = [
                    f"Campos não permitidos: {', '.join(extra_fields)}"
                ]

        return errors

    def is_valid(self, data: dict[str, Any], strict: bool = False) -> bool:
        """Verifica se os dados são válidos."""
        errors = self.validate(data, strict)
        return len(errors) == 0

    def validate_and_raise(self, data: dict[str, Any], strict: bool = False) -> None:
        """Valida e levanta exceção se inválido."""
        errors = self.validate(data, strict)
        if errors:
            error_messages = []
            for _field, field_errors in errors.items():
                error_messages.extend(field_errors)
            raise ValidationError("Dados inválidos: " + "; ".join(error_messages))


class DataValidator:
    """Validador de dados unificado."""

    @staticmethod
    def validate_config(
        config_data: dict[str, Any], schema: ValidationSchema
    ) -> dict[str, Any]:
        """Valida configuração usando schema."""
        errors = schema.validate(config_data, strict=True)
        if errors:
            error_messages = []
            for _field, field_errors in errors.items():
                error_messages.extend(field_errors)
            raise ValidationError(f"Configuração inválida: {'; '.join(error_messages)}")

        return config_data

    @staticmethod
    def validate_network_config(config: dict[str, Any]) -> None:
        """Valida configurações de rede."""
        schema = ValidationSchema(
            [
                ValidationRule(
                    "timeout", [TypeValidator(int), RangeValidator(1, 300)], default=30
                ),
                ValidationRule(
                    "max_retries",
                    [TypeValidator(int), RangeValidator(0, 10)],
                    default=3,
                ),
                ValidationRule(
                    "retry_delay",
                    [TypeValidator((int, float)), RangeValidator(0, 60)],
                    default=1,
                ),
                ValidationRule(
                    "user_agent",
                    [TypeValidator(str), LengthValidator(1, 500)],
                    required=False,
                ),
                ValidationRule("headers", [TypeValidator(dict)], required=False),
            ]
        )

        schema.validate_and_raise(config)

    @staticmethod
    def validate_cache_config(config: dict[str, Any]) -> None:
        """Valida configurações de cache."""
        schema = ValidationSchema(
            [
                ValidationRule("enable_cache", [TypeValidator(bool)], default=True),
                ValidationRule(
                    "cache_ttl",
                    [TypeValidator(int), RangeValidator(1, 86400)],
                    default=3600,
                ),
                ValidationRule(
                    "max_cache_size",
                    [TypeValidator(int), RangeValidator(1, 10000)],
                    default=1000,
                ),
                ValidationRule("cache_dir", [TypeValidator(str)], required=False),
            ]
        )

        schema.validate_and_raise(config)

    @staticmethod
    def validate_logging_config(config: dict[str, Any]) -> None:
        """Valida configurações de logging."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        schema = ValidationSchema(
            [
                ValidationRule(
                    "level",
                    [TypeValidator(str), ChoiceValidator(valid_levels)],
                    default="INFO",
                ),
                ValidationRule("format", [TypeValidator(str)], required=False),
                ValidationRule("file_path", [TypeValidator(str)], required=False),
                ValidationRule(
                    "max_file_size",
                    [TypeValidator(int), RangeValidator(1, 1000)],
                    required=False,
                ),
                ValidationRule(
                    "backup_count",
                    [TypeValidator(int), RangeValidator(1, 100)],
                    required=False,
                ),
            ]
        )

        schema.validate_and_raise(config)

    @staticmethod
    def validate_security_config(config: dict[str, Any]) -> None:
        """Valida configurações de segurança."""
        schema = ValidationSchema(
            [
                ValidationRule("verify_ssl", [TypeValidator(bool)], default=True),
                ValidationRule("api_key", [TypeValidator(str)], required=False),
                ValidationRule("api_secret", [TypeValidator(str)], required=False),
                ValidationRule(
                    "allowed_domains", [TypeValidator(list)], required=False
                ),
                ValidationRule(
                    "rate_limit",
                    [TypeValidator(int), RangeValidator(1, 10000)],
                    required=False,
                ),
            ]
        )

        schema.validate_and_raise(config)


# Validadores pré-definidos comuns
COMMON_VALIDATORS = {
    "url": URLValidator(),
    "email": EmailValidator(),
    "positive_int": CustomValidator(
        lambda x: isinstance(x, int) and x > 0, "Deve ser um inteiro positivo"
    ),
    "non_empty_string": CustomValidator(
        lambda x: isinstance(x, str) and len(x.strip()) > 0,
        "Deve ser uma string não vazia",
    ),
    "file_path": CustomValidator(
        lambda x: isinstance(x, str) and len(x) > 0,
        "Deve ser um caminho de arquivo válido",
    ),
}
