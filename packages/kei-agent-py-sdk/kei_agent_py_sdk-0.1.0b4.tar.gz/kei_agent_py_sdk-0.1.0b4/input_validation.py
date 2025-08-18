# sdk/python/kei_agent/input_validation.py
"""
Enterprise Input Validation für KEI-Agent SDK.

Implementiert umfassende Input-Validierung und Sanitization für
Security-Hardening und Schutz vor Injection-Attacken.
"""

from __future__ import annotations

import re
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union, Pattern
from enum import Enum
import html

from exceptions import ValidationError
from enterprise_logging import get_logger

# Initialisiert Modul-Logger
_logger = get_logger(__name__)


class ValidationSeverity(str, Enum):
    """Schweregrad von Validierungsfehlern.

    Attributes:
        INFO: Informative Warnung
        WARNING: Warnung, aber verarbeitbar
        ERROR: Fehler, Verarbeitung gestoppt
        CRITICAL: Kritischer Sicherheitsfehler
    """

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Ergebnis einer Input-Validierung.

    Attributes:
        valid: Ob Input gültig ist
        sanitized_value: Bereinigte Version des Inputs
        errors: Liste von Validierungsfehlern
        warnings: Liste von Warnungen
        metadata: Zusätzliche Metadaten zur Validierung
    """

    valid: bool
    sanitized_value: Any
    errors: List[str] = None
    warnings: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """Post-Initialisierung für Default-Werte."""
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.metadata is None:
            self.metadata = {}

    def add_error(
        self, message: str, severity: ValidationSeverity = ValidationSeverity.ERROR
    ) -> None:
        """Fügt Validierungsfehler hinzu.

        Args:
            message: Fehlermeldung
            severity: Schweregrad des Fehlers
        """
        self.errors.append(message)
        self.valid = False

        # Logge Sicherheitsereignis bei kritischen Fehlern
        if severity == ValidationSeverity.CRITICAL:
            _logger.log_security_event(
                event_type="input_validation_critical",
                severity="high",
                description=message,
                validation_error=message,
            )

    def add_warning(self, message: str) -> None:
        """Fügt Validierungswarnung hinzu.

        Args:
            message: Warnmeldung
        """
        self.warnings.append(message)


class BaseValidator(ABC):
    """Abstrakte Basisklasse für Input-Validatoren.

    Definiert Interface für alle Validator-Implementierungen
    mit gemeinsamen Funktionalitäten.
    """

    def __init__(self, name: str, required: bool = True) -> None:
        """Initialisiert Base Validator.

        Args:
            name: Name des Validators
            required: Ob Input erforderlich ist
        """
        self.name = name
        self.required = required

    @abstractmethod
    def validate(self, value: Any) -> ValidationResult:
        """Validiert Input-Wert.

        Args:
            value: Zu validierender Wert

        Returns:
            Validierungsergebnis
        """
        pass

    def _check_required(self, value: Any) -> Optional[ValidationResult]:
        """Prüft ob erforderlicher Wert vorhanden ist.

        Args:
            value: Zu prüfender Wert

        Returns:
            ValidationResult bei Fehler, None bei Erfolg
        """
        if self.required and (value is None or value == ""):
            result = ValidationResult(valid=False, sanitized_value=value)
            result.add_error(f"Erforderlicher Wert fehlt: {self.name}")
            return result
        return None


class StringValidator(BaseValidator):
    """Validator für String-Inputs mit Pattern-Matching und Sanitization."""

    def __init__(
        self,
        name: str,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        pattern: Optional[Union[str, Pattern]] = None,
        allowed_chars: Optional[str] = None,
        forbidden_patterns: Optional[List[Union[str, Pattern]]] = None,
        sanitize_html: bool = True,
        sanitize_sql: bool = True,
        **kwargs: Any,
    ) -> None:
        """Initialisiert String Validator.

        Args:
            name: Name des Validators
            min_length: Minimale String-Länge
            max_length: Maximale String-Länge
            pattern: Erlaubtes Pattern (Regex)
            allowed_chars: Erlaubte Zeichen
            forbidden_patterns: Verbotene Patterns
            sanitize_html: HTML-Sanitization aktivieren
            sanitize_sql: SQL-Injection-Schutz aktivieren
            **kwargs: Zusätzliche Parameter für BaseValidator
        """
        super().__init__(name, **kwargs)
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = re.compile(pattern) if isinstance(pattern, str) else pattern
        self.allowed_chars = allowed_chars
        self.forbidden_patterns = [
            re.compile(p) if isinstance(p, str) else p
            for p in (forbidden_patterns or [])
        ]
        self.sanitize_html = sanitize_html
        self.sanitize_sql = sanitize_sql

    def validate(self, value: Any) -> ValidationResult:
        """Validiert String-Input."""
        # Prüfe Required
        required_result = self._check_required(value)
        if required_result:
            return required_result

        # Konvertiere zu String
        if value is None:
            str_value = ""
        else:
            str_value = str(value)

        result = ValidationResult(valid=True, sanitized_value=str_value)

        # Längen-Validierung
        if self.min_length is not None and len(str_value) < self.min_length:
            result.add_error(f"String zu kurz: {len(str_value)} < {self.min_length}")

        if self.max_length is not None and len(str_value) > self.max_length:
            result.add_error(f"String zu lang: {len(str_value)} > {self.max_length}")

        # Pattern-Validierung
        if self.pattern and not self.pattern.match(str_value):
            result.add_error(
                f"String entspricht nicht dem Pattern: {self.pattern.pattern}"
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

        # Sanitization
        sanitized = str_value

        if self.sanitize_html:
            sanitized = html.escape(sanitized)
            if sanitized != str_value:
                result.add_warning("HTML-Zeichen wurden escaped")

        if self.sanitize_sql:
            # Einfache SQL-Injection-Prävention
            sql_patterns = [
                r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
                r"(--|#|/\*|\*/)",
                r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
                r"(\'\s*(OR|AND)\s+\'\w+\'\s*=\s*\'\w+\')",
            ]

            for pattern in sql_patterns:
                if re.search(pattern, sanitized, re.IGNORECASE):
                    result.add_error(
                        "Potenzielle SQL-Injection erkannt", ValidationSeverity.CRITICAL
                    )
                    break

        result.sanitized_value = sanitized
        return result


class NumberValidator(BaseValidator):
    """Validator für numerische Inputs."""

    def __init__(
        self,
        name: str,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        integer_only: bool = False,
        positive_only: bool = False,
        **kwargs: Any,
    ) -> None:
        """Initialisiert Number Validator.

        Args:
            name: Name des Validators
            min_value: Minimaler Wert
            max_value: Maximaler Wert
            integer_only: Nur Ganzzahlen erlauben
            positive_only: Nur positive Zahlen erlauben
            **kwargs: Zusätzliche Parameter für BaseValidator
        """
        super().__init__(name, **kwargs)
        self.min_value = min_value
        self.max_value = max_value
        self.integer_only = integer_only
        self.positive_only = positive_only

    def validate(self, value: Any) -> ValidationResult:
        """Validiert numerischen Input."""
        # Prüfe Required
        required_result = self._check_required(value)
        if required_result:
            return required_result

        result = ValidationResult(valid=True, sanitized_value=value)

        # Konvertiere zu Zahl
        try:
            if self.integer_only:
                num_value = int(value)
            else:
                num_value = float(value)
        except (ValueError, TypeError):
            result.add_error(f"Ungültiger numerischer Wert: {value}")
            return result

        result.sanitized_value = num_value

        # Bereichs-Validierung
        if self.min_value is not None and num_value < self.min_value:
            result.add_error(f"Wert zu klein: {num_value} < {self.min_value}")

        if self.max_value is not None and num_value > self.max_value:
            result.add_error(f"Wert zu groß: {num_value} > {self.max_value}")

        # Positive-Only Validierung
        if self.positive_only and num_value <= 0:
            result.add_error(f"Wert muss positiv sein: {num_value}")

        return result


class JSONValidator(BaseValidator):
    """Validator für JSON-Inputs mit Schema-Validierung."""

    def __init__(
        self,
        name: str,
        max_depth: int = 10,
        max_size: int = 1024 * 1024,  # 1MB
        allowed_types: Optional[List[type]] = None,
        **kwargs: Any,
    ) -> None:
        """Initialisiert JSON Validator.

        Args:
            name: Name des Validators
            max_depth: Maximale Verschachtelungstiefe
            max_size: Maximale JSON-Größe in Bytes
            allowed_types: Erlaubte Python-Typen
            **kwargs: Zusätzliche Parameter für BaseValidator
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
        """Validiert JSON-Input."""
        # Prüfe Required
        required_result = self._check_required(value)
        if required_result:
            return required_result

        result = ValidationResult(valid=True, sanitized_value=value)

        # Konvertiere String zu JSON
        if isinstance(value, str):
            # Größen-Check
            if len(value.encode("utf-8")) > self.max_size:
                result.add_error(f"JSON zu groß: {len(value)} > {self.max_size} Bytes")
                return result

            try:
                json_value = json.loads(value)
            except json.JSONDecodeError as e:
                result.add_error(f"Ungültiges JSON: {str(e)}")
                return result
        else:
            json_value = value

        # Tiefe-Validierung
        depth = self._calculate_depth(json_value)
        if depth > self.max_depth:
            result.add_error(f"JSON zu tief verschachtelt: {depth} > {self.max_depth}")

        # Typ-Validierung
        if not self._validate_types(json_value):
            result.add_error("JSON enthält unerlaubte Typen")

        result.sanitized_value = json_value
        return result

    def _calculate_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Berechnet Verschachtelungstiefe von JSON-Objekt."""
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
        """Validiert erlaubte Typen in JSON-Objekt."""
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
    """Validator für komplexe Objekte mit mehreren Feldern."""

    def __init__(self, name: str) -> None:
        """Initialisiert Composite Validator.

        Args:
            name: Name des Validators
        """
        self.name = name
        self.field_validators: Dict[str, BaseValidator] = {}

    def add_field(self, field_name: str, validator: BaseValidator) -> None:
        """Fügt Feld-Validator hinzu.

        Args:
            field_name: Name des Feldes
            validator: Validator für das Feld
        """
        self.field_validators[field_name] = validator

    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """Validiert komplexes Objekt."""
        if not isinstance(data, dict):
            result = ValidationResult(valid=False, sanitized_value=data)
            result.add_error("Input muss ein Dictionary sein")
            return result

        result = ValidationResult(valid=True, sanitized_value={})
        all_valid = True

        # Validiere jedes Feld
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

        # Prüfe auf unbekannte Felder
        unknown_fields = set(data.keys()) - set(self.field_validators.keys())
        if unknown_fields:
            result.add_warning(f"Unbekannte Felder ignoriert: {unknown_fields}")

        result.valid = all_valid
        return result


class InputValidator:
    """Haupt-Validator-Klasse für Enterprise Input Validation."""

    def __init__(self) -> None:
        """Initialisiert Input Validator."""
        self.validators: Dict[str, BaseValidator] = {}

    def register_validator(self, name: str, validator: BaseValidator) -> None:
        """Registriert Validator.

        Args:
            name: Name des Validators
            validator: Validator-Instanz
        """
        self.validators[name] = validator

    def validate(self, validator_name: str, value: Any) -> ValidationResult:
        """Validiert Wert mit spezifischem Validator.

        Args:
            validator_name: Name des Validators
            value: Zu validierender Wert

        Returns:
            Validierungsergebnis

        Raises:
            ValidationError: Wenn Validator nicht gefunden
        """
        if validator_name not in self.validators:
            raise ValidationError(f"Validator nicht gefunden: {validator_name}")

        validator = self.validators[validator_name]
        result = validator.validate(value)

        # Logge Validierungsergebnis
        _logger.debug(
            f"Input-Validierung: {validator_name}",
            validator=validator_name,
            valid=result.valid,
            errors=len(result.errors),
            warnings=len(result.warnings),
        )

        return result

    def validate_agent_operation(
        self, operation: str, data: Dict[str, Any]
    ) -> ValidationResult:
        """Validiert Agent-Operation-Input.

        Args:
            operation: Name der Operation
            data: Operation-Daten

        Returns:
            Validierungsergebnis
        """
        # Standard-Validierung für Agent-Operationen
        composite = CompositeValidator(f"agent_operation_{operation}")

        # Basis-Felder
        composite.add_field(
            "operation",
            StringValidator(
                "operation",
                min_length=1,
                max_length=100,
                pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$",
            ),
        )

        # Operation-spezifische Validierung
        if operation == "plan":
            composite.add_field(
                "objective",
                StringValidator(
                    "objective",
                    min_length=1,
                    max_length=1000,
                    sanitize_html=True,
                    sanitize_sql=True,
                ),
            )
            composite.add_field(
                "context", JSONValidator("context", required=False, max_depth=5)
            )
        elif operation == "act":
            composite.add_field(
                "action", StringValidator("action", min_length=1, max_length=100)
            )
            composite.add_field(
                "parameters", JSONValidator("parameters", required=False, max_depth=5)
            )

        return composite.validate(data)


# Globaler Input Validator
_input_validator: Optional[InputValidator] = None


def get_input_validator() -> InputValidator:
    """Gibt globalen Input Validator zurück.

    Returns:
        Input Validator Instanz
    """
    global _input_validator

    if _input_validator is None:
        _input_validator = InputValidator()

        # Registriere Standard-Validatoren
        _input_validator.register_validator("string", StringValidator("string"))
        _input_validator.register_validator("number", NumberValidator("number"))
        _input_validator.register_validator("json", JSONValidator("json"))

    return _input_validator


__all__ = [
    "ValidationSeverity",
    "ValidationResult",
    "BaseValidator",
    "StringValidator",
    "NumberValidator",
    "JSONValidator",
    "CompositeValidator",
    "InputValidator",
    "get_input_validator",
]
