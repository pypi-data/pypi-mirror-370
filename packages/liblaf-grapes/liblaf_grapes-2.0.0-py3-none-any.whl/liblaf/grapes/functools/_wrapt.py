from collections.abc import Callable
from typing import Any, Protocol, overload

import wrapt

from liblaf.grapes.sentinel import MISSING


class Decorator(Protocol):
    def __call__[T](self, wrapped: T, /) -> T: ...


class Wrapper(Protocol):
    def __call__(
        self, wrapped: Any, instance: Any, args: tuple, kwargs: dict[str, Any], /
    ) -> Any: ...


@overload
def decorator(
    wrapper: Wrapper,
    enabled: bool | Callable[[], None] | None = None,  # noqa: FBT001
    adapter: Any = None,
    proxy: Callable = ...,
) -> Decorator: ...
@overload
def decorator(
    wrapper: None = None,
    enabled: bool | Callable[[], None] | None = None,  # noqa: FBT001
    adapter: Any = None,
    proxy: Callable = ...,
) -> Callable[[Wrapper], Decorator]: ...
def decorator(*args, **kwargs) -> Any:
    return wrapt.decorator(*args, **kwargs)


def unbind[T](o: T) -> T:
    return getattr(o, "_self_parent", o)


@overload
def unbind_getattr(o: object, name: str, /) -> Any: ...
@overload
def unbind_getattr[T](o: object, name: str, default: T, /) -> Any | T: ...
def unbind_getattr(o: object, name: str, default: Any = MISSING, /) -> Any:
    try:
        return getattr(o, name)
    except AttributeError:
        parent: Any = getattr(o, "_self_parent", MISSING)
        if parent is MISSING:
            # `o` is not a wrapt.BoundFunctionWrapper
            # further inspection is not applicable
            if default is MISSING:
                raise
            return default
        # `o` is a wrapt.BoundFunctionWrapper
        # `parent` is a wrapt.FunctionWrapper
        # further inspection is applicable
        attr: Any = getattr(parent, name, MISSING)
        if attr is not MISSING:
            return attr
        if default is MISSING:
            raise
        return default
