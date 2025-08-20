from kaya_module_sdk.src.utils.metadata.min_len import MinLen
from kaya_module_sdk.src.utils.metadata.abstract_metadata import KMetadata
from kaya_module_sdk.src.utils.metadata.abstract_validation import KValidation


def test_minlen_initialization_with_float():
    """Test that MinLen initializes correctly with a float value."""
    instance = MinLen(5.5)
    assert instance._data["min_len"] == 5.5


def test_minlen_initialization_with_str():
    """Test that MinLen initializes correctly with a string value."""
    instance = MinLen("threshold")
    assert instance._data["min_len"] == "threshold"


def test_minlen_str_with_float():
    """Test that __str__ returns the correct string for a float value."""
    instance = MinLen(8.0)
    expected = "minlen:8.0"
    assert str(instance) == expected


def test_minlen_str_with_str():
    """Test that __str__ returns the correct string for a string value."""
    instance = MinLen("boundary")
    expected = "minlen:boundary"
    assert str(instance) == expected


def test_minlen_load_valid_float():
    """
    Test that load() correctly processes a valid string representation
    where the value can be converted to a float.
    """
    instance = MinLen(0)
    result = instance.load("minlen:10.75")
    expected = {"min_len": 10.75}
    assert result == expected
    assert instance._data["min_len"] == 10.75


def test_minlen_load_valid_non_numeric():
    """
    Test that load() correctly processes a valid string representation
    where the value is non-numeric.
    """
    instance = MinLen(0)
    result = instance.load("minlen:threshold")
    expected = {"min_len": "threshold"}
    assert result == expected
    assert instance._data["min_len"] == "threshold"


def test_minlen_load_invalid_no_colon():
    """
    Test that load() returns an empty dict when the colon is missing.
    """
    instance = MinLen(0)
    result = instance.load("minlen10")
    assert result == {}
    assert instance._data["min_len"] == 0


def test_minlen_load_invalid_wrong_prefix():
    """
    Test that load() returns an empty dict when the prefix is incorrect.
    """
    instance = MinLen(0)
    result = instance.load("wrong:15")
    assert result == {}
    assert instance._data["min_len"] == 0


def test_minlen_load_invalid_extra_segments():
    """
    Test that load() returns an empty dict when there are extra segments.
    """
    instance = MinLen(0)
    result = instance.load("minlen:20:extra")
    assert result == {}
    assert instance._data["min_len"] == 0


def test_minlen_inheritance():
    """
    Test that MinLen is an instance of both KMetadata and KValidation.
    """
    instance = MinLen(10)
    assert isinstance(instance, KMetadata)
    assert isinstance(instance, KValidation)
