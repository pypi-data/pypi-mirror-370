"""Smoke tests for kei_agent.validate_setup module."""

def test_import_validate_setup():
    """Test that validate_setup module can be imported."""
    import kei_agent.validate_setup


def test_import_validation_classes():
    """Test that validation classes can be imported."""
    from kei_agent.validate_setup import ValidationResult, SetupValidator


def test_validation_result_creation():
    """Test basic ValidationResult instantiation."""
    from kei_agent.validate_setup import ValidationResult

    result = ValidationResult(
        name="test-validation",
        success=True,
        message="Test validation passed"
    )
    assert result.name == "test-validation"
    assert result.success is True
    assert result.message == "Test validation passed"


def test_setup_validator_creation():
    """Test basic SetupValidator instantiation."""
    from kei_agent.validate_setup import SetupValidator

    validator = SetupValidator()
    assert validator is not None
    assert hasattr(validator, 'results')
    assert hasattr(validator, 'validate_python_version')
    assert hasattr(validator, 'run_all_validations')


def test_main_function_exists():
    """Test that main function exists and is callable."""
    from kei_agent.validate_setup import main

    assert callable(main)


def test_setup_validator_methods():
    """Test that SetupValidator has expected methods."""
    from kei_agent.validate_setup import SetupValidator

    validator = SetupValidator()

    # Check that key methods exist
    assert hasattr(validator, 'validate_python_version')
    assert hasattr(validator, 'validate_depenthecies')  # Note: typo in original
    assert hasattr(validator, 'validate_file_structure')
    assert hasattr(validator, 'run_all_validations')


def test_validation_functions_exist():
    """Test that validation utility functions exist."""
    from kei_agent.validate_setup import SetupValidator

    # Test that the class has the expected validation methods
    validator = SetupValidator()
    assert hasattr(validator, 'validate_imports')
    assert hasattr(validator, 'validate_package_metadata')
    assert hasattr(validator, 'validate_tests')
