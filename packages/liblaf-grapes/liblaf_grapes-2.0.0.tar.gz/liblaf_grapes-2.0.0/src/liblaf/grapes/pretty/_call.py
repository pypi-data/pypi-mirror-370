import inspect
from collections.abc import Callable, Mapping, Sequence
from typing import Any

import attrs
import wadler_lindig as wl

from ._func import _get_name
from ._wadler_lindig import pformat


@attrs.define
class PrettyCall:
    func: Callable
    args: Sequence[Any] = attrs.field(default=())
    kwargs: Mapping[str, Any] = attrs.field(default={})

    def __repr__(self) -> str:
        return pformat(self)

    def __pdoc__(self, **kwargs) -> wl.AbstractDoc:
        func_name: str = _get_name(self.func)
        docs: list[wl.AbstractDoc] = [wl.pdoc(arg, **kwargs) for arg in self.args]
        docs += wl.named_objs(self.kwargs.items(), **kwargs)
        return wl.bracketed(
            begin=wl.TextDoc(func_name) + wl.TextDoc("("),
            docs=docs,
            sep=wl.comma,
            end=wl.TextDoc(")"),
            indent=kwargs["indent"],
        )


def pretty_call(
    func: Callable,
    args: Sequence[Any] = (),
    kwargs: Mapping[str, Any] = {},
    **wl_kwargs,
) -> str:
    func = inspect.unwrap(func)
    args, kwargs = _bind_safe(func, args, kwargs)
    return pformat(PrettyCall(func, args, kwargs), **wl_kwargs)


def _bind_safe(
    func: Callable, /, args: Sequence[Any], kwargs: Mapping[str, Any]
) -> tuple[Sequence[Any], Mapping[str, Any]]:
    try:
        signature: inspect.Signature = inspect.signature(func)
        arguments: inspect.BoundArguments = signature.bind(*args, **kwargs)
    except TypeError:
        return args, kwargs
    else:
        return arguments.args, arguments.kwargs
