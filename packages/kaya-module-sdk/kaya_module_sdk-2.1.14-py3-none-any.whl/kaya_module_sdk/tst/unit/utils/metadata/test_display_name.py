from kaya_module_sdk.src.utils.metadata.display_name import DisplayName
from kaya_module_sdk.src.utils.metadata.abstract_metadata import KMetadata


def test_display_name_initialization():
    """Test that DisplayName initializes correctly with a given name."""
    name = "Alice"
    dn = DisplayName(name)
    assert dn._data["name"] == name


def test_display_name_str():
    """Test that the __str__ method returns the correct string representation."""
    name = "Alice"
    dn = DisplayName(name)
    expected = f"name:{name}"
    assert str(dn) == expected


def test_display_name_load_valid():
    """Test that load() correctly processes a valid string representation."""
    dn = DisplayName("Initial")
    # Valid representation: should update the internal data.
    result = dn.load("name:UpdatedName")
    expected = {"name": "UpdatedName"}
    assert result == expected
    assert dn._data["name"] == "UpdatedName"


def test_display_name_load_invalid_no_colon():
    """
    Test that load() returns an empty dict when the input string
    is missing the colon separator.
    """
    dn = DisplayName("Initial")
    result = dn.load("nameUpdatedName")
    assert result == {}
    # Internal data should remain unchanged.
    assert dn._data["name"] == "Initial"


def test_display_name_load_invalid_wrong_prefix():
    """
    Test that load() returns an empty dict when the prefix is incorrect.
    """
    dn = DisplayName("Initial")
    result = dn.load("other:UpdatedName")
    assert result == {}
    # Internal data should remain unchanged.
    assert dn._data["name"] == "Initial"


def test_display_name_load_invalid_extra_segments():
    """
    Test that load() returns an empty dict when the string has extra segments.
    """
    dn = DisplayName("Initial")
    result = dn.load("name:UpdatedName:Extra")
    assert result == {}
    # Internal data should remain unchanged.
    assert dn._data["name"] == "Initial"


def test_display_name_inheritance():
    """
    Test that DisplayName is an instance of KMetadata.
    """
    dn = DisplayName("Alice")
    assert isinstance(dn, KMetadata)
