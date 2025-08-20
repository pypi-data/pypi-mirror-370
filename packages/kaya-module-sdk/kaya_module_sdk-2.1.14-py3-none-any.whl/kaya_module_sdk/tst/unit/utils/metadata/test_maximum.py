from kaya_module_sdk.src.utils.metadata.maximum import Max
from kaya_module_sdk.src.utils.metadata.abstract_metadata import KMetadata
from kaya_module_sdk.src.utils.metadata.abstract_validation import KValidation


def test_max_initialization_with_float():
    """Test that Max initializes correctly with a float value."""
    instance = Max(99.9)
    assert instance._data["maximum"] == 99.9


def test_max_initialization_with_str():
    """Test that Max initializes correctly with a string value."""
    instance = Max("limit")
    assert instance._data["maximum"] == "limit"


def test_max_str_with_float():
    """Test that __str__ returns the correct string for a float value."""
    instance = Max(42.0)
    expected = "max:42.0"
    assert str(instance) == expected


def test_max_str_with_str():
    """Test that __str__ returns the correct string for a string value."""
    instance = Max("top")
    expected = "max:top"
    assert str(instance) == expected


def test_max_load_valid_float():
    """
    Test that load() correctly processes a valid string representation
    where the value can be converted to a float.
    """
    instance = Max(0)
    result = instance.load("max:200.5")
    expected = {"maximum": 200.5}
    assert result == expected
    assert instance._data["maximum"] == 200.5


def test_max_load_valid_non_numeric():
    """
    Test that load() correctly processes a valid string representation
    where the value is non-numeric.
    """
    instance = Max(0)
    result = instance.load("max:threshold")
    expected = {"maximum": "threshold"}
    assert result == expected
    assert instance._data["maximum"] == "threshold"


def test_max_load_invalid_no_colon():
    """
    Test that load() returns an empty dict when the colon is missing.
    """
    instance = Max(0)
    result = instance.load("max200")
    assert result == {}
    assert instance._data["maximum"] == 0


def test_max_load_invalid_wrong_prefix():
    """
    Test that load() returns an empty dict when the prefix is incorrect.
    """
    instance = Max(0)
    result = instance.load("wrong:100")
    assert result == {}
    assert instance._data["maximum"] == 0


def test_max_load_invalid_extra_segments():
    """
    Test that load() returns an empty dict when there are extra segments.
    """
    instance = Max(0)
    result = instance.load("max:100:extra")
    assert result == {}
    assert instance._data["maximum"] == 0


def test_max_inheritance():
    """
    Test that Max is an instance of both KMetadata and KValidation.
    """
    instance = Max(10)
    assert isinstance(instance, KMetadata)
    assert isinstance(instance, KValidation)
