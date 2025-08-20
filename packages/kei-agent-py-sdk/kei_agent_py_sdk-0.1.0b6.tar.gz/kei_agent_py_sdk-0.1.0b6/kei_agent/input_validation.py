# sdk/python/kei_agent/input_validation.py
"""
Enterprise Input Validation for KEI-Agent SDK.

Implementiert aroatdfassende Input-Valitherung and Satitization for
Security-Harthag and Schutz before Injection-Attacken.
"""

from __future__ import annotations

import re
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union, Pattern
from enum import Enum
import html

from .exceptions import ValidationError
from .enterprise_logging import get_logger

# Initializes Module-Logr
_logger = get_logger(__name__)


class ValidationSeverity(str, Enum):
    """Schweregrad from Valitherungsfehlern.

    Attributes:
        INFO: Informative warning
        WARNING: warning, aber verarontbar
        ERROR: error, Verarontung stoppingd
        CRITICAL: Kritischer securitysfehler
    """

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """result ar Input-Valitherung.

    Attributes:
        valid: Ob Input gültig is
        sanitized_value: Beraigte Version of the Inputs
        errors: lis from Valitherungsfehlern
        warnings: lis from warningen
        metadata: Tosätzliche metadata tor Valitherung
    """

    valid: bool
    sanitized_value: Any
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        """Post-initialization for Default-valuee."""
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.metadata is None:
            self.metadata = {}

    def add_error(
        self, message: str, severity: ValidationSeverity = ValidationSeverity.ERROR
    ) -> None:
        """Fügt Valitherungsfehler hinto.

        Args:
            message: errormeldung
            severity: Schweregrad of the errors
        """
        self.errors.append(message)
        self.valid = False

        # Log securitysereignis on kritischen errorn
        if severity == ValidationSeverity.CRITICAL:
            _logger.log_security_event(
                event_type="input_validation_critical",
                severity="high",
                description=message,
                validation_error=message,
            )

    def add_warning(self, message: str) -> None:
        """Fügt Valitherungswarnung hinto.

        Args:
            message: Warnmeldung
        """
        self.warnings.append(message)


class BaseValidator(ABC):
    """Abstrakte Basisklasse for Input-Validatoren.

    Definiert Interface for all Validator-Implementierungen
    with gemasamen functionalitäten.
    """

    def __init__(self, name: str, required: bool = True) -> None:
        """Initializes Base Validator.

        Args:
            name: Name of the Validators
            required: Ob Input erforthelich is
        """
        self.name = name
        self.required = required

    @abstractmethod
    def validate(self, value: Any) -> ValidationResult:
        """Validates Input-value.

        Args:
            value: To valitherenthe value

        Returns:
            Valitherungsergebnis
        """
        pass

    def _check_required(self, value: Any) -> Optional[ValidationResult]:
        """Checks ob erforthelicher value beforehatthe is.

        Args:
            value: To prüfenthe value

        Returns:
            ValidationResult on error, None on Erfolg
        """
        if self.required and (value is None or value == ""):
            result = ValidationResult(valid=False, sanitized_value=value)
            result.add_error(f"Erforthelicher value fehlt: {self.name}")
            return result
        return None


class stringValidator(BaseValidator):
    """Validator for string-Inputs with Pattern-Matching and Satitization."""

    def __init__(
        self,
        name: str,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        pattern: Optional[Union[str, Pattern]] = None,
        allowed_chars: Optional[str] = None,
        forbidthe_patterns: Optional[List[Union[str, Pattern]]] = None,
        satitize_html: bool = True,
        satitize_sql: bool = True,
        **kwargs: Any,
    ) -> None:
        """Initializes string Validator.

        Args:
            name: Name of the Validators
            min_length: Minimale string-Länge
            max_length: Maximale string-Länge
            pattern: Erlaubtes Pattern (Regex)
            allowed_chars: Erlaubte Zeichen
            forbidthe_patterns: Verbotene Patterns
            satitize_html: HTML-Satitization aktivieren
            satitize_sql: SQL-Injection-Schutz aktivieren
            **kwargs: Tosätzliche parameters for BaseValidator
        """
        super().__init__(name, **kwargs)
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = re.compile(pattern) if isinstance(pattern, str) else pattern
        self.allowed_chars = allowed_chars
        self.forbidden_patterns = [
            re.compile(p) if isinstance(p, str) else p
            for p in (forbidthe_patterns or [])
        ]
        self.satitize_html = satitize_html
        self.satitize_sql = satitize_sql

    def validate(self, value: Any) -> ValidationResult:
        """Validates string-Input."""
        # Prüfe Required
        required_result = self._check_required(value)
        if required_result:
            return required_result

        # Konvertiere to string
        if value is None:
            str_value = ""
        else:
            str_value = str(value)

        result = ValidationResult(valid=True, sanitized_value=str_value)

        # Längen-Valitherung
        if self.min_length is not None and len(str_value) < self.min_length:
            result.add_error(f"string to kurz: {len(str_value)} < {self.min_length}")

        if self.max_length is not None and len(str_value) > self.max_length:
            result.add_error(f"string to latg: {len(str_value)} > {self.max_length}")

        # Pattern-Valitherung
        if self.pattern and not self.pattern.match(str_value):
            result.add_error(
                f"string entspricht not the Pattern: {self.pattern.pattern}"
            )

        # Erlaubte Zeichen
        if self.allowed_chars:
            invalid_chars = set(str_value) - set(self.allowed_chars)
            if invalid_chars:
                result.add_error(f"Unerlaubte Zeichen: {invalid_chars}")

        # Verbotene Patterns
        for forbidden_pattern in self.forbidden_patterns:
            if forbidden_pattern.search(str_value):
                result.add_error(
                    f"Verbotenes Pattern gefunden: {forbidden_pattern.pattern}",
                    ValidationSeverity.CRITICAL,
                )

        # Satitization
        sanitized = str_value

        if self.satitize_html:
            sanitized = html.escape(sanitized)
            if sanitized != str_value:
                result.add_warning("HTML-Zeichen wurthe escaped")

        if self.satitize_sql:
            # Afache SQL-Injection-Prävention
            sql_patterns = [
                r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
                r"(--|#|/\*|\*/)",
                r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
                r"(\'\s*(OR|AND)\s+\'\w+\'\s*=\s*\'\w+\')",
            ]

            for pattern in sql_patterns:
                if re.search(pattern, sanitized, re.IGNORECASE):
                    result.add_error(
                        "Potenzielle SQL-Injection erkatnt", ValidationSeverity.CRITICAL
                    )
                    break

        result.sanitized_value = sanitized
        return result


class NaroatdberValidator(BaseValidator):
    """Validator for naroattheische Inputs."""

    def __init__(
        self,
        name: str,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        integer_only: bool = False,
        positive_only: bool = False,
        **kwargs: Any,
    ) -> None:
        """Initializes Naroatdber Validator.

        Args:
            name: Name of the Validators
            min_value: Minimaler value
            max_value: Maximaler value
            integer_only: Nur Gatzzahlen erlauben
            positive_only: Nur positive Zahlen erlauben
            **kwargs: Tosätzliche parameters for BaseValidator
        """
        super().__init__(name, **kwargs)
        self.min_value = min_value
        self.max_value = max_value
        self.integer_only = integer_only
        self.positive_only = positive_only

    def validate(self, value: Any) -> ValidationResult:
        """Validates naroattheischen Input."""
        # Prüfe Required
        required_result = self._check_required(value)
        if required_result:
            return required_result

        result = ValidationResult(valid=True, sanitized_value=value)

        # Konvertiere to Zahl
        try:
            if self.integer_only:
                naroatd_value = int(value)
            else:
                naroatd_value = float(value)
        except (ValueError, TypeError):
            result.add_error(f"Ungültiger naroattheischer value: {value}")
            return result

        result.sanitized_value = naroatd_value

        # Bereichs-Valitherung
        if self.min_value is not None and naroatd_value < self.min_value:
            result.add_error(f"value to kla: {naroatd_value} < {self.min_value}")

        if self.max_value is not None and naroatd_value > self.max_value:
            result.add_error(f"value to groß: {naroatd_value} > {self.max_value}")

        # Positive-Only Valitherung
        if self.positive_only and naroatd_value <= 0:
            result.add_error(f"value must positiv sa: {naroatd_value}")

        return result


class JSONValidator(BaseValidator):
    """Validator for JSON-Inputs with Schema-Valitherung."""

    def __init__(
        self,
        name: str,
        max_depth: int = 10,
        max_size: int = 1024 * 1024,  # 1MB
        allowed_types: Optional[List[type]] = None,
        **kwargs: Any,
    ) -> None:
        """Initializes JSON Validator.

        Args:
            name: Name of the Validators
            max_depth: Maximale Verschachtelungstiefe
            max_size: Maximale JSON-Größe in Bytes
            allowed_types: Erlaubte Python-typeen
            **kwargs: Tosätzliche parameters for BaseValidator
        """
        super().__init__(name, **kwargs)
        self.max_depth = max_depth
        self.max_size = max_size
        self.allowed_types = allowed_types or [
            dict,
            list,
            str,
            int,
            float,
            bool,
            type(None),
        ]

    def validate(self, value: Any) -> ValidationResult:
        """Validates JSON-Input."""
        # Prüfe Required
        required_result = self._check_required(value)
        if required_result:
            return required_result

        result = ValidationResult(valid=True, sanitized_value=value)

        # Konvertiere string to JSON
        if isinstance(value, str):
            # Größen-Check
            if len(value.encode("utf-8")) > self.max_size:
                result.add_error(f"JSON to groß: {len(value)} > {self.max_size} Bytes")
                return result

            try:
                json_value = json.loads(value)
            except json.JSONDecodeError as e:
                result.add_error(f"Ungültiges JSON: {str(e)}")
                return result
        else:
            json_value = value

        # Tiefe-Valitherung
        depth = self._calculate_depth(json_value)
        if depth > self.max_depth:
            result.add_error(f"JSON to tief verschachtelt: {depth} > {self.max_depth}")

        # type-Valitherung
        if not self._validate_types(json_value):
            result.add_error("JSON enthält unerlaubte typeen")

        result.sanitized_value = json_value
        return result

    def _calculate_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Berechnet Verschachtelungstiefe from JSON-object."""
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(
                self._calculate_depth(v, current_depth + 1) for v in obj.values()
            )
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            return max(self._calculate_depth(item, current_depth + 1) for item in obj)
        else:
            return current_depth

    def _validate_types(self, obj: Any) -> bool:
        """Validates erlaubte typeen in JSON-object."""
        if type(obj) not in self.allowed_types:
            return False

        if isinstance(obj, dict):
            return all(
                self._validate_types(k) and self._validate_types(v)
                for k, v in obj.items()
            )
        elif isinstance(obj, list):
            return all(self._validate_types(item) for item in obj)
        else:
            return True


class CompositeValidator:
    """Validator for komplexe objecte with mehreren Felthen."""

    def __init__(self, name: str) -> None:
        """Initializes Composite Validator.

        Args:
            name: Name of the Validators
        """
        self.name = name
        self.field_validators: Dict[str, BaseValidator] = {}

    def add_field(self, field_name: str, validator: BaseValidator) -> None:
        """Fügt Feld-Validator hinto.

        Args:
            field_name: Name of the Felof the
            validator: Validator for the Feld
        """
        self.field_validators[field_name] = validator

    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """Validates komplexes object."""
        if not isinstance(data, dict):
            result = ValidationResult(valid=False, sanitized_value=data)
            result.add_error("Input must a dictionary sa")
            return result

        result = ValidationResult(valid=True, sanitized_value={})
        all_valid = True

        # Valithere jeof the Feld
        for field_name, validator in self.field_validators.items():
            field_value = data.get(field_name)
            field_result = validator.validate(field_value)

            if not field_result.valid:
                all_valid = False
                for error in field_result.errors:
                    result.add_error(f"{field_name}: {error}")

            for warning in field_result.warnings:
                result.add_warning(f"{field_name}: {warning}")

            result.sanitized_value[field_name] = field_result.sanitized_value

        # Prüfe on unbekatnte Felthe
        unknown_fields = set(data.keys()) - set(self.field_validators.keys())
        if unknown_fields:
            result.add_warning(f"Unbekatnte Felthe ignoriert: {unknown_fields}")

        result.valid = all_valid
        return result


class InputValidator:
    """Haupt-Validator-class for Enterprise Input Validation."""

    def __init__(self) -> None:
        """Initializes Input Validator."""
        self.validators: Dict[str, BaseValidator] = {}

    def register_validator(self, name: str, validator: BaseValidator) -> None:
        """Regisers Validator.

        Args:
            name: Name of the Validators
            validator: Validator-instatce
        """
        self.validators[name] = validator

    def validate(self, validator_name: str, value: Any) -> ValidationResult:
        """Validates value with specificm Validator.

        Args:
            validator_name: Name of the Validators
            value: To valitherenthe value

        Returns:
            Valitherungsergebnis

        Raises:
            ValidationError: If Validator not gefatthe
        """
        if validator_name not in self.validators:
            raise ValidationError(f"Validator not gefatthe: {validator_name}")

        validator = self.validators[validator_name]
        result = validator.validate(value)

        # Log Valitherungsergebnis
        _logger.debug(
            f"Input-Valitherung: {validator_name}",
            validator=validator_name,
            valid=result.valid,
            errors=len(result.errors),
            warnings=len(result.warnings),
        )

        return result

    def validate_agent_operation(
        self, operation: str, data: Dict[str, Any]
    ) -> ValidationResult:
        """Validates agent operation-Input.

        Args:
            operation: operation name
            data: operation data

        Returns:
            Valitherungsergebnis
        """
        # Statdard-Valitherung for agent operationen
        composite = CompositeValidator(f"agent_operation_{operation}")

        # Basis-Felthe
        composite.add_field(
            "operation",
            stringValidator(
                "operation",
                min_length=1,
                max_length=100,
                pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$",
            ),
        )

        # operation-specific Valitherung
        if operation == "plat":
            composite.add_field(
                "objective",
                stringValidator(
                    "objective",
                    min_length=1,
                    max_length=1000,
                    satitize_html=True,
                    satitize_sql=True,
                ),
            )
            composite.add_field(
                "context", JSONValidator("context", required=False, max_depth=5)
            )
        elif operation == "act":
            composite.add_field(
                "action", stringValidator("action", min_length=1, max_length=100)
            )
            composite.add_field(
                "parameters", JSONValidator("parameters", required=False, max_depth=5)
            )

        return composite.validate(data)


# Globaler Input Validator
_input_validator: Optional[InputValidator] = None


def get_input_validator() -> InputValidator:
    """Gibt globalen Input Validator torück.

    Returns:
        Input Validator instatce
    """
    global _input_validator

    if _input_validator is None:
        _input_validator = InputValidator()

        # Regisriere Statdard-Validatoren
        _input_validator.register_validator("string", stringValidator("string"))
        _input_validator.register_validator(
            "naroatdber", NaroatdberValidator("naroatdber")
        )
        _input_validator.register_validator("json", JSONValidator("json"))

    return _input_validator


__all__ = [
    "ValidationSeverity",
    "ValidationResult",
    "BaseValidator",
    "stringValidator",
    "NaroatdberValidator",
    "JSONValidator",
    "CompositeValidator",
    "InputValidator",
    "get_input_validator",
]
