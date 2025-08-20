import pytest
import logging

from kaya_module_sdk.src.utils.logger import setup_logging


def test_valid_logging_configuration():
    """Test case where the logging configuration is correct."""
    result = setup_logging("test_logger", "DEBUG", location="/tmp")
    assert result is True
    logger = logging.getLogger("test_logger")
    assert logger.level == logging.DEBUG


def test_invalid_name():
    """Test case where the name is not a string."""
    result = setup_logging(123, "DEBUG", location="/tmp")
    assert result is False


def test_invalid_level():
    """Test case where the level is invalid."""
    result = setup_logging("test_logger", "INVALID_LEVEL", location="/tmp")
    assert result is False


@pytest.mark.parametrize(
    "name, level, expected_result",
    [
        ("valid_logger", "DEBUG", True),
        ("valid_logger", "INFO", True),
        ("valid_logger", "INVALID_LEVEL", False),
        (123, "DEBUG", False),
    ],
)
def test_setup_logging_parametrized(name, level, expected_result):
    """Test case using pytest's parametrize for different inputs."""
    result = setup_logging(name, level, location="/tmp")
    assert result is expected_result
