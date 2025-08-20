import pytest

from kaya_module_sdk.src.utils.constraints.min_len import kminlen


def test_args_above_min_len():
    """Number of arguments is above the minimum length"""

    @kminlen(3)
    def func(*args):
        return sum(args)

    result = func(1, 2, 3, 4)  # Length is 4, which is above the minimum of 3
    assert result == 10


def test_args_equal_to_min_len():
    """Number of arguments equals the minimum length"""

    @kminlen(3)
    def func(*args):
        return sum(args)

    result = func(1, 2, 3)  # Length is exactly 3
    assert result == 6


def test_args_below_min_len():
    """Number of arguments is below the minimum length"""

    @kminlen(3)
    def func(*args):
        return sum(args)

    with pytest.raises(ValueError, match="Composite type length should not be below 3"):
        func(1, 2)  # Length is 2, which is below the minimum of 3


def test_no_arguments():
    """No arguments are passed"""

    @kminlen(1)
    def func(*args):
        return len(args)

    with pytest.raises(ValueError, match="Composite type length should not be below 1"):
        func()  # No arguments passed


def test_min_len_zero():
    """Edge case where min length is 0"""

    @kminlen(0)
    def func(*args):
        return len(args)

    result = func()  # Min length is 0, so no error should be raised
    assert result == 0


def test_function_without_args():
    """Decorator applied to functions with no *args"""

    @kminlen(1)
    def func():
        return "No arguments here"

    with pytest.raises(ValueError, match="Composite type length should not be below 1"):
        func()  # Function without *args doesn't meet the min length


def test_function_with_kwargs():
    """Function with both *args and **kwargs"""

    @kminlen(2)
    def func(*args, **kwargs):
        return len(args), kwargs

    with pytest.raises(ValueError, match="Composite type length should not be below 2"):
        func(1, key="value")  # Only positional arguments are checked
    result = func(1, 2, key="value")  # Meets the min length
    assert result == (2, {"key": "value"})


def test_non_numeric_arguments():
    """Non-numeric arguments"""

    @kminlen(2)
    def func(*args):
        return " ".join(args)

    with pytest.raises(ValueError, match="Composite type length should not be below 2"):
        func("hello")  # Only one argument, below the min length
    result = func("hello", "world")  # Meets the min length
    assert result == "hello world"


def test_mixed_argument_types():
    """Mixed argument types"""

    @kminlen(2)
    def func(*args):
        return [type(arg) for arg in args]

    with pytest.raises(ValueError, match="Composite type length should not be below 2"):
        func(1)  # Length is 1, below the min length

    result = func(1, "two")  # Meets the min length
    assert result == [int, str]


def test_large_number_of_arguments():
    """Large number of arguments"""

    @kminlen(100)
    def func(*args):
        return len(args)

    with pytest.raises(ValueError, match="Composite type length should not be below 100"):
        func(*range(99))  # Length is 99, below the min length

    result = func(*range(100))  # Length is exactly 100
    assert result == 100


def test_multiple_decorators():
    """Multiple decorators applied"""

    @kminlen(3)
    @kminlen(2)
    def func(*args):
        return sum(args)

    with pytest.raises(ValueError, match="Composite type length should not be below 3"):
        func(1, 2)  # Violates the stricter decorator

    result = func(1, 2, 3)  # Valid for both decorators
    assert result == 6
