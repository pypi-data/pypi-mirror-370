from kaya_module_sdk.src.exceptions.web_server_down import WebServerDownException


def test_web_server_down_exception_default_error_code():
    """Test initialization with default error code."""
    exception = WebServerDownException("Web server is down")
    assert exception.message == "Web server is down"
    assert exception.error_code == 9


def test_web_server_down_exception_custom_error_code():
    """Test initialization with a custom error code."""
    exception = WebServerDownException("Web server is down", 503)
    assert exception.message == "Web server is down"
    assert exception.error_code == 503


def test_web_server_down_exception_string_representation():
    """Test the string representation of the exception."""
    exception = WebServerDownException("Web server is down", 503)
    assert str(exception) == "Error 503: Web server is down"
