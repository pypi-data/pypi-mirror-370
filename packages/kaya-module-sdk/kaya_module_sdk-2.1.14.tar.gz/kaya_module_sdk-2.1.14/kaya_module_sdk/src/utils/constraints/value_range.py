from typing import Callable, Any


def krange(range_min_value: str | int | float, range_max_value: str | int | float) -> Callable:
    def decorator(func: Callable) -> Callable:
        def wrapper(*args: str | int | float, **kwargs: dict[str, str | int | float]) -> Any:
            for arg_value in args:
                if (
                    isinstance(arg_value, (int, float))
                    and isinstance(range_min_value, (int, float))
                    and isinstance(range_max_value, (int, float))
                    and (arg_value < range_min_value or arg_value > range_max_value)
                ):
                    raise ValueError(f"Value should be in the {range_min_value}-{range_max_value} range")
            return func(*args, **kwargs)

        return wrapper

    return decorator
