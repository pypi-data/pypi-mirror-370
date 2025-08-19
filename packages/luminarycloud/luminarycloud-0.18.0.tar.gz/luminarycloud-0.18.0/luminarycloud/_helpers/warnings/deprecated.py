# mypy: ignore-errors

import warnings
from functools import wraps
from typing import Callable, TypeVar

C = TypeVar("C")


def deprecated(reason: str, version: str = "") -> Callable[[C], C]:
    """
    Mark a class or function as deprecated.

    Parameters
    ----------
    reason : str
        The reason for deprecation.
    """

    def decorator(f: C) -> C:
        if isinstance(f, type):
            return _deprecated_class(f, reason)
        else:
            return _deprecated_function(f, reason)

    return decorator


def _deprecated_class(cls: type[C], reason: str) -> type[C]:
    old_init = cls.__init__

    @wraps(old_init)
    def new_init(self, *args, **kwargs):
        warnings.warn(
            f"{cls.__name__} is deprecated: {reason}",
            category=DeprecationWarning,
            stacklevel=2,
        )
        return old_init(self, *args, **kwargs)

    cls.__init__ = new_init
    return cls


def _deprecated_function(f: Callable, reason: str) -> Callable:
    @wraps(f)
    def new_func(*args, **kwargs):
        warnings.warn(
            f"{f.__name__}() is deprecated: {reason}",
            category=DeprecationWarning,
            stacklevel=2,
        )
        return f(*args, **kwargs)

    return new_func
