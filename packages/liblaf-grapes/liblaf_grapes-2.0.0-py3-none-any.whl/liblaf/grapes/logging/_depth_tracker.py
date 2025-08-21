import contextlib
import contextvars
import types
from collections.abc import Callable
from typing import Any, Self, overload, override

import attrs

from liblaf.grapes import functools as _ft
from liblaf.grapes import itertools as _it

_depth: contextvars.ContextVar[int] = contextvars.ContextVar("depth", default=0)


@attrs.define
class DepthTrackerDecorator(contextlib.AbstractContextManager):
    _depth_inc: int | None = attrs.field(default=None, alias="depth_inc")
    _token: contextvars.Token[int] = attrs.field(default=None, init=False)

    @override  # impl contextlib.AbstractContextManager
    def __enter__(self) -> Self:
        self._token = _depth.set(_depth.get() + _it.first_not_none(self._depth_inc, 1))
        return self

    @override  # impl contextlib.AbstractContextManager
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
        /,
    ) -> None:
        _depth.reset(self._token)
        del self._token

    def __call__[C: Callable](self, func: C, /) -> C:
        @_ft.decorator
        def wrapper(
            wrapped: Callable, _instance: Any, args: tuple, kwargs: dict[str, Any]
        ) -> Any:
            token: contextvars.Token[int] = _depth.set(
                _depth.get() + _it.first_not_none(self._depth_inc, 2)
            )
            try:
                return wrapped(*args, **kwargs)
            finally:
                _depth.reset(token)

        return wrapper(func)


@attrs.define
class DepthTracker:
    @overload
    def __call__(self, /, *, depth: int | None = None) -> DepthTrackerDecorator: ...
    @overload
    def __call__[C: Callable](self, func: C, /, *, depth: int | None = None) -> C: ...
    def __call__(
        self, func: Callable | None = None, /, *, depth: int | None = None
    ) -> Callable:
        decorator = DepthTrackerDecorator(depth_inc=depth)
        if func is None:
            return decorator
        return decorator(func)

    @property
    def depth(self) -> int:
        return _depth.get()


depth_tracker: DepthTracker = DepthTracker()
