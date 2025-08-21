import functools
from collections.abc import Callable, Mapping
from typing import Any, NoReturn, overload

import attrs
import sortedcontainers

from liblaf.grapes import pretty


@attrs.frozen
class Function:
    condition: Callable[..., bool]
    function: Callable
    precedence: int = 0


class NotFoundLookupError(LookupError):
    func: Callable
    args: tuple
    kwargs: Mapping

    def __init__(self, func: Callable, args: tuple, kwargs: Mapping) -> None:
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __str__(self) -> str:
        pretty_call: str = pretty.pretty_call(self.func, self.args, self.kwargs)
        return f"{pretty_call} could not be resolved."


def _fallback(func: Callable) -> Callable[..., NoReturn]:
    def fallback(*args, **kwargs) -> NoReturn:
        raise NotFoundLookupError(func, args, kwargs)

    return fallback


class ConditionalDispatcher:
    fallback: Callable
    functions: sortedcontainers.SortedList[Function]

    def __init__(self) -> None:
        self.functions = sortedcontainers.SortedList(key=lambda f: -f.precedence)

    def __call__(self, *args, **kwargs) -> Any:
        for func in self.functions:
            try:
                if func.condition(*args, **kwargs):
                    return func.function(*args, **kwargs)
            except TypeError:
                continue
        return self.fallback(*args, **kwargs)

    @overload
    def final[**P, T](
        self, fn: Callable[P, T], /, *, fallback: bool = False
    ) -> Callable[P, T]: ...
    @overload
    def final[**P, T](
        self, /, *, fallback: bool = False
    ) -> Callable[[Callable[P, T]], Callable[P, T]]: ...
    def final[**P, T](
        self, func: Callable[P, T] | None = None, /, *, fallback: bool = False
    ) -> Callable:
        if func is None:
            return functools.partial(self.final, fallback=fallback)
        if fallback:
            self.fallback = func
        else:
            self.fallback = _fallback(func)
        functools.update_wrapper(self, func)
        return self

    def register[**P, T](
        self, condition: Callable[..., bool], *, precedence: int = 0
    ) -> Callable[[Callable[P, T]], Callable[P, T]]:
        def decorator(func: Callable[P, T], /) -> Callable[P, T]:
            self.functions.add(Function(condition, func, precedence))
            return func

        return decorator
