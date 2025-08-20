import pytest

from kaya_module_sdk.src.utils.constraints.length import klen

# UTILS


@klen(2)
def add(a, b):
    return a + b


@klen(3)
def concatenate(a, b, c):
    return f"{a}{b}{c}"


@klen(1)
def single_arg_function(value):
    return value * 2


# TESTS


def test_valid_arguments():
    """Test valid arguments that meet the condition."""
    assert add(1, 2) == 3
    assert concatenate("a", "b", "c") == "abc"
    assert single_arg_function(10) == 20


def test_invalid_arguments_length():
    """Test invalid argument lengths that fail the condition."""
    with pytest.raises(ValueError, match="Composite type length should be equal to 2"):
        add(1)
    with pytest.raises(ValueError, match="Composite type length should be equal to 3"):
        concatenate("a", "b")
    with pytest.raises(ValueError, match="Composite type length should be equal to 1"):
        single_arg_function(10, 20)


def test_no_arguments():
    """Test cases where the function receives no arguments."""

    @klen(0)
    def no_arg_function():
        return "no arguments"

    assert no_arg_function() == "no arguments"
    with pytest.raises(ValueError, match="Composite type length should be equal to 0"):
        no_arg_function(1)


def test_edge_cases_with_empty_args():
    """Test edge cases with empty arguments."""

    @klen(0)
    def empty_args_function():
        return "empty"

    assert empty_args_function() == "empty"

    @klen(1)
    def single_empty_arg_function(arg):
        return arg

    with pytest.raises(ValueError, match="Composite type length should be equal to 1"):
        single_empty_arg_function()


def test_keyword_arguments_ignored():
    """
    Test cases where the function receives keyword arguments.
    Only positional arguments are validated.
    """

    @klen(2)
    def func_with_kwargs(a, b, c=None):
        return a + b

    assert func_with_kwargs(1, 2, c=3) == 3
    with pytest.raises(ValueError, match="Composite type length should be equal to 2"):
        func_with_kwargs(1, c=3)


def test_nested_functions():
    """Test cases where the decorated function is nested inside another function."""

    def outer_function():
        @klen(1)
        def inner_function(a):
            return a * 2

        return inner_function

    inner = outer_function()
    assert inner(3) == 6
    with pytest.raises(ValueError, match="Composite type length should be equal to 1"):
        inner(1, 2)


def test_non_numeric_types():
    """Test cases with non-numeric argument types."""

    @klen(2)
    def non_numeric_function(a, b):
        return f"{a}-{b}"

    assert non_numeric_function("hello", [1, 2, 3]) == "hello-[1, 2, 3]"
    assert non_numeric_function({"key": "value"}, (1, 2)) == "{'key': 'value'}-(1, 2)"
    with pytest.raises(ValueError, match="Composite type length should be equal to 2"):
        non_numeric_function(
            "hello",
        )


def test_large_argument_length():
    """Test cases with large argument lengths."""

    @klen(100)
    def large_args_function(*args):
        return sum(args)

    args = [1] * 100
    assert large_args_function(*args) == 100
    with pytest.raises(ValueError, match="Composite type length should be equal to 100"):
        large_args_function(*args[:-1])


def test_return_value_unchanged():
    """Ensure the decorator does not alter the return value."""

    @klen(2)
    def always_return_true(a, b):
        return True

    assert always_return_true(1, 2) is True
    with pytest.raises(ValueError, match="Composite type length should be equal to 2"):
        always_return_true(1)


def test_partial_arguments():
    """Test cases where some arguments are valid, and others are invalid."""

    @klen(3)
    def partial_args(a, b, c):
        return a + b + c

    assert partial_args(1, 2, 3) == 6
    with pytest.raises(ValueError, match="Composite type length should be equal to 3"):
        partial_args(1, 2)
