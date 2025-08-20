from typing import Callable, Any


def kmax(max_value: str | int | float) -> Callable:
    def decorator(func: Callable) -> Callable:
        def wrapper(*args: str | int | float, **kwargs: dict[str, str | int | float]) -> Any:
            for arg_value in args:
                if (
                    isinstance(arg_value, (int, float))
                    and isinstance(max_value, (int, float))
                    and arg_value > max_value
                ):
                    raise ValueError(f"Value should be lesser than or equal to {max_value}")
            return func(*args, **kwargs)

        return wrapper

    return decorator
