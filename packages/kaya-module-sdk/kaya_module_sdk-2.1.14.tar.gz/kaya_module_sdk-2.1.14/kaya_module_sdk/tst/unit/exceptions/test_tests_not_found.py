from kaya_module_sdk.src.exceptions.tests_not_found import (
    TestsNotFoundException as TNFException,
)


def test_tests_not_found_exception_default_error_code():
    """Test initialization with default error code."""
    exception = TNFException("Tests not found")
    assert exception.message == "Tests not found"
    assert exception.error_code == 5


def test_tests_not_found_exception_custom_error_code():
    """Test initialization with a custom error code."""
    exception = TNFException("Tests not found", 404)
    assert exception.message == "Tests not found"
    assert exception.error_code == 404


def test_tests_not_found_exception_string_representation():
    """Test the string representation of the exception."""
    exception = TNFException("Tests not found", 404)
    assert str(exception) == "Error 404: Tests not found"
