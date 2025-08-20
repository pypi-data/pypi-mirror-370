from kaya_module_sdk.src.exceptions.kvl_failure import KVLFailureException


def test_kvl_failure_exception_default_error_code():
    """Test initialization with default error code."""
    exception = KVLFailureException("KVL failure occurred")
    assert exception.message == "KVL failure occurred"
    assert exception.error_code == 7


def test_kvl_failure_exception_custom_error_code():
    """Test initialization with a custom error code."""
    exception = KVLFailureException("KVL failure occurred", 503)
    assert exception.message == "KVL failure occurred"
    assert exception.error_code == 503


def test_kvl_failure_exception_string_representation():
    """Test the string representation of the exception."""
    exception = KVLFailureException("KVL failure occurred", 503)
    assert str(exception) == "Error 503: KVL failure occurred"
