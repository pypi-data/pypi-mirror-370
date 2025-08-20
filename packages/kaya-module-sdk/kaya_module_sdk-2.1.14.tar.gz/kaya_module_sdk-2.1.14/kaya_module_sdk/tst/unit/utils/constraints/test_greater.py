import pytest

from kaya_module_sdk.src.utils.constraints.greater import kgt

# UTILS


@kgt(10)
def add(a, b):
    return a + b


@kgt(5)
def multiply(a, b):
    return a * b


@kgt(100)
def single_arg_function(value):
    return value * 2


# TESTS


def test_valid_arguments():
    """Test valid arguments that meet the condition."""
    assert add(11, 12) == 23
    assert multiply(6, 7) == 42
    assert single_arg_function(101) == 202


def test_invalid_arguments():
    """Test invalid arguments that fail the condition."""
    with pytest.raises(ValueError, match="Value should be greater than 10"):
        add(9, 12)
    with pytest.raises(ValueError, match="Value should be greater than 5"):
        multiply(5, 6)
    with pytest.raises(ValueError, match="Value should be greater than 100"):
        single_arg_function(100)


def test_mixed_types():
    """Test cases where non-numeric arguments are ignored."""

    @kgt(10)
    def mixed_function(a, b):
        return f"{a}-{b}"

    assert mixed_function("hello", "world") == "hello-world"
    assert mixed_function(11, "world") == "11-world"
    with pytest.raises(ValueError, match="Value should be greater than 10"):
        mixed_function(9, "world")


def test_no_arguments():
    """Test cases where the function receives no arguments."""

    @kgt(42)
    def no_arg_function():
        return "no arguments"

    assert no_arg_function() == "no arguments"


def test_keyword_arguments():
    """
    Test cases where the function receives keyword arguments.
    The decorator only validates positional arguments.
    """

    @kgt(7)
    def custom_func(a, b, c=None):
        return a + b

    assert custom_func(8, 9, c=14) == 17
    with pytest.raises(ValueError, match="Value should be greater than 7"):
        custom_func(7, 8, c=14)


def test_nested_functions():
    """Test cases where the decorated function is nested inside another function."""

    def outer_function():
        @kgt(3)
        def inner_function(a):
            return a * 2

        return inner_function

    inner = outer_function()
    assert inner(4) == 8
    with pytest.raises(ValueError, match="Value should be greater than 3"):
        inner(3)


def test_edge_cases():
    """Test edge cases, including zero and negative numbers."""

    @kgt(0)
    def check_zero(a):
        return a

    assert check_zero(1) == 1
    with pytest.raises(ValueError, match="Value should be greater than 0"):
        check_zero(0)

    @kgt(-5)
    def check_negative(a):
        return a

    assert check_negative(-4) == -4
    with pytest.raises(ValueError, match="Value should be greater than -5"):
        check_negative(-6)


def test_multiple_decorators():
    """Test cases where multiple decorators are applied to a single function."""

    @kgt(2)
    @kgt(5)
    def double_decorated_function(a):
        return a * 2

    with pytest.raises(ValueError, match="Value should be greater than 5"):
        double_decorated_function(3)
    assert double_decorated_function(6) == 12


def test_non_numeric_types():
    """Test cases where arguments are of unsupported types."""

    @kgt(10)
    def func(a, b):
        return f"{a}-{b}"

    assert func("string", [1, 2, 3]) == "string-[1, 2, 3]"
    assert func(11, {"key": "value"}) == "11-{'key': 'value'}"
    with pytest.raises(ValueError, match="Value should be greater than 10"):
        func(9, {"key": "value"})


def test_partial_arguments():
    """Test cases where some arguments are valid, and others are invalid."""

    @kgt(42)
    def partial_args(a, b, c):
        return a + b + c

    with pytest.raises(ValueError, match="Value should be greater than 42"):
        partial_args(43, 41, 44)
    assert partial_args(43, 44, 45) == 132


def test_return_value_unchanged():
    """Ensure the decorator does not alter the return value."""

    @kgt(1)
    def always_return_true(a):
        return True

    assert always_return_true(2) is True
    with pytest.raises(ValueError, match="Value should be greater than 1"):
        always_return_true(1)
