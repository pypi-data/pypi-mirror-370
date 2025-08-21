import functools
import types
from collections.abc import Callable, Iterable
from typing import Any

from ._timer import Timer


@functools.singledispatch
def _timer_dispatch(*args, **kwargs) -> Any:
    return Timer(*args, **kwargs)


@_timer_dispatch.register(str)
@_timer_dispatch.register(types.NoneType)
def _timer_name(name: str | None, /, **kwargs) -> Timer:
    return Timer(name=name, **kwargs)


@_timer_dispatch.register(Callable)
@_timer_dispatch.register(Iterable)
def _timer_wrapper[T: Callable | Iterable](wrapped: T, /, **kwargs) -> T:
    return Timer(**kwargs)(wrapped)


def timer(*args, **kwargs) -> Any:
    if len(args) > 0:
        return _timer_dispatch(*args, **kwargs)
    return Timer(*args, **kwargs)
