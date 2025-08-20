from kaya_module_sdk.src.utils.metadata.abstract_metadata import KMetadata
from kaya_module_sdk.src.utils.metadata.abstract_validation import KValidation
from kaya_module_sdk.src.utils.metadata.const import Const


def test_const_initialization_with_bool():
    """
    Test that the Const class is initialized correctly with a boolean value.
    """
    const_instance = Const(True)
    assert const_instance._data["const"] is True


def test_const_initialization_with_str():
    """
    Test that the Const class is initialized correctly with a string value.
    """
    const_instance = Const("some_string")
    assert const_instance._data["const"] == "some_string"


def test_const_str_repr():
    """
    Test the __str__ method to check that it returns the expected string representation.
    """
    const_instance = Const(True)
    assert str(const_instance) == "const:True"

    const_instance = Const("some_string")
    assert str(const_instance) == "const:some_string"


def test_const_load_with_valid_boolean():
    """
    Test the load method when given a valid "const:True" or "const:False" string representation.
    """
    const_instance = Const(False)
    result = const_instance.load("const:True")
    assert result == {"const": True}
    assert const_instance._data["const"] is True

    result = const_instance.load("const:False")
    assert result == {"const": False}
    assert const_instance._data["const"] is False


def test_const_load_with_invalid_format():
    """
    Test the load method when given an invalid string representation.
    """
    const_instance = Const("invalid")
    result = const_instance.load("invalid_string")
    assert result == {}
    assert const_instance._data["const"] == "invalid"


def test_const_load_with_non_boolean_value():
    """
    Test the load method when given a non-boolean value in the string representation.
    """
    const_instance = Const(True)
    result = const_instance.load("const:something")
    assert result == {"const": "something"}
    assert const_instance._data["const"] == "something"


def test_const_load_with_empty_string():
    """
    Test the load method with an empty string input.
    """
    const_instance = Const(True)
    result = const_instance.load("")
    assert result == {}
    assert const_instance._data["const"] is True


def test_const_is_instance_of_kmetadata_and_kvalidation():
    """
    Test that Const is an instance of both KMetadata and KValidation.
    """
    const_instance = Const(True)
    assert isinstance(const_instance, KMetadata)
    assert isinstance(const_instance, KValidation)


def test_const_load_with_invalid_segments():
    """
    Test load method with invalid segments.
    """
    const_instance = Const(True)

    # Case with extra colon or invalid prefix
    result = const_instance.load("const:extra:value")
    assert result == {}
    assert const_instance._data["const"] is True

    result = const_instance.load("const:")
    assert result == {"const": ""}
    assert const_instance._data["const"] == ""

    result = const_instance.load("some_invalid_prefix:True")
    assert result == {}
    assert const_instance._data["const"] == ""
