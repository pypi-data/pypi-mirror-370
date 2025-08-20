from kaya_module_sdk.src.exceptions.kit_failure import KITFailureException


def test_kit_failure_exception_default_error_code():
    """Test initialization with default error code."""
    exception = KITFailureException("KIT failure occurred")
    assert exception.message == "KIT failure occurred"
    assert exception.error_code == 6


def test_kit_failure_exception_custom_error_code():
    """Test initialization with a custom error code."""
    exception = KITFailureException("KIT failure occurred", 500)
    assert exception.message == "KIT failure occurred"
    assert exception.error_code == 500


def test_kit_failure_exception_string_representation():
    """Test the string representation of the exception."""
    exception = KITFailureException("KIT failure occurred", 500)
    assert str(exception) == "Error 500: KIT failure occurred"
