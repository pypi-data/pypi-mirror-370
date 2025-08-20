import pytest


@pytest.mark.parametrize(
    "kmetadata_subclass",
    [{"_data": {"_field": "test"}}],
    indirect=True,  # NOTE: Pass parameter to the fixture
)
def test_repr_method(kmetadata_subclass):
    """Test that the __repr__ method calls __str__ correctly."""
    # NOTE: The repr should use the string representation of the object
    assert repr(kmetadata_subclass) == "KMetadata: {'_field': 'test'}"


@pytest.mark.parametrize(
    "kmetadata_subclass",
    [{"_data": {"_field": "test"}}],
    indirect=True,
)
def test_init_subclass(kmetadata_subclass):
    """Test that the subclass can be instantiated correctly."""
    # NOTE: Check if the data attribute is correctly initialized
    assert kmetadata_subclass.get_data() == {"_field": "test"}


@pytest.mark.parametrize(
    "kmetadata_subclass",
    [{"_data": {"_field": "test"}}],
    indirect=True,
)
def test_str_method(kmetadata_subclass):
    """Test that the __str__ method returns the correct string."""
    # NOTE: The str method should return a custom string representation
    assert str(kmetadata_subclass) == "KMetadata: {'_field': 'test'}"


@pytest.mark.parametrize(
    "kmetadata_subclass",
    [{"_data": {}}],
    indirect=True,
)
def test_repr_with_empty_data(kmetadata_subclass):
    """Test __repr__ method with empty data."""
    # NOTE: Check that the string representation handles empty data
    assert repr(kmetadata_subclass) == "KMetadata: {}"


@pytest.mark.parametrize(
    "kmetadata_subclass",
    [{"_data": None}],
    indirect=True,
)
def test_repr_with_none_data(kmetadata_subclass):
    """Test __repr__ method with empty data."""
    # NOTE: Check that the string representation handles empty data
    assert repr(kmetadata_subclass) == "KMetadata: None"


@pytest.mark.parametrize(
    "kmetadata_subclass",
    [{"_data": {"nested": {"key": "value"}}}],
    indirect=True,
)
def test_repr_with_nested_data(kmetadata_subclass):
    """Test __repr__ method with nested data."""
    # NOTE: Check that the string representation handles nested data
    assert repr(kmetadata_subclass) == "KMetadata: {'nested': {'key': 'value'}}"
