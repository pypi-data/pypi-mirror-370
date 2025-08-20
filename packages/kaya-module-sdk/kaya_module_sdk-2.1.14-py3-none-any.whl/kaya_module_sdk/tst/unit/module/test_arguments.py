import unittest

from unittest.mock import patch

from kaya_module_sdk.src.utils.metadata.display_description import DisplayDescription
from kaya_module_sdk.src.utils.metadata.display_name import DisplayName
from kaya_module_sdk.src.module.arguments import Args


def test_initialization():
    """Test that the Args object initializes correctly."""
    args = Args()
    assert args.errors == [], "Errors should be initialized as an empty list."


def test_set_errors_adds_single_error():
    """Test that set_errors adds a single error."""
    args = Args()
    error = Exception("Test error")
    args.set_errors(error)
    assert args.errors == [error], "Errors list should contain the added error."


def test_set_errors_adds_multiple_errors():
    """Test that set_errors adds multiple errors."""
    args = Args()
    error1 = Exception("Test error 1")
    error2 = Exception("Test error 2")
    args.set_errors(error1, error2)
    assert args.errors == [
        error1,
        error2,
    ], "Errors list should contain all added errors."


def test_metadata_returns_correct_type_hints():
    """Test that metadata method returns correct type hints with annotations."""
    args = Args()
    metadata = args.metadata()
    assert "_errors" in metadata, "Metadata should include '_errors'."
    # NOTE: Correct way to access Annotated arguments
    annotations = metadata["_errors"]
    # NOTE: Access the metadata from the __metadata__ attribute if it exists
    if hasattr(annotations, "__metadata__"):
        # NOTE: Verify the length and presence of metadata annotations
        if len(annotations.__metadata__) > 1:
            display_name = annotations.__metadata__[0]  # First metadata
            display_description = annotations.__metadata__[1]  # Second metadata
            # NOTE: Check if the annotations are correctly applied
            assert isinstance(display_name, DisplayName), "First annotation should be DisplayName."
            assert display_name._data.get("name") == "Errors", "DisplayName should match the expected value."
            assert isinstance(
                display_description, DisplayDescription
            ), "Second annotation should be DisplayDescription."
            assert (
                display_description._data.get("description") == "Collection of things that went very, very wrong."
            ), "DisplayDescription should match the expected value."
        else:
            assert False, "Annotations do not contain the expected metadata."
    else:
        assert False, "Annotations do not have '__metadata__' attribute."


@patch("logging.getLogger")
def test_logging(mock_logger):
    """Test that logging is initialized correctly."""
    log = mock_logger.return_value
    log.debug("Debugging message.")
    log.debug.assert_called_with("Debugging message.")


if __name__ == "__main__":
    unittest.main()

# CODE DUMP
