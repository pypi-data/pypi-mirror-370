from kaya_module_sdk.src.exceptions.kmetadata import KayaMetadataException


def test_kaya_metadata_exception_default_error_code():
    """Test initialization with default error code."""
    exception = KayaMetadataException("Metadata error occurred")
    assert exception.message == "Metadata error occurred"
    assert exception.error_code == 2


def test_kaya_metadata_exception_custom_error_code():
    """Test initialization with a custom error code."""
    exception = KayaMetadataException("Metadata error occurred", 404)
    assert exception.message == "Metadata error occurred"
    assert exception.error_code == 404


def test_kaya_metadata_exception_string_representation():
    """Test the string representation of the exception."""
    exception = KayaMetadataException("Metadata error occurred", 404)
    assert str(exception) == "Error 404: Metadata error occurred"
