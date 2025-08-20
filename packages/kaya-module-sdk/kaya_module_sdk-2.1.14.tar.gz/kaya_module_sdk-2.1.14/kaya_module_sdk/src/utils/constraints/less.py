from typing import Callable, Any


def klt(lt_value: str | int | float) -> Callable:
    def decorator(func: Callable) -> Callable:
        def wrapper(*args: str | int | float, **kwargs: dict[str, str | int | float]) -> Any:
            for arg_value in args:
                if isinstance(arg_value, (int, float)) and isinstance(lt_value, (int, float)) and arg_value >= lt_value:
                    raise ValueError(f"Value should be less than {lt_value}")
            return func(*args, **kwargs)

        return wrapper

    return decorator
