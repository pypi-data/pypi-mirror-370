import pytest

from kaya_module_sdk.src.utils.constraints.value_range import krange


def test_all_args_within_range():
    """All arguments within the range"""

    @krange(10, 20)
    def func(*args):
        return sum(args)

    result = func(10, 15, 20)  # All values are within [10, 20]
    assert result == 45


def test_args_equal_to_boundaries():
    """Arguments equal to range boundaries"""

    @krange(10, 20)
    def func(*args):
        return sum(args)

    result = func(10, 20)  # Values equal to the boundaries [10, 20]
    assert result == 30


def test_arg_below_range():
    """Argument below the range"""

    @krange(10, 20)
    def func(*args):
        return sum(args)

    with pytest.raises(ValueError, match="Value should be in the 10-20 range"):
        func(9, 15)  # 9 is below the range


def test_arg_above_range():
    """Argument above the range"""

    @krange(10, 20)
    def func(*args):
        return sum(args)

    with pytest.raises(ValueError, match="Value should be in the 10-20 range"):
        func(15, 21)  # 21 is above the range


def test_mixed_arguments():
    """Mixed valid and invalid arguments"""

    @krange(10, 20)
    def func(*args):
        return sum(args)

    with pytest.raises(ValueError, match="Value should be in the 10-20 range"):
        func(10, 15, 25)  # 25 is outside the range


def test_non_numeric_arguments():
    """Non-numeric arguments"""

    @krange(10, 20)
    def func(*args):
        return " ".join(map(str, args))

    result = func("hello", "world")  # Non-numeric arguments, should not raise an error
    assert result == "hello world"


def test_empty_arguments():
    """Empty arguments"""

    @krange(10, 20)
    def func(*args):
        return len(args)

    result = func()  # No arguments provided, should not raise an error
    assert result == 0


def test_keyword_arguments_ignored():
    """Keyword arguments are ignored"""

    @krange(10, 20)
    def func(*args, **kwargs):
        return len(args), kwargs

    result = func(10, 15, key="value")  # Only positional args are checked
    assert result == (2, {"key": "value"})


def test_single_argument_below_range():
    """Single argument below the range"""

    @krange(10, 20)
    def func(arg):
        return arg

    with pytest.raises(ValueError, match="Value should be in the 10-20 range"):
        func(9)  # Argument 9 is below the range


def test_single_argument_equal_to_range():
    """Single argument equal to the range"""

    @krange(10, 20)
    def func(arg):
        return arg

    result = func(10)  # Argument equals the lower boundary
    assert result == 10

    result = func(20)  # Argument equals the upper boundary
    assert result == 20


def test_single_argument_above_range():
    """Single argument above the range"""

    @krange(10, 20)
    def func(arg):
        return arg

    with pytest.raises(ValueError, match="Value should be in the 10-20 range"):
        func(21)  # Argument 21 is above the range


def test_large_range_of_arguments():
    """Large range of arguments"""

    @krange(0, 100)
    def func(*args):
        return max(args)

    result = func(*range(0, 101))  # All values are within [0, 100]
    assert result == 100

    with pytest.raises(ValueError, match="Value should be in the 0-100 range"):
        func(*range(-1, 101))  # -1 is outside the range


def test_function_without_args():
    """Decorator applied to functions with no *args"""

    @krange(10, 20)
    def func():
        return "No arguments"

    result = func()  # No *args, should work without issues
    assert result == "No arguments"
