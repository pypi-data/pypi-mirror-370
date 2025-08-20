from kaya_module_sdk.src.exceptions.files_not_found import FilesNotFoundException


def test_files_not_found_exception_default_error_code():
    """Test initialization with default error code."""
    exception = FilesNotFoundException("File not found")
    assert exception.message == "File not found"
    assert exception.error_code == 4


def test_files_not_found_exception_custom_error_code():
    """Test initialization with a custom error code."""
    exception = FilesNotFoundException("File not found", 404)
    assert exception.message == "File not found"
    assert exception.error_code == 404


def test_files_not_found_exception_string_representation():
    """Test the string representation of the exception."""
    exception = FilesNotFoundException("File not found", 404)
    assert str(exception) == "Error 404: File not found"
