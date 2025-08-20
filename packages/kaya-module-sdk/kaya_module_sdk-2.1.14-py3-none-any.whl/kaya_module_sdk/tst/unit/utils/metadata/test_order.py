from kaya_module_sdk.src.utils.metadata.order import Order
from kaya_module_sdk.src.utils.metadata.abstract_metadata import KMetadata
from kaya_module_sdk.src.utils.metadata.abstract_validation import KValidation


def test_order_initialization():
    """Test that Order initializes correctly with an integer value."""
    instance = Order(10)
    assert instance._data["position"] == 10


def test_order_str():
    """Test that __str__ returns the correct string representation."""
    instance = Order(5)
    expected = "position:5"
    assert str(instance) == expected


def test_order_load_valid_integer():
    """
    Test that load() correctly processes a valid string representation
    where the value is an integer.
    """
    instance = Order(0)
    result = instance.load("position:25")
    expected = {"position": 25}
    assert result == expected
    assert instance._data["position"] == 25


def test_order_load_invalid_no_colon():
    """
    Test that load() returns an empty dict when the colon is missing.
    """
    instance = Order(0)
    result = instance.load("position25")
    assert result == {}
    assert instance._data["position"] == 0


def test_order_load_invalid_wrong_prefix():
    """
    Test that load() returns an empty dict when the prefix is incorrect.
    """
    instance = Order(0)
    result = instance.load("rank:10")
    assert result == {}
    assert instance._data["position"] == 0


def test_order_load_invalid_non_integer():
    """
    Test that load() assigns the original string if conversion to integer fails.
    """
    instance = Order(0)
    result = instance.load("position:ten")
    expected = {"position": "ten"}
    assert result == expected
    assert instance._data["position"] == "ten"


def test_order_load_invalid_extra_segments():
    """
    Test that load() returns an empty dict when there are extra segments.
    """
    instance = Order(0)
    result = instance.load("position:10:extra")
    assert result == {}
    assert instance._data["position"] == 0


def test_order_inheritance():
    """
    Test that Order is an instance of both KMetadata and KValidation.
    """
    instance = Order(5)
    assert isinstance(instance, KMetadata)
    assert isinstance(instance, KValidation)
