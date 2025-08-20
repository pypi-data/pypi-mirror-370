import pytest

from kaya_module_sdk.src.utils.constraints.minimum import kmin


def test_all_args_above_min():
    """All arguments are above the minimum value"""

    @kmin(5)
    def func(*args):
        return sum(args)

    result = func(5, 6, 7)  # All values are ≥ 5
    assert result == 18


def test_args_equal_to_min():
    """Arguments equal to the minimum value"""

    @kmin(5)
    def func(*args):
        return sum(args)

    result = func(5, 5, 5)  # All values are exactly 5
    assert result == 15


def test_arg_below_min():
    """Argument below the minimum value"""

    @kmin(5)
    def func(*args):
        return sum(args)

    with pytest.raises(ValueError, match="Value should be greater than or equal to 5"):
        func(5, 4)  # 4 is below the minimum value of 5


def test_mixed_arguments():
    """Mixed valid and invalid arguments"""

    @kmin(5)
    def func(*args):
        return sum(args)

    with pytest.raises(ValueError, match="Value should be greater than or equal to 5"):
        func(5, 6, 4)  # 4 is below the minimum


def test_non_numeric_arguments():
    """Non-numeric arguments"""

    @kmin(5)
    def func(*args):
        return " ".join(map(str, args))

    result = func("hello", "world")  # Non-numeric arguments, should not raise an error
    assert result == "hello world"


def test_empty_arguments():
    """Empty arguments"""

    @kmin(5)
    def func(*args):
        return len(args)

    result = func()  # No arguments provided, should not raise an error
    assert result == 0


def test_keyword_arguments_ignored():
    """Keyword arguments are ignored"""

    @kmin(5)
    def func(*args, **kwargs):
        return len(args), kwargs

    result = func(5, 6, key="value")  # Only positional args are checked
    assert result == (2, {"key": "value"})


def test_single_argument_below_min():
    """Single argument below the minimum value"""

    @kmin(5)
    def func(arg):
        return arg

    with pytest.raises(ValueError, match="Value should be greater than or equal to 5"):
        func(4)  # Argument 4 is below the minimum


def test_single_argument_equal_to_min():
    """Single argument equal to the minimum value"""

    @kmin(5)
    def func(arg):
        return arg

    result = func(5)  # Argument equals the minimum of 5
    assert result == 5


def test_large_range_of_arguments():
    """Large range of arguments"""

    @kmin(0)
    def func(*args):
        return min(args)

    result = func(*range(0, 100))  # All values are ≥ 0
    assert result == 0
    with pytest.raises(ValueError, match="Value should be greater than or equal to 0"):
        func(*range(-1, 100))  # -1 is below the minimum


def test_function_without_args():
    """Decorator applied to functions with no *args"""

    @kmin(5)
    def func():
        return "No arguments"

    result = func()  # No *args, should work without issues
    assert result == "No arguments"
