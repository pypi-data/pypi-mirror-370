from kaya_module_sdk.src.utils.metadata.not_const import NotConst
from kaya_module_sdk.src.utils.metadata.abstract_metadata import KMetadata
from kaya_module_sdk.src.utils.metadata.abstract_validation import KValidation


# --------------------------------------------------------------------
# Initialization Tests
# --------------------------------------------------------------------
def test_notconst_initialization_with_bool():
    """Test that NotConst initializes correctly with a boolean value."""
    instance = NotConst(True)
    assert instance._data["not_const"] is True


def test_notconst_initialization_with_str():
    """Test that NotConst initializes correctly with a string value."""
    instance = NotConst("dynamic")
    assert instance._data["not_const"] == "dynamic"


# --------------------------------------------------------------------
# __str__ Method Tests
# --------------------------------------------------------------------
def test_notconst_str_with_bool():
    """Test that __str__ returns the correct string for a boolean value."""
    instance = NotConst(False)
    expected = "notconst:False"
    assert str(instance) == expected


def test_notconst_str_with_str():
    """Test that __str__ returns the correct string for a string value."""
    instance = NotConst("variable")
    expected = "notconst:variable"
    assert str(instance) == expected


# --------------------------------------------------------------------
# load() Method Tests
# --------------------------------------------------------------------
def test_notconst_load_valid_bool_true():
    """
    Test that load() correctly processes a valid string representation
    where the value can be converted to a boolean (True).
    """
    instance = NotConst(False)
    result = instance.load("notconst:True")
    expected = {"not_const": True}
    assert result == expected
    assert instance._data["not_const"] is True


def test_notconst_load_valid_bool_false():
    """
    Test that load() correctly processes a valid string representation
    where the value can be converted to a boolean (False).
    """
    instance = NotConst(True)
    result = instance.load("notconst:False")
    expected = {"not_const": False}
    assert result == expected
    assert instance._data["not_const"] is False


def test_notconst_load_valid_non_boolean():
    """
    Test that load() correctly processes a valid string representation
    where the value is non-boolean.
    """
    instance = NotConst(False)
    result = instance.load("notconst:dynamic_value")
    expected = {"not_const": "dynamic_value"}
    assert result == expected
    assert instance._data["not_const"] == "dynamic_value"


def test_notconst_load_invalid_no_colon():
    """
    Test that load() returns an empty dict when the colon is missing.
    """
    instance = NotConst(False)
    result = instance.load("notconstTrue")
    assert result == {}
    assert instance._data["not_const"] is False


def test_notconst_load_invalid_wrong_prefix():
    """
    Test that load() returns an empty dict when the prefix is incorrect.
    """
    instance = NotConst(False)
    result = instance.load("incorrect:True")
    assert result == {}
    assert instance._data["not_const"] is False


def test_notconst_load_invalid_extra_segments():
    """
    Test that load() returns an empty dict when there are extra segments.
    """
    instance = NotConst(False)
    result = instance.load("notconst:True:extra")
    assert result == {}
    assert instance._data["not_const"] is False


# --------------------------------------------------------------------
# Inheritance Test
# --------------------------------------------------------------------
def test_notconst_inheritance():
    """
    Test that NotConst is an instance of both KMetadata and KValidation.
    """
    instance = NotConst(True)
    assert isinstance(instance, KMetadata)
    assert isinstance(instance, KValidation)
