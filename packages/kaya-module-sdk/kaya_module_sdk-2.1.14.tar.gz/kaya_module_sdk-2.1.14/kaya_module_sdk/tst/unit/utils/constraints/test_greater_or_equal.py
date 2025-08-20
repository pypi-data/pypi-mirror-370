import pytest

from kaya_module_sdk.src.utils.constraints.greater_or_equal import kgte

# UTILS


@kgte(10)
def add(a, b):
    return a + b


@kgte(5)
def multiply(a, b):
    return a * b


@kgte(100)
def single_arg_function(value):
    return value * 2


# TESTS


def test_valid_arguments():
    """Test valid arguments that meet the condition."""
    assert add(10, 12) == 22
    assert multiply(5, 7) == 35
    assert single_arg_function(100) == 200


def test_invalid_arguments():
    """Test invalid arguments that fail the condition."""
    with pytest.raises(ValueError, match="Value should be greater than or equal to 10"):
        add(9, 12)
    with pytest.raises(ValueError, match="Value should be greater than or equal to 5"):
        multiply(4, 6)
    with pytest.raises(ValueError, match="Value should be greater than or equal to 100"):
        single_arg_function(99)


def test_mixed_types():
    """Test cases where non-numeric arguments are ignored."""

    @kgte(10)
    def mixed_function(a, b):
        return f"{a}-{b}"

    assert mixed_function("hello", "world") == "hello-world"
    assert mixed_function(10, "world") == "10-world"
    with pytest.raises(ValueError, match="Value should be greater than or equal to 10"):
        mixed_function(9, "world")


def test_no_arguments():
    """Test cases where the function receives no arguments."""

    @kgte(42)
    def no_arg_function():
        return "no arguments"

    assert no_arg_function() == "no arguments"


def test_keyword_arguments():
    """
    Test cases where the function receives keyword arguments.
    The decorator only validates positional arguments.
    """

    @kgte(7)
    def custom_func(a, b, c=None):
        return a + b

    assert custom_func(7, 8, c=14) == 15
    with pytest.raises(ValueError, match="Value should be greater than or equal to 7"):
        custom_func(6, 8, c=14)


def test_nested_functions():
    """Test cases where the decorated function is nested inside another function."""

    def outer_function():
        @kgte(3)
        def inner_function(a):
            return a * 2

        return inner_function

    inner = outer_function()
    assert inner(3) == 6
    with pytest.raises(ValueError, match="Value should be greater than or equal to 3"):
        inner(2)


def test_edge_cases():
    """Test edge cases, including zero and negative numbers."""

    @kgte(0)
    def check_zero(a):
        return a

    assert check_zero(0) == 0
    assert check_zero(1) == 1
    with pytest.raises(ValueError, match="Value should be greater than or equal to 0"):
        check_zero(-1)

    @kgte(-5)
    def check_negative(a):
        return a

    assert check_negative(-5) == -5
    assert check_negative(-4) == -4
    with pytest.raises(ValueError, match="Value should be greater than or equal to -5"):
        check_negative(-6)


def test_multiple_decorators():
    """Test cases where multiple decorators are applied to a single function."""

    @kgte(2)
    @kgte(5)
    def double_decorated_function(a):
        return a * 2

    with pytest.raises(ValueError, match="Value should be greater than or equal to 5"):
        double_decorated_function(3)
    assert double_decorated_function(5) == 10


def test_non_numeric_types():
    """Test cases where arguments are of unsupported types."""

    @kgte(10)
    def func(a, b):
        return f"{a}-{b}"

    assert func("string", [1, 2, 3]) == "string-[1, 2, 3]"
    assert func(10, {"key": "value"}) == "10-{'key': 'value'}"
    with pytest.raises(ValueError, match="Value should be greater than or equal to 10"):
        func(9, {"key": "value"})


def test_partial_arguments():
    """Test cases where some arguments are valid, and others are invalid."""

    @kgte(42)
    def partial_args(a, b, c):
        return a + b + c

    with pytest.raises(ValueError, match="Value should be greater than or equal to 42"):
        partial_args(43, 41, 44)
    assert partial_args(42, 43, 44) == 129


def test_return_value_unchanged():
    """Ensure the decorator does not alter the return value."""

    @kgte(1)
    def always_return_true(a):
        return True

    assert always_return_true(1) is True
    with pytest.raises(ValueError, match="Value should be greater than or equal to 1"):
        always_return_true(0)
