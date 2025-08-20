from kaya_module_sdk.src.exceptions.malformed_results import MalformedResultsException


def test_malformed_results_exception_default_error_code():
    """Test initialization with default error code."""
    exception = MalformedResultsException("Malformed results occurred")
    assert exception.message == "Malformed results occurred"
    assert exception.error_code == 10


def test_malformed_results_exception_custom_error_code():
    """Test initialization with a custom error code."""
    exception = MalformedResultsException("Malformed results occurred", 400)
    assert exception.message == "Malformed results occurred"
    assert exception.error_code == 400


def test_malformed_results_exception_string_representation():
    """Test the string representation of the exception."""
    exception = MalformedResultsException("Malformed results occurred", 400)
    assert str(exception) == "Error 400: Malformed results occurred"
