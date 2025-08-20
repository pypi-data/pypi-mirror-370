from kaya_module_sdk.src.utils.metadata.less import LT
from kaya_module_sdk.src.utils.metadata.abstract_metadata import KMetadata
from kaya_module_sdk.src.utils.metadata.abstract_validation import KValidation


def test_lt_initialization_with_float():
    """Test that LT initializes correctly with a float value."""
    instance = LT(3.14)
    assert instance._data["less"] == 3.14


def test_lt_initialization_with_str():
    """Test that LT initializes correctly with a string value."""
    instance = LT("example")
    assert instance._data["less"] == "example"


def test_lt_str_with_float():
    """Test that __str__ returns the expected string for a float value."""
    instance = LT(2.71)
    expected = "<:2.71"
    assert str(instance) == expected


def test_lt_str_with_str():
    """Test that __str__ returns the expected string for a string value."""
    instance = LT("hello")
    expected = "<:hello"
    assert str(instance) == expected


def test_lt_load_valid_float():
    """
    Test that load() correctly processes a valid string representation
    where the value can be converted to a float.
    """
    instance = LT(0)
    result = instance.load("<:3.14")
    expected = {"less": 3.14}
    assert result == expected
    assert instance._data["less"] == 3.14


def test_lt_load_valid_non_numeric():
    """
    Test that load() correctly processes a valid string representation
    where the value cannot be converted to a float.
    """
    instance = LT(0)
    result = instance.load("<:abc")
    expected = {"less": "abc"}
    assert result == expected
    assert instance._data["less"] == "abc"


def test_lt_load_invalid_no_colon():
    """
    Test that load() returns an empty dictionary when the colon separator is missing.
    """
    instance = LT(0)
    result = instance.load("<3.14")
    assert result == {}
    assert instance._data["less"] == 0


def test_lt_load_invalid_wrong_prefix():
    """
    Test that load() returns an empty dictionary when the prefix is incorrect.
    """
    instance = LT(0)
    result = instance.load("wrong:3.14")
    assert result == {}
    assert instance._data["less"] == 0


def test_lt_load_invalid_extra_segments():
    """
    Test that load() returns an empty dictionary when there are extra segments.
    """
    instance = LT(0)
    result = instance.load("<:3.14:extra")
    assert result == {}
    assert instance._data["less"] == 0


def test_lt_inheritance():
    """
    Test that LT is an instance of both KMetadata and KValidation.
    """
    instance = LT(3.14)
    assert isinstance(instance, KMetadata)
    assert isinstance(instance, KValidation)
