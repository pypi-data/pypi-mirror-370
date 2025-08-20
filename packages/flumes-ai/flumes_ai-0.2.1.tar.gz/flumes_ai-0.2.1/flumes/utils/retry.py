import time
from functools import wraps
from typing import Callable, Type, Tuple


def retry(
    exceptions: Tuple[Type[Exception], ...],
    *,
    tries: int = 3,
    delay: float = 0.5,
    backoff: float = 2.0,
):
    """Simple exponential-backoff retry decorator."""

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _tries, _delay = tries, delay
            while _tries > 1:
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    time.sleep(_delay)
                    _tries -= 1
                    _delay *= backoff
            return func(*args, **kwargs)

        return wrapper

    return decorator
