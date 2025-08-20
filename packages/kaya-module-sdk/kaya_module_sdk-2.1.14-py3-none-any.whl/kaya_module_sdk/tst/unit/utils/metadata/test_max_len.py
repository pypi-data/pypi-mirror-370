from kaya_module_sdk.src.utils.metadata.max_len import MaxLen
from kaya_module_sdk.src.utils.metadata.abstract_metadata import KMetadata
from kaya_module_sdk.src.utils.metadata.abstract_validation import KValidation


def test_maxlen_initialization_with_float():
    """Test that MaxLen initializes correctly with a float value."""
    instance = MaxLen(10.5)
    assert instance._data["max_len"] == 10.5


def test_maxlen_initialization_with_str():
    """Test that MaxLen initializes correctly with a string value."""
    instance = MaxLen("abc")
    assert instance._data["max_len"] == "abc"


def test_maxlen_str_with_float():
    """Test that __str__ returns the correct string for a float value."""
    instance = MaxLen(42.0)
    expected = "maxlen:42.0"
    assert str(instance) == expected


def test_maxlen_str_with_str():
    """Test that __str__ returns the correct string for a string value."""
    instance = MaxLen("test")
    expected = "maxlen:test"
    assert str(instance) == expected


def test_maxlen_load_valid_float():
    """
    Test that load() correctly processes a valid string representation
    where the value can be converted to a float.
    """
    instance = MaxLen(0)
    result = instance.load("maxlen:100.5")
    expected = {"max_len": 100.5}
    assert result == expected
    assert instance._data["max_len"] == 100.5


def test_maxlen_load_valid_non_numeric():
    """
    Test that load() correctly processes a valid string representation
    where the value is non-numeric.
    """
    instance = MaxLen(0)
    result = instance.load("maxlen:hello")
    expected = {"max_len": "hello"}
    assert result == expected
    assert instance._data["max_len"] == "hello"


def test_maxlen_load_invalid_no_colon():
    """
    Test that load() returns an empty dict when the colon is missing.
    """
    instance = MaxLen(0)
    result = instance.load("maxlen100")
    assert result == {}
    assert instance._data["max_len"] == 0


def test_maxlen_load_invalid_wrong_prefix():
    """
    Test that load() returns an empty dict when the prefix is incorrect.
    """
    instance = MaxLen(0)
    result = instance.load("wrong:100")
    assert result == {}
    assert instance._data["max_len"] == 0


def test_maxlen_load_invalid_extra_segments():
    """
    Test that load() returns an empty dict when there are extra segments.
    """
    instance = MaxLen(0)
    result = instance.load("maxlen:100:extra")
    assert result == {}
    assert instance._data["max_len"] == 0


def test_maxlen_inheritance():
    """
    Test that MaxLen is an instance of both KMetadata and KValidation.
    """
    instance = MaxLen(10)
    assert isinstance(instance, KMetadata)
    assert isinstance(instance, KValidation)
