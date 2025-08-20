import pytest

from kaya_module_sdk.src.utils.constraints.max_len import kmaxlen


def test_length_below_max():
    @kmaxlen(3)
    def func(*args):
        return sum(args)

    result = func(1, 2, 3)  # Length is 3 (allowed)
    assert result == 6


def test_length_equal_to_max():
    @kmaxlen(3)
    def func(*args):
        return sum(args)

    result = func(1, 2, 3)  # Length is exactly 3 (allowed)
    assert result == 6


def test_length_above_max():
    @kmaxlen(3)
    def func(*args):
        return sum(args)

    with pytest.raises(ValueError, match="Composite type length should not be above 3"):
        func(1, 2, 3, 4)  # Length is 4 (not allowed)


def test_empty_arguments():
    @kmaxlen(3)
    def func(*args):
        return sum(args)

    result = func()  # No arguments, length is 0 (allowed)
    assert result == 0


def test_edge_case_zero_max_len():
    @kmaxlen(0)
    def func(*args):
        return sum(args)

    with pytest.raises(ValueError, match="Composite type length should not be above 0"):
        func(1)  # Length is 1 (not allowed)


def test_non_numeric_arguments():
    @kmaxlen(2)
    def func(*args):
        return " ".join(str(arg) for arg in args)

    result = func("hello", "motherfucker")  # Length is 2 (allowed)
    assert result == "hello motherfucker"


def test_mixed_arguments_below_max():
    @kmaxlen(3)
    def func(*args):
        return len(args)

    result = func("hello", 123, [1, 2, 3])  # Length is 3 (allowed)
    assert result == 3


def test_keyword_arguments_ignored_in_length():
    @kmaxlen(2)
    def func(*args, **kwargs):
        return len(args), kwargs

    result = func(1, 2, key="value")  # Only positional args are counted
    assert result == (2, {"key": "value"})


def test_decorator_applied_to_no_args_function():
    @kmaxlen(1)
    def func():
        return "No arguments here"

    result = func()  # Length of args is 0 (allowed)
    assert result == "No arguments here"
