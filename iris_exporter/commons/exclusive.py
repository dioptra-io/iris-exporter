from functools import wraps
from hashlib import sha256
from itertools import chain
from typing import Any, Callable, ParamSpec, TypeVar

from redis import Redis
from redis.exceptions import LockError

from iris_exporter.commons.logger import logger

P = ParamSpec("P")
R = TypeVar("R")


def format_args(*args: Any, **kwargs: Any) -> str:
    """
    >>> format_args(1, 2)
    '1, 2'
    >>> format_args(c=3)
    'c=3'
    >>> format_args(1, 2, c=3)
    '1, 2, c=3'
    """
    args_ = (str(x) for x in args)
    kwargs_ = (f"{x}={y}" for x, y in kwargs.items())
    return ", ".join(chain(args_, kwargs_))


def exclusive(redis_client: Redis, namespace: str) -> Callable:
    def decorator(f: Callable[P, R]) -> Callable[P, R | None]:
        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> R | None:
            params_hash = sha256(f"{args}-{kwargs}".encode()).hexdigest()
            lock_key = f"{namespace}:{f.__name__}-{params_hash}"
            try:
                with redis_client.lock(lock_key, blocking_timeout=0, timeout=86400):
                    logger.info("lock=acquired")
                    return f(*args, **kwargs)
            except LockError:
                logger.info("lock=already-acquired")
            return None

        return wrapper

    return decorator
