import pytest

from kaya_module_sdk.src.utils.metadata.abstract_validation import KValidation


@pytest.mark.parametrize(
    "kvalidation_subclass",
    [{"_data": {"key": "value"}}],
    indirect=True,  # NOTE: Pass parameter to the fixture
)
def test_repr_method(kvalidation_subclass):
    """Test that the __repr__ method calls __str__ correctly."""
    # NOTE: The repr should use the string representation of the object
    assert repr(kvalidation_subclass) == "KValidation: {'key': 'value'}"


@pytest.mark.parametrize(
    "kvalidation_subclass",
    [{"_data": {"key": "value"}}],
    indirect=True,  # NOTE: Pass parameter to the fixture
)
def test_init_subclass(kvalidation_subclass):
    """Test that the subclass can be instantiated correctly."""
    # NOTE: Check if the data attribute is correctly initialized
    assert kvalidation_subclass.get_data() == {"key": "value"}


@pytest.mark.parametrize(
    "kvalidation_subclass",
    [{"_data": {"key": "value"}}],
    indirect=True,  # NOTE: Pass parameter to the fixture
)
def test_invalid_init(kvalidation_subclass):
    """Test that an error is raised when initializing without a valid subclass."""
    with pytest.raises(TypeError):
        # NOTE: KValidation is abstract, so it can't be instantiated directly
        KValidation(kvalidation_subclass)


@pytest.mark.parametrize(
    "kvalidation_subclass",
    [{"_data": {"key": "value"}}],
    indirect=True,  # NOTE: Pass parameter to the fixture
)
def test_str_method(kvalidation_subclass):
    """Test that the __str__ method returns the correct string."""
    # NOTE: The str method should return a custom string representation
    assert str(kvalidation_subclass) == "KValidation: {'key': 'value'}"


@pytest.mark.parametrize(
    "kvalidation_subclass",
    [{"_data": {}}],
    indirect=True,  # note: pass parameter to the fixture
)
def test_repr_with_empty_data(kvalidation_subclass):
    """Test __repr__ method with empty data."""
    # NOTE: Check that the string representation handles empty data
    assert repr(kvalidation_subclass) == "KValidation: {}"


@pytest.mark.parametrize(
    "kvalidation_subclass",
    [{"_data": None}],
    indirect=True,  # note: pass parameter to the fixture
)
def test_repr_with_none_data(kvalidation_subclass):
    """Test __repr__ method with None data."""
    # NOTE: Check that the string representation handles None data
    assert repr(kvalidation_subclass) == "KValidation: None"


@pytest.mark.parametrize(
    "kvalidation_subclass",
    [{"_data": {"nested": {"key": "value"}}}],
    indirect=True,  # note: pass parameter to the fixture
)
def test_repr_with_nested_data(kvalidation_subclass):
    """Test __repr__ method with nested data."""
    # NOTE: Check that the string representation handles nested data
    assert repr(kvalidation_subclass) == "KValidation: {'nested': {'key': 'value'}}"
