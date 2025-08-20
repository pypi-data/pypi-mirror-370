from kaya_module_sdk.src.exceptions.kunimplemented import KayaUnimplementedException


def test_kaya_unimplemented_exception_default_error_code():
    """Test initialization with default error code."""
    exception = KayaUnimplementedException("Feature not implemented")
    assert exception.message == "Feature not implemented"
    assert exception.error_code == 1


def test_kaya_unimplemented_exception_custom_error_code():
    """Test initialization with a custom error code."""
    exception = KayaUnimplementedException("Feature not implemented", 501)
    assert exception.message == "Feature not implemented"
    assert exception.error_code == 501


def test_kaya_unimplemented_exception_string_representation():
    """Test the string representation of the exception."""
    exception = KayaUnimplementedException("Feature not implemented", 501)
    assert str(exception) == "Error 501: Feature not implemented"
