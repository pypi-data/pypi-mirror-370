from collections.abc import Callable
from typing import Any


def clone_param_spec[**P, T](
    _func: Callable[P, T], /
) -> Callable[[Any], Callable[P, T]]:
    def wrapper(wrapped: Any, /) -> Callable[P, T]:
        return wrapped

    return wrapper


def clone_signature[C](_source: C, /) -> Callable[[Any], C]:
    def wrapper(obj: Any) -> C:
        return obj

    return wrapper
