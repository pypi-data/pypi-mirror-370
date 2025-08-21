import functools
from typing import Any

import attrs
import cytoolz as toolz
import wadler_lindig as wl

from liblaf.grapes._config import config

from ._console import get_console

UNINITIALIZED = wl.TextDoc("<uninitialized>")


def pdoc_attrs(self: Any, **kwargs) -> wl.AbstractDoc:
    """.

    References:
        1. <https://github.com/patrick-kidger/wadler_lindig/blob/0226340d56f0c18e10cd4d375cf7ea25818359b8/wadler_lindig/_definitions.py#L308-L326>
    """
    kwargs: dict[str, Any] = toolz.merge(config.pretty.kwargs, kwargs)
    cls: type = type(self)
    objs: list[tuple[str, Any]] = []
    for field in attrs.fields(cls):
        field: attrs.Attribute
        if not field.repr:
            continue
        value: Any = getattr(self, field.name, UNINITIALIZED)
        if kwargs["hide_defaults"] and value is field.default:
            continue
        objs.append((field.name, value))
    name_kwargs: dict[str, Any] = toolz.assoc(
        kwargs, "show_type_module", kwargs["show_dataclass_module"]
    )
    return wl.bracketed(
        begin=wl.pdoc(cls, **name_kwargs) + wl.TextDoc("("),
        docs=wl.named_objs(objs, **kwargs),
        sep=wl.comma,
        end=wl.TextDoc(")"),
        indent=kwargs["indent"],
    )


@functools.singledispatch
def pformat(obj: Any, **kwargs) -> str:
    kwargs: dict[str, Any] = toolz.merge(config.pretty.kwargs, kwargs)
    if "width" not in kwargs:
        kwargs["width"] = get_console(stderr=True).width
    if not hasattr(obj, "__pdoc__") and attrs.has(type(obj)):
        return pformat_attrs(obj, **kwargs)
    return wl.pformat(obj, **kwargs)


def pformat_attrs(obj: Any, **kwargs) -> str:
    kwargs: dict[str, Any] = toolz.merge(config.pretty.kwargs, kwargs)
    return wl.pformat(pdoc_attrs(obj, **kwargs), **kwargs)


def wadler_lindig[T](
    cls: type[T],
    *,
    repr: bool | None = None,  # noqa: A002
    pdoc: bool | None = None,
) -> type[T]:
    if repr or (repr is None and "__repr__" not in cls.__dict__):
        cls.__repr__ = _repr
    if (pdoc or (pdoc is None and "__pdoc__" not in cls.__dict__)) and attrs.has(cls):
        cls.__pdoc__ = pdoc_attrs  # pyright: ignore[reportAttributeAccessIssue]
    return cls


def _repr(self: Any) -> str:
    return pformat(self)
