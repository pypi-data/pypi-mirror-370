import pytest

from kaya_module_sdk.src.utils.constraints.equal import keq

# UTILS


@keq(10)
def add(a, b):
    return a + b


@keq(5)
def multiply(a, b):
    return a * b


# TESTS


def test_valid_arguments():
    """Test cases where all arguments meet the condition."""
    assert add(10, 10) == 20
    assert multiply(5, 5) == 25


def test_invalid_arguments():
    """Test cases where an argument fails the condition."""
    with pytest.raises(ValueError, match="Value should be equal to 10"):
        add(10, 5)
    with pytest.raises(ValueError, match="Value should be equal to 5"):
        multiply(5, 10)


def test_mixed_types():
    """Test cases where non-numeric arguments are ignored."""

    @keq(100)
    def concat_numbers_and_strings(a, b):
        return f"{a}-{b}"

    # NOTE: Non-numeric arguments should not raise errors
    assert concat_numbers_and_strings("hello", "world") == "hello-world"
    assert concat_numbers_and_strings(100, "world") == "100-world"
    # NOTE: Numeric arguments that fail the condition should raise an error
    with pytest.raises(ValueError, match="Value should be equal to 100"):
        concat_numbers_and_strings(50, "world")


def test_no_arguments():
    """Test cases where the function receives no arguments."""

    @keq(42)
    def no_arg_function():
        return "no arguments"

    assert no_arg_function() == "no arguments"


def test_keyword_arguments():
    """
    Test cases where the function receives keyword arguments.
    The decorator only checks positional arguments.
    """

    @keq(7)
    def custom_func(a, b, c=None):
        return a + b

    # NOTE: Only positional arguments are checked
    assert custom_func(7, 7, c=14) == 14
    # NOTE: Invalid positional argument
    with pytest.raises(ValueError, match="Value should be equal to 7"):
        custom_func(7, 8, c=14)


def test_nested_functions():
    """Test cases where the decorated function is nested within another function."""

    def outer_function():
        @keq(3)
        def inner_function(a):
            return a * 2

        return inner_function

    inner = outer_function()
    assert inner(3) == 6  # Valid input
    with pytest.raises(ValueError, match="Value should be equal to 3"):
        inner(4)


def test_edge_cases():
    """Test cases for edge values like zero and negative numbers."""

    @keq(0)
    def check_zero(a):
        return a

    assert check_zero(0) == 0
    with pytest.raises(ValueError, match="Value should be equal to 0"):
        check_zero(1)

    @keq(-5)
    def check_negative(a):
        return a

    assert check_negative(-5) == -5
    with pytest.raises(ValueError, match="Value should be equal to -5"):
        check_negative(5)
