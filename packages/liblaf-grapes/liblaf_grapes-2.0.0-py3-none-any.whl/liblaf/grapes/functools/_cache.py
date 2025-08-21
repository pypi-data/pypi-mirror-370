import datetime
import functools
from collections.abc import Callable
from typing import Any, Protocol, TypedDict, overload

import joblib

from liblaf.grapes._config import config

from ._wrapt import decorator


class ReduceSizeKwargs(TypedDict, total=False):
    bytes_limit: int | str | None
    items_limit: int | None
    age_limit: datetime.timedelta | None


class MemorizedFunc[**P, T](Protocol):
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T: ...


@overload
def cache[**P, T](
    func: Callable[P, T],
    /,
    *,
    memory: joblib.Memory | None = None,
    reduce_size: ReduceSizeKwargs | None = None,
    **kwargs: Any,
) -> MemorizedFunc[P, T]: ...
@overload
def cache[**P, T](
    *,
    memory: joblib.Memory | None = None,
    reduce_size: ReduceSizeKwargs | None = None,
    **kwargs: Any,
) -> Callable[[Callable[P, T]], MemorizedFunc[P, T]]: ...
def cache(
    func: Callable | None = None,
    /,
    *,
    memory: joblib.Memory | None = None,
    reduce_size: ReduceSizeKwargs | None = None,
    **kwargs: Any,
) -> Any:
    if func is None:
        return functools.partial(
            cache, memory=memory, reduce_size=reduce_size, **kwargs
        )
    if memory is None:
        memory = joblib.Memory(config.joblib.memory.location)
    if reduce_size is None:
        reduce_size = {"bytes_limit": config.joblib.memory.bytes_limit}
    func: MemorizedFunc = memory.cache(func, **kwargs)  # pyright: ignore[reportAssignmentType]

    @decorator
    def wrapper(
        wrapped: Callable, _instance: Any, args: tuple, kwargs: dict[str, Any]
    ) -> Any:
        ret: Any = wrapped(*args, **kwargs)
        memory.reduce_size(**reduce_size)
        return ret

    proxy: MemorizedFunc = wrapper(func)
    proxy._self_memory = memory  # pyright: ignore[reportAttributeAccessIssue] # noqa: SLF001
    return proxy
