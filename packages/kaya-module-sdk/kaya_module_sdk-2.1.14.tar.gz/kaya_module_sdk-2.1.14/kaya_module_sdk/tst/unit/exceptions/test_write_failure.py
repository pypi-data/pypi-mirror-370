from kaya_module_sdk.src.exceptions.write_failure import WriteFailureException


def test_write_failure_exception_default_error_code():
    """Test initialization with default error code."""
    exception = WriteFailureException("Write operation failed")
    assert exception.message == "Write operation failed"
    assert exception.error_code == 12


def test_write_failure_exception_custom_error_code():
    """Test initialization with a custom error code."""
    exception = WriteFailureException("Write operation failed", 500)
    assert exception.message == "Write operation failed"
    assert exception.error_code == 500


def test_write_failure_exception_string_representation():
    """Test the string representation of the exception."""
    exception = WriteFailureException("Write operation failed", 500)
    assert str(exception) == "Error 500: Write operation failed"
