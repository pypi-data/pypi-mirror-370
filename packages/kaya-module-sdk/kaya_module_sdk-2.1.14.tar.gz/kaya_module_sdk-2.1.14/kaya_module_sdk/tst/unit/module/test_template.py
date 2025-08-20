from unittest.mock import patch, MagicMock
from typing import Annotated

from kaya_module_sdk.src.module.template import Module, Config


def test_init(mock_module):
    """Test the initialization of the Module class."""
    assert isinstance(mock_module.config, Config)
    assert isinstance(mock_module.subclasses, list)
    assert isinstance(mock_module.modules, dict)
    assert mock_module._recompute_manifest is True


def test_import_subclasses(mock_module):
    """Test the import_subclasses method."""
    mock_package = "mock_package"
    mock_mod = MagicMock()
    mock_mod.__package__ = mock_package  # Simulate a real module with a __package__ attribute.
    with patch("importlib.import_module", return_value=mock_mod):
        result = mock_module.import_subclasses()
        assert result == mock_module.subclasses  # Verify that it returns the subclasses list.


def test_extract_manifest(mock_module):
    """Test that manifest extraction works"""
    mock_module.config = MagicMock()
    mock_module.config.name = "Test Module"
    mock_module.config.version = "1.0"
    mock_module.config.display_label = "Test Label"
    mock_module.config.category = "Test Category"
    mock_module.config.description = "Test Description"
    mock_module.config.author = "Test Author"
    manifest = mock_module._extract_manifest()
    assert "moduleName" in manifest
    assert manifest["moduleName"] == "Test Module"
    assert "moduleVersion" in manifest
    assert manifest["moduleVersion"] == "1.0"


def test_order_records_by_priority(mock_module):
    """Test the _order_records_by_priority method."""
    records = [
        {"name": "input1", "validations": ["position:2"]},
        {"name": "input2", "validations": []},
        {"name": "input3", "validations": ["position:1"]},
    ]
    ordered = mock_module._order_records_by_priority(*records)
    assert ordered[0]["name"] == "input3"
    assert ordered[1]["name"] == "input1"
    assert ordered[2]["name"] == "input2"


def test_add_subclasses_from_module(mock_module):
    " " "Test the _add_subclasses_from_module method." ""
    # NOTE: Create a mock module with valid and invalid subclasses
    mock_mod = MagicMock()

    # NOTE: Create a valid subclass of Module
    class ValidSubclass(Module):
        def main(self, args):
            pass

    # NOTE: Create an invalid subclass
    class InvalidSubclass:
        pass

    # NOTE: Mock inspect.getmembers to return these classes
    with patch(
        "inspect.getmembers",
        return_value=[
            ("ValidSubclass", ValidSubclass),
            ("InvalidSubclass", InvalidSubclass),
        ],
    ):
        mock_module._add_subclasses_from_module(mock_mod)
        assert len(mock_module.subclasses) == 1
        assert isinstance(mock_module.subclasses[0], ValidSubclass)


def test_is_valid_subclass(mock_module):
    """Test the _is_valid_subclass method."""

    # NOTE: Define a valid subclass of Module
    class ValidSubclass(Module):
        def main(self, args):
            pass

    # NOTE: Define an invalid subclass (not inheriting from Module)
    class InvalidSubclass:
        pass

    # NOTE: Assert that _is_valid_subclass identifies the valid subclass
    assert mock_module._is_valid_subclass(ValidSubclass) is True
    # NOTE: Assert that _is_valid_subclass rejects the invalid subclass
    assert mock_module._is_valid_subclass(InvalidSubclass) is False


def test_unpack_annotated(mock_module):
    """Test the _unpack_annotated method."""
    annotated_type = Annotated[int, "metadata"]
    base_type, metadata = mock_module._unpack_annotated(annotated_type)
    assert base_type is int
    assert metadata == ["metadata"]


def test_manifest_property(mock_module):
    """Test the manifest property."""
    with patch.object(mock_module, "_extract_manifest", return_value={"moduleName": "TestModule"}):
        manifest = mock_module.manifest
        assert manifest == {"moduleName": "TestModule"}


# CODE DUMP
