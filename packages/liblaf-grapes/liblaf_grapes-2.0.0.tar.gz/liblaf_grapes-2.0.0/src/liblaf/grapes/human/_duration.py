import math
from collections.abc import Callable


def _mm_ss(sec: float) -> str:
    minute: float
    sec: float
    minute, sec = divmod(sec, 60)
    return f"{int(minute):02}:{int(sec):02}"


def _hh_mm_ss(sec: float) -> str:
    hour: float
    sec: float
    hour, sec = divmod(sec, 3600)
    return f"{int(hour):02}:{_mm_ss(sec)}"


def _d_hh_mm_ss(sec: float) -> str:
    day: float
    sec: float
    day, sec = divmod(sec, 86400)
    return f"{int(day)}d,{_hh_mm_ss(sec)}"


DEFAULT_TEMPLATES: list[tuple[float, Callable[[float], str]]] = [
    (1e-9, lambda sec: f"{sec * 1e9:#.2f} ns"),
    (1e-6, lambda sec: f"{sec * 1e9:#.3g} ns"),
    (1e-3, lambda sec: f"{sec * 1e6:#.3g} µs"),
    (1.0, lambda sec: f"{sec * 1e3:#.3g} ms"),
    (60, lambda sec: f"{sec:#.3g} s"),
    (3600, _mm_ss),
    (360000, _hh_mm_ss),
    (math.inf, _d_hh_mm_ss),
]


def human_duration(sec: float) -> str:
    """.

    Examples:
        >>> human_duration(math.nan)
        '?? s'
        >>> human_duration(1e-12)
        '0.00 ns'
        >>> human_duration(1e-11)
        '0.01 ns'
        >>> human_duration(1e-10)
        '0.10 ns'
        >>> human_duration(1e-9)
        '1.00 ns'
        >>> human_duration(1e-8)
        '10.0 ns'
        >>> human_duration(1e-7)
        '100. ns'
        >>> human_duration(1e-6)
        '1.00 µs'
        >>> human_duration(1e-5)
        '10.0 µs'
        >>> human_duration(1e-4)
        '100. µs'
        >>> human_duration(1e-3)
        '1.00 ms'
        >>> human_duration(1e-2)
        '10.0 ms'
        >>> human_duration(1e-1)
        '100. ms'
        >>> human_duration(1.0)
        '1.00 s'
        >>> human_duration(1e1)
        '10.0 s'
        >>> human_duration(1e2)
        '01:40'
        >>> human_duration(1e3)
        '16:40'
        >>> human_duration(1e4)
        '02:46:40'
        >>> human_duration(1e5)
        '27:46:40'
        >>> human_duration(1e6)
        '11d,13:46:40'
    """
    if not math.isfinite(sec):
        return "?? s"
    for threshold, template in DEFAULT_TEMPLATES:
        if sec < threshold:
            return template(sec)
    raise NotImplementedError


def human_duration_with_stdev(mean: float, stdev: float) -> str:
    if not math.isfinite(stdev):
        return human_duration(mean)
    return f"{human_duration(mean)} ± {human_duration(stdev)}"
