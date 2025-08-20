import pytest

from kaya_module_sdk.src.utils.metadata.display_description import DisplayDescription
from kaya_module_sdk.src.utils.metadata.display_name import DisplayName
from kaya_module_sdk.src.utils.metadata.min_len import MinLen

# from kaya_module_sdk.src.utils.constraints.min_len import kminlen
from kaya_module_sdk.src.module.returns import Rets


def test_initialization():
    """Test initialization and property access"""
    r = Rets()
    # NOTE: Check that the _results and _errors lists are empty on initialization
    assert r.results == [], "Expected _results to be an empty list upon initialization."
    assert r.errors == [], "Expected _errors to be an empty list upon initialization."


def test_set_results():
    """Test the 'set_results' method (to add values to _results)"""
    r = Rets()
    # NOTE: Add some results
    r.set_results(1, 2, 3)
    # NOTE: Check if the values are added correctly
    assert r.results == [1, 2, 3], "Expected _results to contain [1, 2, 3]."


def test_set_errors():
    """Test the 'set_errors' method (to add values to _errors)"""
    r = Rets()
    # NOTE: Add some errors
    r.set_errors(Exception("Error 1"), Exception("Error 2"))
    # NOTE: Check if the errors are added correctly
    assert len(r.errors) == 2, "Expected _errors to contain 2 exceptions."
    assert str(r.errors[0]) == "Error 1", "Expected the first error to be 'Error 1'."
    assert str(r.errors[1]) == "Error 2", "Expected the second error to be 'Error 2'."


def test_property_getters():
    """Test that the `results` and `errors` properties return correct values"""
    r = Rets()
    # NOTE: Set some results and errors
    r.set_results(10, 20, 30)
    r.set_errors(Exception("Test error"))
    # NOTE: Check that the results and errors properties return the correct lists
    assert r.results == [10, 20, 30], "Expected _results to contain [10, 20, 30]."
    assert len(r.errors) == 1, "Expected _errors to contain 1 exception."
    assert str(r.errors[0]) == "Test error", "Expected the first error to be 'Test error'."


def test_metadata():
    r = Rets()
    metadata = r.metadata()
    # NOTE: Check if '_results' and '_errors' are present in the metadata
    assert "_results" in metadata, "Metadata should include '_results'."
    assert "_errors" in metadata, "Metadata should include '_errors'."
    # NOTE: Check if the annotations for '_results' are correctly applied
    results_annotations = metadata["_results"]
    assert hasattr(results_annotations, "__args__"), "Annotations for '_results' should have '__args__'."
    # NOTE: The __args__ in Annotated contains only the type (list[typing.Any]), not the metadata
    # So, we need to inspect the metadata more carefully by checking the annotations directly.
    if len(results_annotations.__args__) == 1:
        # NOTE: The second argument for Annotated should be the metadata
        metadata_items = getattr(results_annotations, "__metadata__", [])
        display_name = None
        display_description = None
        min_len = None
        # NOTE: Iterate through the metadata and find the expected annotations
        for item in metadata_items:
            if isinstance(item, DisplayName):
                display_name = item
            elif isinstance(item, DisplayDescription):
                display_description = item
            elif isinstance(item, MinLen):
                min_len = item
        # NOTE: Verify if the annotations are correctly applied
        assert display_name is not None, "Expected DisplayName annotation for '_results'."
        assert display_name._data.get("name") == "Result", "DisplayName should match the expected value."
        assert display_description is not None, "Expected DisplayDescription annotation for '_results'."
        assert (
            display_description._data.get("description") == "Module computation results."
        ), "DisplayDescription should match the expected value."
        assert min_len is not None, "Expected MinLen annotation for '_results'."
        assert min_len._data.get("min_len") == 1, "MinLen should be 1."
    else:
        pytest.fail("Annotations for '_results' do not contain the expected metadata.")


def test_kminlen_constraint():
    """Test kminlen constraint applied on set_results method"""
    r = Rets()
    # NOTE: Check that we can add at least one result
    r.set_results(1)
    assert r.results == [1], "Expected _results to contain [1]."
    # NOTE: Check that if no results are added, it raises a ValueError due to kminlen
    with pytest.raises(ValueError, match="Composite type length should not be below 1"):
        r.set_results()


def test_results_and_errors():
    """Test if the 'results' and 'errors' properties are being set correctly"""
    r = Rets()
    # NOTE: Directly set the attributes
    r._results = [1, 2, 3]
    r._errors = [Exception("Error 1")]
    # NOTE: Ensure properties return correct values
    assert r.results == [1, 2, 3], "Expected _results to be [1, 2, 3]."
    # NOTE: Check the message of the exception rather than the instance itself
    assert [str(e) for e in r.errors] == ["Error 1"], "Expected _errors to be ['Error 1']."


def test_min_len_constraint():
    """Test if set_results method raises ValueError when there are fewer results than required (due to MinLen)"""
    r = Rets()
    # NOTE: This should raise a ValueError because kminlen is applied and the list is empty
    with pytest.raises(ValueError, match="Composite type length should not be below 1"):
        r.set_results()


# CODE DUMP
