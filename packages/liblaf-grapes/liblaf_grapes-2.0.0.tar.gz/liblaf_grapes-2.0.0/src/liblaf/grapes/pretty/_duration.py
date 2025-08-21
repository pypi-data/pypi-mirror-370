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
    (1e-9, lambda sec: f"{sec * 1e12:#.3g} ps"),
    (1e-6, lambda sec: f"{sec * 1e9:#.3g} ns"),
    (1e-3, lambda sec: f"{sec * 1e6:#.3g} µs"),
    (1.0, lambda sec: f"{sec * 1e3:#.3g} ms"),
    (60, lambda sec: f"{sec:#.3g} s"),
    (3600, _mm_ss),
    (360000, _hh_mm_ss),
    (math.inf, _d_hh_mm_ss),
]


def pretty_duration(sec: float) -> str:
    for threshold, template in DEFAULT_TEMPLATES:
        if sec < threshold:
            return template(sec)
    raise ValueError(sec)
