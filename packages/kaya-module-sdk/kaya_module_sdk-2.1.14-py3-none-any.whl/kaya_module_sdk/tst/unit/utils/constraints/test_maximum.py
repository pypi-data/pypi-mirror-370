import pytest

from kaya_module_sdk.src.utils.constraints.maximum import kmax


def test_all_args_below_max():
    """All arguments are below the maximum value"""

    @kmax(10)
    def func(*args):
        return sum(args)

    result = func(1, 2, 3)  # All values are ≤ 10
    assert result == 6


def test_args_equal_to_max():
    """Arguments equal to the maximum value"""

    @kmax(10)
    def func(*args):
        return sum(args)

    result = func(10, 10)  # All values are exactly 10
    assert result == 20


def test_arg_exceeds_max():
    """Argument exceeds the maximum value"""

    @kmax(10)
    def func(*args):
        return sum(args)

    with pytest.raises(ValueError, match="Value should be lesser than or equal to 10"):
        func(5, 15)  # 15 exceeds the max value of 10


def test_mixed_arguments():
    """Mixed valid and invalid arguments"""

    @kmax(10)
    def func(*args):
        return sum(args)

    with pytest.raises(ValueError, match="Value should be lesser than or equal to 10"):
        func(3, 10, 11)  # 11 exceeds the max value


def test_non_numeric_arguments():
    """Non-numeric arguments"""

    @kmax(10)
    def func(*args):
        return " ".join(map(str, args))

    result = func("hello", "world")  # Non-numeric arguments, should not raise an error
    assert result == "hello world"


def test_empty_arguments():
    """Empty arguments"""

    @kmax(10)
    def func(*args):
        return len(args)

    result = func()  # No arguments provided, should not raise an error
    assert result == 0


def test_keyword_arguments_ignored():
    """Keyword arguments are ignored"""

    @kmax(10)
    def func(*args, **kwargs):
        return len(args), kwargs

    result = func(5, 7, key="value")  # Only positional args are checked
    assert result == (2, {"key": "value"})


def test_single_argument_above_max():
    """Single argument above the max"""

    @kmax(10)
    def func(arg):
        return arg

    with pytest.raises(ValueError, match="Value should be lesser than or equal to 10"):
        func(20)  # Argument 20 exceeds the max of 10


def test_single_argument_equal_to_max():
    """Single argument equal to the max"""

    @kmax(10)
    def func(arg):
        return arg

    result = func(10)  # Argument equals the max of 10
    assert result == 10


def test_large_range_of_arguments():
    """Large range of arguments"""

    @kmax(1000)
    def func(*args):
        return max(args)

    result = func(*range(1001))  # All values ≤ 1000
    assert result == 1000
    with pytest.raises(ValueError, match="Value should be lesser than or equal to 1000"):
        func(*range(1002))  # 1001 exceeds the max


def test_function_without_args():
    """Decorator applied to functions with no *args"""

    @kmax(10)
    def func():
        return "No arguments"

    result = func()  # No *args, should work without issues
    assert result == "No arguments"
