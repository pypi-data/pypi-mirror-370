"""Smoke tests for kei_agent.input_validation module."""

def test_import_input_validation():
    """Test that input_validation module can be imported."""
    import kei_agent.input_validation


def test_import_validation_classes():
    """Test that validation classes can be imported."""
    from kei_agent.input_validation import (
        ValidationSeverity,
        ValidationResult,
        BaseValidator,
        stringValidator,
        JSONValidator,
        CompositeValidator,
        InputValidator,
    )


def test_validation_severity_enum():
    """Test basic ValidationSeverity enum usage."""
    from kei_agent.input_validation import ValidationSeverity

    assert hasattr(ValidationSeverity, 'ERROR')
    assert hasattr(ValidationSeverity, 'WARNING') or hasattr(ValidationSeverity, 'WARN')


def test_validation_result_creation():
    """Test basic ValidationResult instantiation."""
    from kei_agent.input_validation import ValidationResult

    result = ValidationResult(
        valid=True,
        sanitized_value="test-value"
    )
    assert result.valid is True
    assert result.sanitized_value == "test-value"


def test_string_validator_creation():
    """Test basic stringValidator instantiation."""
    from kei_agent.input_validation import stringValidator

    validator = stringValidator(
        name="test-string",
        min_length=1,
        max_length=100
    )
    assert validator.name == "test-string"
    assert hasattr(validator, 'validate')


def test_json_validator_creation():
    """Test basic JSONValidator instantiation."""
    from kei_agent.input_validation import JSONValidator

    validator = JSONValidator(
        name="test-json",
        max_depth=5
    )
    assert validator.name == "test-json"
    assert hasattr(validator, 'validate')


def test_composite_validator_creation():
    """Test basic CompositeValidator instantiation."""
    from kei_agent.input_validation import CompositeValidator

    validator = CompositeValidator(name="test-composite")
    assert validator.name == "test-composite"
    assert hasattr(validator, 'add_field')
    assert hasattr(validator, 'validate')


def test_input_validator_creation():
    """Test basic InputValidator instantiation."""
    from kei_agent.input_validation import InputValidator

    validator = InputValidator()
    assert validator is not None
    assert hasattr(validator, 'register_validator')
    assert hasattr(validator, 'validate')


def test_get_input_validator():
    """Test global input validator function."""
    from kei_agent.input_validation import get_input_validator

    validator = get_input_validator()
    assert validator is not None
    assert hasattr(validator, 'validate')
