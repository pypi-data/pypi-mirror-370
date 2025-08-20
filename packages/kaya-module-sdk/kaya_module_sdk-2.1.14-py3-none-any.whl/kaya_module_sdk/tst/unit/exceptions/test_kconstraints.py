from kaya_module_sdk.src.exceptions.kconstraint import KayaConstraintException


def test_kaya_constraint_exception_default_error_code():
    """Test initialization with default error code."""
    exception = KayaConstraintException("Constraint violation")
    assert exception.message == "Constraint violation"
    assert exception.error_code == 3


def test_kaya_constraint_exception_custom_error_code():
    """Test initialization with a custom error code."""
    exception = KayaConstraintException("Constraint violation", 400)
    assert exception.message == "Constraint violation"
    assert exception.error_code == 400


def test_kaya_constraint_exception_string_representation():
    """Test the string representation of the exception."""
    exception = KayaConstraintException("Constraint violation", 400)
    assert str(exception) == "Error 400: Constraint violation"
