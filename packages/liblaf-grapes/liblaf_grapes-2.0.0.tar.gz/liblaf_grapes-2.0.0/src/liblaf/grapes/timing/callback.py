import functools
from collections.abc import Iterable
from typing import Any, overload

from liblaf.grapes.logging import depth_tracker

from ._statistics import StatisticName
from ._timings import Callback, Timings
from .defaults import (
    LOG_RECORD_DEFAULT_INDEX,
    LOG_RECORD_DEFAULT_LEVEL,
    LOG_RECORD_DEFAULT_THRESHOLD_SEC,
    LOG_SUMMARY_DEFAULT_LEVEL,
    LOG_SUMMARY_DEFAULT_STATISTICS,
)


@overload
def log_record(
    timer: Timings,
    /,
    *,
    index: int = LOG_RECORD_DEFAULT_INDEX,
    level: int | str = LOG_RECORD_DEFAULT_LEVEL,
    threshold_sec: float | None = LOG_RECORD_DEFAULT_THRESHOLD_SEC,
) -> Any: ...
@overload
def log_record(
    *,
    index: int = LOG_RECORD_DEFAULT_INDEX,
    level: int | str = LOG_RECORD_DEFAULT_LEVEL,
    threshold_sec: float | None = LOG_RECORD_DEFAULT_THRESHOLD_SEC,
) -> Callback: ...
@depth_tracker
def log_record(timer: Timings | None = None, /, **kwargs) -> Any:
    if timer is None:
        return functools.partial(log_record, **kwargs)
    return timer.log_record(**kwargs)


@overload
def log_summary(
    timer: Timings,
    /,
    *,
    level: int | str = LOG_SUMMARY_DEFAULT_LEVEL,
    stats: Iterable[StatisticName] = LOG_SUMMARY_DEFAULT_STATISTICS,
) -> None: ...
@overload
def log_summary(
    *,
    level: int | str = LOG_SUMMARY_DEFAULT_LEVEL,
    stats: Iterable[StatisticName] = LOG_SUMMARY_DEFAULT_STATISTICS,
) -> Callback: ...
@depth_tracker
def log_summary(timer: Timings | None = None, /, **kwargs) -> Any:
    if timer is None:
        return functools.partial(log_summary, **kwargs)
    return timer.log_summary(**kwargs)
