import pytest

from kaya_module_sdk.src.utils.constraints.less import klt


def test_argument_less_than_lt_value():
    """Argument is less than the specified lt_value"""

    @klt(10)
    def func(a):
        return a

    result = func(5)  # Argument is less than 10
    assert result == 5


def test_argument_equal_to_lt_value():
    """Argument is equal to the specified lt_value"""

    @klt(10)
    def func(a):
        return a

    with pytest.raises(ValueError, match="Value should be less than 10"):
        func(10)  # Argument is equal to 10, which is not allowed


def test_argument_greater_than_lt_value():
    """Argument is greater than the specified lt_value"""

    @klt(10)
    def func(a):
        return a

    with pytest.raises(ValueError, match="Value should be less than 10"):
        func(15)  # Argument is greater than 10, which is not allowed


def test_multiple_arguments_with_violation():
    """Multiple arguments with one violating the lt_value constraint"""

    @klt(10)
    def func(a, b):
        return a + b

    with pytest.raises(ValueError, match="Value should be less than 10"):
        func(5, 12)  # b is greater than 10, should raise an error


def test_multiple_arguments_without_violation():
    """Multiple arguments with none violating the lt_value constraint"""

    @klt(10)
    def func(a, b):
        return a + b

    result = func(5, 3)  # None of the arguments violate the constraint
    assert result == 8


def test_float_argument_less_than_lt_value():
    """Floating point number is less than lt_value"""

    @klt(10)
    def func(a):
        return a

    result = func(9.9)  # Float argument is less than 10
    assert result == 9.9


def test_float_argument_greater_than_or_equal_to_lt_value():
    """Floating point number is greater than or equal to lt_value"""

    @klt(10)
    def func(a):
        return a

    with pytest.raises(ValueError, match="Value should be less than 10"):
        func(10.0)  # Float argument equals 10, should raise an error
    with pytest.raises(ValueError, match="Value should be less than 10"):
        func(15.5)  # Float argument greater than 10, should raise an error


def test_non_numeric_argument():
    """Non-numeric argument should be allowed"""

    @klt(10)
    def func(a):
        return a

    result = func("hello")  # Non-numeric argument, should be allowed
    assert result == "hello"


def test_multiple_arguments_with_non_numeric():
    """Multiple arguments with a non-numeric argument"""

    @klt(10)
    def func(a, b):
        return a + str(b)

    result = func("hello", 8)  # Non-numeric argument is allowed
    assert result == "hello8"


def test_argument_zero():
    """Edge case - Argument is exactly 0 (boundary value)"""

    @klt(1)
    def func(a):
        return a

    result = func(0)  # Zero is less than 1, so it should be valid
    assert result == 0


def test_large_number():
    """Very large number that does not raise error"""

    @klt(1000000)
    def func(a):
        return a

    result = func(999999)  # Argument is less than 1000000, so valid
    assert result == 999999


def test_large_number_error():
    """Very large number that raises an error"""

    @klt(1000000)
    def func(a):
        return a

    with pytest.raises(ValueError, match="Value should be less than 1000000"):
        func(1000000)  # Argument equals the limit, so error should be raised
