from kaya_module_sdk.src.exceptions.module_not_found import ModuleNotFoundException


def test_module_not_found_exception_default_error_code():
    """Test initialization with default error code."""
    exception = ModuleNotFoundException("Module not found")
    assert exception.message == "Module not found"
    assert exception.error_code == 8


def test_module_not_found_exception_custom_error_code():
    """Test initialization with a custom error code."""
    exception = ModuleNotFoundException("Module not found", 404)
    assert exception.message == "Module not found"
    assert exception.error_code == 404


def test_module_not_found_exception_string_representation():
    """Test the string representation of the exception."""
    exception = ModuleNotFoundException("Module not found", 404)
    assert str(exception) == "Error 404: Module not found"
