import contextlib
import types
from collections.abc import Callable, Iterable
from typing import Any, Self, overload, override

import attrs

from liblaf.grapes.logging import depth_tracker

from ._base import BaseTimer
from ._callable import timed_callable
from ._iterable import TimedIterable


@attrs.define
class Timer(BaseTimer, contextlib.AbstractContextManager):
    @override  # contextlib.AbstractContextManager
    @depth_tracker
    def __enter__(self) -> Self:
        self.start()
        return self

    @override  # contextlib.AbstractContextManager
    @depth_tracker
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
        /,
    ) -> None:
        self.stop()

    @overload
    def __call__[C: Callable](self, func: C, /) -> C: ...
    @overload
    def __call__[I: Iterable](self, iterable: I, /) -> I: ...
    def __call__(self, func_or_iterable: Callable | Iterable, /) -> Any:
        if callable(func_or_iterable):
            return timed_callable(func_or_iterable, self)
        return TimedIterable(func_or_iterable, self)
