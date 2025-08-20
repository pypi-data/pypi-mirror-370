from kaya_module_sdk.src.utils.metadata.eq_len import EQLen
from kaya_module_sdk.src.utils.metadata.abstract_metadata import KMetadata
from kaya_module_sdk.src.utils.metadata.abstract_validation import KValidation


def test_eqlen_initialization_with_int():
    """Test that EQLen initializes correctly with an integer."""
    instance = EQLen(10)
    assert instance._data["eq_len"] == 10


def test_eqlen_initialization_with_str():
    """Test that EQLen initializes correctly with a string."""
    instance = EQLen("sample")
    assert instance._data["eq_len"] == "sample"


def test_eqlen_str_with_int():
    """Test that __str__ returns the expected string when initialized with an integer."""
    instance = EQLen(15)
    expected = "eqlen:15"
    assert str(instance) == expected


def test_eqlen_str_with_str():
    """Test that __str__ returns the expected string when initialized with a string."""
    instance = EQLen("hello")
    expected = "eqlen:hello"
    assert str(instance) == expected


def test_eqlen_load_valid_int():
    """
    Test that load() correctly processes a valid string representation
    where the value can be converted to an integer.
    """
    instance = EQLen(0)  # initial value is 0
    result = instance.load("eqlen:20")
    expected = {"eq_len": 20}
    assert result == expected
    assert instance._data["eq_len"] == 20


def test_eqlen_load_valid_non_int():
    """
    Test that load() correctly processes a valid string representation
    where the value is non-numeric.
    """
    instance = EQLen(0)
    result = instance.load("eqlen:abc")
    expected = {"eq_len": "abc"}
    assert result == expected
    assert instance._data["eq_len"] == "abc"


def test_eqlen_load_invalid_format_no_colon():
    """
    Test that load() returns an empty dictionary when the colon is missing.
    """
    instance = EQLen(0)
    result = instance.load("eqlenabc")
    assert result == {}
    # The internal data should remain unchanged.
    assert instance._data["eq_len"] == 0


def test_eqlen_load_invalid_prefix():
    """
    Test that load() returns an empty dictionary when the prefix is incorrect.
    """
    instance = EQLen(0)
    result = instance.load("wrong:20")
    assert result == {}
    assert instance._data["eq_len"] == 0


def test_eqlen_load_with_extra_segments():
    """
    Test that load() returns an empty dictionary when there are extra segments.
    """
    instance = EQLen(0)
    result = instance.load("eqlen:20:extra")
    assert result == {}
    assert instance._data["eq_len"] == 0


def test_eqlen_inheritance():
    """
    Test that EQLen is an instance of both KMetadata and KValidation.
    """
    instance = EQLen(0)
    assert isinstance(instance, KMetadata)
    assert isinstance(instance, KValidation)
