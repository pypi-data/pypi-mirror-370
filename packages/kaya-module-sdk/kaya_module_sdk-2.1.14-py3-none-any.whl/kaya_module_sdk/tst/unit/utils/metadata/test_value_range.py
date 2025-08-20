from kaya_module_sdk.src.utils.metadata.value_range import ValueRange
from kaya_module_sdk.src.utils.metadata.abstract_metadata import KMetadata
from kaya_module_sdk.src.utils.metadata.abstract_validation import KValidation


def test_value_range_initialization():
    """Test that ValueRange initializes correctly with min and max values."""
    instance = ValueRange(10, 20)
    assert instance._data["min_val"] == 10
    assert instance._data["max_val"] == 20


def test_value_range_str():
    """Test that __str__ returns the correct string representation."""
    instance = ValueRange(5.5, 15.2)
    expected = "range:5.5;15.2"
    assert str(instance) == expected


def test_value_range_load_valid_numbers():
    """
    Test that load() correctly processes a valid string representation
    with numeric values.
    """
    instance = ValueRange(0, 0)
    result = instance.load("range:10.5;20.3")
    expected = {"min_val": 10.5, "max_val": 20.3}
    assert result == expected
    assert instance._data["min_val"] == 10.5
    assert instance._data["max_val"] == 20.3


def test_value_range_load_valid_integer():
    """Test that load() correctly handles integer values."""
    instance = ValueRange(0, 0)
    result = instance.load("range:5;15")
    expected = {"min_val": 5, "max_val": 15}
    assert result == expected
    assert instance._data["min_val"] == 5
    assert instance._data["max_val"] == 15


def test_value_range_load_invalid_no_colon():
    """Test that load() returns an empty dict when the colon is missing."""
    instance = ValueRange(0, 0)
    result = instance.load("range5;15")
    assert result == {}


def test_value_range_load_invalid_wrong_prefix():
    """Test that load() returns an empty dict when the prefix is incorrect."""
    instance = ValueRange(0, 0)
    result = instance.load("limit:10;20")
    assert result == {}


def test_value_range_load_invalid_missing_semicolon():
    """Test that load() returns an empty dict when the semicolon is missing."""
    instance = ValueRange(0, 0)
    result = instance.load("range:10")
    assert result == {}


def test_value_range_load_invalid_extra_segments():
    """Test that load() returns an empty dict when there are extra segments."""
    instance = ValueRange(0, 0)
    result = instance.load("range:10;20;30")
    assert result == {}


def test_value_range_load_invalid_non_numeric():
    """Test that load() assigns the original strings if conversion to float fails."""
    instance = ValueRange(0, 0)
    result = instance.load("range:low;high")
    expected = {"min_val": "low", "max_val": "high"}
    assert result == expected
    assert instance._data["min_val"] == "low"
    assert instance._data["max_val"] == "high"


def test_value_range_inheritance():
    """Test that ValueRange is an instance of both KMetadata and KValidation."""
    instance = ValueRange(5, 15)
    assert isinstance(instance, KMetadata)
    assert isinstance(instance, KValidation)
