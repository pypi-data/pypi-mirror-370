from typing import Callable, TypeVar

T = TypeVar('T', bound=Callable)

def public(func: T) -> T:
    """Decorator to mark an endpoint as an endpoint that requires no authentication.

    Args:
        func: The function to decorate

    Returns:
        The decorated function
    """
