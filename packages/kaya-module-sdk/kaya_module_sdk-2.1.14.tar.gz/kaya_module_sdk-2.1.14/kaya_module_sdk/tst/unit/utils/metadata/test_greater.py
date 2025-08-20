from kaya_module_sdk.src.utils.metadata.greater import GT
from kaya_module_sdk.src.utils.metadata.abstract_metadata import KMetadata
from kaya_module_sdk.src.utils.metadata.abstract_validation import KValidation


def test_gt_initialization_with_float():
    """Test that GT initializes correctly with a float value."""
    gt_instance = GT(3.14)
    assert gt_instance._data["greater"] == 3.14


def test_gt_initialization_with_str():
    """Test that GT initializes correctly with a string value."""
    gt_instance = GT("example")
    assert gt_instance._data["greater"] == "example"


def test_gt_str_with_float():
    """Test that __str__ returns the expected string for a float value."""
    gt_instance = GT(2.71)
    expected = ">:2.71"
    assert str(gt_instance) == expected


def test_gt_str_with_str():
    """Test that __str__ returns the expected string for a string value."""
    gt_instance = GT("hello")
    expected = ">:hello"
    assert str(gt_instance) == expected


def test_gt_load_valid_float():
    """
    Test that load() correctly processes a valid string representation
    where the value can be converted to a float.
    """
    gt_instance = GT(0)
    result = gt_instance.load(">:3.14")
    expected = {"greater": 3.14}
    assert result == expected
    assert gt_instance._data["greater"] == 3.14


def test_gt_load_valid_non_numeric():
    """
    Test that load() correctly processes a valid string representation
    where the value is non-numeric and remains a string.
    """
    gt_instance = GT(0)
    result = gt_instance.load(">:not_a_number")
    expected = {"greater": "not_a_number"}
    assert result == expected
    assert gt_instance._data["greater"] == "not_a_number"


def test_gt_load_invalid_no_colon():
    """
    Test that load() returns an empty dictionary when the colon is missing.
    """
    gt_instance = GT(0)
    result = gt_instance.load(">3.14")
    assert result == {}
    assert gt_instance._data["greater"] == 0


def test_gt_load_invalid_prefix():
    """
    Test that load() returns an empty dictionary when the prefix is incorrect.
    """
    gt_instance = GT(0)
    result = gt_instance.load("wrong:3.14")
    assert result == {}
    assert gt_instance._data["greater"] == 0


def test_gt_load_invalid_extra_segments():
    """
    Test that load() returns an empty dictionary when there are extra segments.
    """
    gt_instance = GT(0)
    result = gt_instance.load(">:3.14:extra")
    assert result == {}
    assert gt_instance._data["greater"] == 0


def test_gt_inheritance():
    """Test that GT is an instance of both KMetadata and KValidation."""
    gt_instance = GT(3.14)
    assert isinstance(gt_instance, KMetadata)
    assert isinstance(gt_instance, KValidation)
