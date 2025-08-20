from kaya_module_sdk.src.utils.metadata.greater_or_equal import GTE
from kaya_module_sdk.src.utils.metadata.abstract_metadata import KMetadata
from kaya_module_sdk.src.utils.metadata.abstract_validation import KValidation


def test_gte_initialization_with_float():
    """Test that GTE initializes correctly with a float value."""
    instance = GTE(3.14)
    assert instance._data["greater_than_or_equal_to"] == 3.14


def test_gte_initialization_with_str():
    """Test that GTE initializes correctly with a string value."""
    instance = GTE("example")
    assert instance._data["greater_than_or_equal_to"] == "example"


def test_gte_str_with_float():
    """Test that __str__ returns the expected string for a float value."""
    instance = GTE(2.71)
    expected = ">=:2.71"
    assert str(instance) == expected


def test_gte_str_with_str():
    """Test that __str__ returns the expected string for a string value."""
    instance = GTE("hello")
    expected = ">=:hello"
    assert str(instance) == expected


def test_gte_load_valid_float():
    """
    Test that load() correctly processes a valid string representation
    where the value can be converted to a float.
    """
    instance = GTE(0)  # initial value is 0
    result = instance.load(">=:3.14")
    expected = {"greater_than_or_equal_to": 3.14}
    assert result == expected
    assert instance._data["greater_than_or_equal_to"] == 3.14


def test_gte_load_valid_non_numeric():
    """
    Test that load() correctly processes a valid string representation
    where the value is non-numeric.
    """
    instance = GTE(0)
    result = instance.load(">=:abc")
    expected = {"greater_than_or_equal_to": "abc"}
    assert result == expected
    assert instance._data["greater_than_or_equal_to"] == "abc"


def test_gte_load_invalid_no_colon():
    """
    Test that load() returns an empty dict when the colon is missing.
    """
    instance = GTE(0)
    result = instance.load(">=3.14")
    assert result == {}
    # Internal data should remain unchanged.
    assert instance._data["greater_than_or_equal_to"] == 0


def test_gte_load_invalid_prefix():
    """
    Test that load() returns an empty dict when the prefix is incorrect.
    """
    instance = GTE(0)
    result = instance.load("wrong:3.14")
    assert result == {}
    assert instance._data["greater_than_or_equal_to"] == 0


def test_gte_load_invalid_extra_segments():
    """
    Test that load() returns an empty dict when there are extra segments.
    """
    instance = GTE(0)
    result = instance.load(">=:3.14:extra")
    assert result == {}
    assert instance._data["greater_than_or_equal_to"] == 0


def test_gte_inheritance():
    """
    Test that GTE is an instance of both KMetadata and KValidation.
    """
    instance = GTE(3.14)
    assert isinstance(instance, KMetadata)
    assert isinstance(instance, KValidation)
