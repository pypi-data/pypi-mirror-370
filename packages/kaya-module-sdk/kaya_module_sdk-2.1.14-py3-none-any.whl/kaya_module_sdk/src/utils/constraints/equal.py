from typing import Callable, Any


def keq(eq_value: str | int | float) -> Callable:
    def decorator(func: Callable) -> Callable:
        def wrapper(*args: str | int | float, **kwargs: dict[str, str | int | float]) -> Any:
            for arg_value in args:
                if isinstance(arg_value, (int, float)) and isinstance(eq_value, (int, float)) and arg_value != eq_value:
                    raise ValueError(f"Value should be equal to {eq_value}")
            return func(*args, **kwargs)

        return wrapper

    return decorator
