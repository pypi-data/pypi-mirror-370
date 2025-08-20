from typing import Callable, Any


def kmin(min_value: str | int | float) -> Callable:
    def decorator(func: Callable) -> Callable:
        def wrapper(*args: str | int | float, **kwargs: dict[str, str | int | float]) -> Any:
            for arg_value in args:
                if (
                    isinstance(arg_value, (int, float))
                    and isinstance(min_value, (int, float))
                    and arg_value < min_value
                ):
                    raise ValueError(f"Value should be greater than or equal to {min_value}")
            return func(*args, **kwargs)

        return wrapper

    return decorator
