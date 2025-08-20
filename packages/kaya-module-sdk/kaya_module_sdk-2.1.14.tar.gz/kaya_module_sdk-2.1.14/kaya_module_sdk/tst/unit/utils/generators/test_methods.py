import pytest

from kaya_module_sdk.src.module.arguments import Args
from kaya_module_sdk.sdk import kaya_io

# TESTS


@pytest.mark.parametrize(
    "kaya_io_decorated_args_type",
    [{"_field1": 10, "_field2": "test"}],
    indirect=True,  # NOTE: Pass parameter to the fixture
)
def test_dynamic_init(kaya_io_decorated_args_type):
    obj = kaya_io_decorated_args_type
    assert isinstance(obj, Args)


@pytest.mark.parametrize(
    "kaya_io_decorated_args_type",
    [{"_field1": 10, "_field2": "test"}],
    indirect=True,
)
def test_setter(kaya_io_decorated_args_type):
    obj = kaya_io_decorated_args_type
    obj.set_field1(20)
    obj.set_field2("updated")
    assert obj.field1 == 20
    assert obj.field2 == "updated"


@pytest.mark.parametrize(
    "kaya_io_decorated_args_type",
    [{"_field1": 10, "_field2": "test"}],
    indirect=True,
)
def test_getter(kaya_io_decorated_args_type):
    obj = kaya_io_decorated_args_type
    assert obj.field1 == 10
    assert obj.field2 == "test"


def test_missing_annotated_field():
    @kaya_io()
    class MissingAnnotatedFieldClass:
        field1: int  # Not Annotated, should be ignored

    obj = MissingAnnotatedFieldClass()
    assert not hasattr(obj, "field1")


@pytest.mark.parametrize(
    "kaya_io_decorated_args_type",
    [{"_field1": None, "_field2": None}],
    indirect=True,
)
def test_init_optional_fields(kaya_io_decorated_args_type):
    obj = kaya_io_decorated_args_type
    assert obj.field1 is None
    assert obj.field2 is None


@pytest.mark.parametrize(
    "kaya_io_decorated_args_type",
    [{"_field1": 10, "_field2": "test"}],
    indirect=True,
)
def test_generated_methods(kaya_io_decorated_args_type):
    obj = kaya_io_decorated_args_type
    assert getattr(obj, "field1")
    assert callable(getattr(obj, "set_field1"))
    assert getattr(obj, "field2")
    assert callable(getattr(obj, "set_field2"))
