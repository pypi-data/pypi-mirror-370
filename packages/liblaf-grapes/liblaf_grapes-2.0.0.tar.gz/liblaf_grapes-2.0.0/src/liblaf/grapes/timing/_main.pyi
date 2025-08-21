from collections.abc import Callable, Iterable, Sequence
from typing import overload

from ._clock import ClockName
from ._timer import Timer
from ._timings import Callback

@overload
def timer(
    name: str | None = ...,
    *,
    clocks: Sequence[ClockName] = ...,
    cb_start: Callback | None = ...,
    cb_stop: Callback | None = ...,
    cb_finish: Callback | None = ...,
) -> Timer: ...
@overload
def timer[C: Callable](
    callable: C,
    /,
    *,
    name: str | None = ...,
    clocks: Sequence[ClockName] = ...,
    cb_start: Callback | None = ...,
    cb_stop: Callback | None = ...,
    cb_finish: Callback | None = ...,
) -> C: ...
@overload
def timer[I: Iterable](
    iterable: I,
    /,
    name: str | None = ...,
    clocks: Sequence[ClockName] = ...,
    cb_start: Callback | None = ...,
    cb_stop: Callback | None = ...,
    cb_finish: Callback | None = ...,
) -> I: ...
