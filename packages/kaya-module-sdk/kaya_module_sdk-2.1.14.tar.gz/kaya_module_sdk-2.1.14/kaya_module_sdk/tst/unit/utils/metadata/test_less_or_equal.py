from kaya_module_sdk.src.utils.metadata.less_or_equal import LTE
from kaya_module_sdk.src.utils.metadata.abstract_metadata import KMetadata
from kaya_module_sdk.src.utils.metadata.abstract_validation import KValidation


def test_lte_initialization_with_float():
    """Test that LTE initializes correctly with a float value."""
    instance = LTE(3.14)
    assert instance._data["less_than_or_equal_to"] == 3.14


def test_lte_initialization_with_str():
    """Test that LTE initializes correctly with a string value."""
    instance = LTE("example")
    assert instance._data["less_than_or_equal_to"] == "example"


def test_lte_str_with_float():
    """Test that __str__ returns the expected string for a float value."""
    instance = LTE(2.71)
    expected = "<=:2.71"
    assert str(instance) == expected


def test_lte_str_with_str():
    """Test that __str__ returns the expected string for a string value."""
    instance = LTE("hello")
    expected = "<=:hello"
    assert str(instance) == expected


def test_lte_load_valid_float():
    """
    Test that load() correctly processes a valid string representation
    where the value can be converted to a float.
    """
    instance = LTE(0)
    result = instance.load("<=:3.14")
    expected = {"less_than_or_equal_to": 3.14}
    assert result == expected
    assert instance._data["less_than_or_equal_to"] == 3.14


def test_lte_load_valid_non_numeric():
    """
    Test that load() correctly processes a valid string representation
    where the value is non-numeric.
    """
    instance = LTE(0)
    result = instance.load("<=:not_a_number")
    expected = {"less_than_or_equal_to": "not_a_number"}
    assert result == expected
    assert instance._data["less_than_or_equal_to"] == "not_a_number"


def test_lte_load_invalid_no_colon():
    """
    Test that load() returns an empty dictionary when the colon is missing.
    """
    instance = LTE(0)
    result = instance.load("<=3.14")
    assert result == {}
    assert instance._data["less_than_or_equal_to"] == 0


def test_lte_load_invalid_wrong_prefix():
    """
    Test that load() returns an empty dictionary when the prefix is incorrect.
    """
    instance = LTE(0)
    result = instance.load("wrong:3.14")
    assert result == {}
    assert instance._data["less_than_or_equal_to"] == 0


def test_lte_load_invalid_extra_segments():
    """
    Test that load() returns an empty dictionary when there are extra segments.
    """
    instance = LTE(0)
    result = instance.load("<=:3.14:extra")
    assert result == {}
    assert instance._data["less_than_or_equal_to"] == 0


def test_lte_inheritance():
    """
    Test that LTE is an instance of both KMetadata and KValidation.
    """
    instance = LTE(3.14)
    assert isinstance(instance, KMetadata)
    assert isinstance(instance, KValidation)
