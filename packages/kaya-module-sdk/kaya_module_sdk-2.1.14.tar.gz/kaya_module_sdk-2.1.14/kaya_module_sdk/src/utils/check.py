from logging import Logger, getLogger
from typing import get_origin, get_args

log: Logger = getLogger(__name__)


def is_matrix(type_hint: type) -> bool:
    """
    Checks if the given type hint represents a matrix (list of lists).

    Args:
        type_hint (Type): The type hint to check.

    Returns:
        bool: True if the type hint is a matrix, False otherwise.
    """
    log.debug(f"Checking if type hint ({type_hint}) is of matrix type...")
    if get_origin(type_hint) is list:
        inner_type = get_args(type_hint)
        if inner_type and get_origin(inner_type[0]) is list:
            log.debug(f"Matrix type confirmed for ({type_hint})!")
            return True
    log.debug(f"Type hint ({type_hint}) is not of matrix type!")
    return False
