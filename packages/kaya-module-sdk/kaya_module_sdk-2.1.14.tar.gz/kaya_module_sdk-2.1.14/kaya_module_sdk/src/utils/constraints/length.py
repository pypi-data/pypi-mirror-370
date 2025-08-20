import inspect

from typing import Any, Callable


def klen(len_value: int) -> Callable:
    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: dict) -> Any:
            # NOTE: Use inspect to check if the function is a method
            signature = inspect.signature(func)
            # NOTE: If the method has 'self' or 'cls' as its first parameter, it's a method
            parameters = list(signature.parameters.keys())
            if len(parameters) > 0 and parameters[0] in ["self", "cls"]:
                # NOTE: If it's a method, exclude `self` or `cls` from the argument length check
                sanitized_args = args[1:]
            else:
                # NOTE: Otherwise, treat it as a normal function
                sanitized_args = args
            if len(sanitized_args) != len_value:
                raise ValueError(f"Composite type length should be equal to {len_value}")
            return func(*args, **kwargs)

        return wrapper

    return decorator
