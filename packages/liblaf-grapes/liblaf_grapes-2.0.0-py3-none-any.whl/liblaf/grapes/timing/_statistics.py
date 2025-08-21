import math
import statistics
from collections.abc import Sequence

import autoregistry

from liblaf.grapes import human

type StatisticName = str


STATISTICS_REGISTRY = autoregistry.Registry(prefix="_compute_")


STATISTICS_REGISTRY["max"] = max
STATISTICS_REGISTRY["mean"] = statistics.mean
STATISTICS_REGISTRY["median"] = statistics.median
STATISTICS_REGISTRY["min"] = min
STATISTICS_REGISTRY["stdev"] = statistics.stdev
STATISTICS_REGISTRY["total"] = sum


def compute_statistic(series: Sequence[float], stat_name: StatisticName) -> float:
    try:
        return STATISTICS_REGISTRY[stat_name](series)
    except (ValueError, statistics.StatisticsError):
        return math.nan


def pretty_statistic(series: Sequence[float], stat_name: StatisticName) -> str:
    if stat_name == "mean+stdev":
        mean: float = compute_statistic(series, "mean")
        stdev: float = compute_statistic(series, "stdev")
        return human.human_duration_with_stdev(mean, stdev)
    value: float = compute_statistic(series, stat_name)
    return human.human_duration(value)
