from collections.abc import Callable
from typing import Any

from liblaf.grapes import functools as _ft
from liblaf.grapes import pretty
from liblaf.grapes.logging import depth_tracker

from ._base import BaseTimer


def timed_callable[C: Callable](func: C, timer: BaseTimer) -> C:
    if timer.name is None:
        timer.name = pretty.pretty_func(func)

    @_ft.decorator
    @depth_tracker
    def wrapper(wrapped: C, _instance: Any, args: tuple, kwargs: dict[str, Any]) -> Any:
        timer.start()
        try:
            return wrapped(*args, **kwargs)
        finally:
            timer.stop()

    proxy: C = wrapper(func)
    proxy._self_timer = timer  # pyright: ignore[reportFunctionMemberAccess] # noqa: SLF001
    return proxy
