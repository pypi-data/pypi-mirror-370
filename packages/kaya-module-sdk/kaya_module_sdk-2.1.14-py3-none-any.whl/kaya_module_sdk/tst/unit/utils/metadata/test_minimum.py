from kaya_module_sdk.src.utils.metadata.minimum import Min
from kaya_module_sdk.src.utils.metadata.abstract_metadata import KMetadata
from kaya_module_sdk.src.utils.metadata.abstract_validation import KValidation


def test_min_initialization_with_float():
    """Test that Min initializes correctly with a float value."""
    instance = Min(3.5)
    assert instance._data["minimum"] == 3.5


def test_min_initialization_with_str():
    """Test that Min initializes correctly with a string value."""
    instance = Min("low_threshold")
    assert instance._data["minimum"] == "low_threshold"


def test_min_str_with_float():
    """Test that __str__ returns the correct string for a float value."""
    instance = Min(7.0)
    expected = "min:7.0"
    assert str(instance) == expected


def test_min_str_with_str():
    """Test that __str__ returns the correct string for a string value."""
    instance = Min("low")
    expected = "min:low"
    assert str(instance) == expected


def test_min_load_valid_float():
    """
    Test that load() correctly processes a valid string representation
    where the value can be converted to a float.
    """
    instance = Min(0)
    result = instance.load("min:10.5")
    expected = {"minimum": 10.5}
    assert result == expected
    assert instance._data["minimum"] == 10.5


def test_min_load_valid_non_numeric():
    """
    Test that load() correctly processes a valid string representation
    where the value is non-numeric.
    """
    instance = Min(0)
    result = instance.load("min:low_threshold")
    expected = {"minimum": "low_threshold"}
    assert result == expected
    assert instance._data["minimum"] == "low_threshold"


def test_min_load_invalid_no_colon():
    """
    Test that load() returns an empty dict when the colon is missing.
    """
    instance = Min(0)
    result = instance.load("min10")
    assert result == {}
    assert instance._data["minimum"] == 0


def test_min_load_invalid_wrong_prefix():
    """
    Test that load() returns an empty dict when the prefix is incorrect.
    """
    instance = Min(0)
    result = instance.load("wrong:5")
    assert result == {}
    assert instance._data["minimum"] == 0


def test_min_load_invalid_extra_segments():
    """
    Test that load() returns an empty dict when there are extra segments.
    """
    instance = Min(0)
    result = instance.load("min:5:extra")
    assert result == {}
    assert instance._data["minimum"] == 0


def test_min_inheritance():
    """
    Test that Min is an instance of both KMetadata and KValidation.
    """
    instance = Min(5)
    assert isinstance(instance, KMetadata)
    assert isinstance(instance, KValidation)
