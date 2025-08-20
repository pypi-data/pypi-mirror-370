from kaya_module_sdk.src.utils.metadata.equal import EQ
from kaya_module_sdk.src.utils.metadata.abstract_metadata import KMetadata
from kaya_module_sdk.src.utils.metadata.abstract_validation import KValidation


def test_eq_initialization_with_float():
    """Test that EQ initializes correctly when given a float value."""
    eq_instance = EQ(3.14)
    assert eq_instance._data["equals"] == 3.14


def test_eq_initialization_with_str():
    """Test that EQ initializes correctly when given a string value."""
    eq_instance = EQ("test")
    assert eq_instance._data["equals"] == "test"


def test_eq_str_with_float():
    """Test that __str__ returns the correct string representation for a float value."""
    eq_instance = EQ(2.71)
    expected = "==:2.71"
    assert str(eq_instance) == expected


def test_eq_str_with_str():
    """Test that __str__ returns the correct string representation for a string value."""
    eq_instance = EQ("value")
    expected = "==:value"
    assert str(eq_instance) == expected


def test_eq_load_valid_float():
    """
    Test that load() correctly processes a valid string representation
    where the value can be converted to a float.
    """
    eq_instance = EQ(0)
    result = eq_instance.load("==:3.14")
    expected = {"equals": 3.14}
    assert result == expected
    assert eq_instance._data["equals"] == 3.14


def test_eq_load_valid_non_numeric():
    """
    Test that load() correctly processes a valid string representation
    where the value cannot be converted to a float, so remains a string.
    """
    eq_instance = EQ(0)
    result = eq_instance.load("==:not_a_number")
    expected = {"equals": "not_a_number"}
    assert result == expected
    assert eq_instance._data["equals"] == "not_a_number"


def test_eq_load_invalid_format_no_colon():
    """
    Test that load() returns an empty dictionary when the colon separator is missing.
    """
    eq_instance = EQ(0)
    result = eq_instance.load("==not_a_number")
    assert result == {}
    assert eq_instance._data["equals"] == 0


def test_eq_load_invalid_prefix():
    """
    Test that load() returns an empty dictionary when the prefix is incorrect.
    """
    eq_instance = EQ(0)
    result = eq_instance.load("wrong:3.14")
    assert result == {}
    assert eq_instance._data["equals"] == 0


def test_eq_load_extra_segments():
    """
    Test that load() returns an empty dictionary when there are extra segments.
    """
    eq_instance = EQ(0)
    result = eq_instance.load("==:3.14:extra")
    assert result == {}
    assert eq_instance._data["equals"] == 0


def test_eq_inheritance():
    """
    Test that EQ is an instance of both KMetadata and KValidation.
    """
    eq_instance = EQ(3.14)
    assert isinstance(eq_instance, KMetadata)
    assert isinstance(eq_instance, KValidation)
