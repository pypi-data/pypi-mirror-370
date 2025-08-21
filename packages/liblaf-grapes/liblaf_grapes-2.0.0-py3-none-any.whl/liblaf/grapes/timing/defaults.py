from collections.abc import Iterable, Sequence

from ._clock import ClockName
from ._statistics import StatisticName

DEFAULT_CLOCKS: Sequence[ClockName] = ("perf",)


LOG_RECORD_DEFAULT_INDEX: int = -1
LOG_RECORD_DEFAULT_LEVEL: int | str = "DEBUG"
LOG_RECORD_DEFAULT_THRESHOLD_SEC: float | None = 0.02


LOG_SUMMARY_DEFAULT_LEVEL: int | str = "INFO"
LOG_SUMMARY_DEFAULT_STATISTICS: Iterable[StatisticName] = (
    "total",
    "mean+stdev",
    "median",
)
