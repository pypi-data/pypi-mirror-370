from typing import Callable, Any


def klte(lte_value: str | int | float) -> Callable:
    def decorator(func: Callable) -> Callable:
        def wrapper(*args: str | int | float, **kwargs: dict[str, str | int | float]) -> Any:
            for arg_value in args:
                if (
                    isinstance(arg_value, (int, float))
                    and isinstance(lte_value, (int, float))
                    and arg_value > lte_value
                ):
                    raise ValueError(f"Value should be less than or equal to {lte_value}")
            return func(*args, **kwargs)

        return wrapper

    return decorator
