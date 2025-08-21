import os
import time
from typing import Literal

import autoregistry

# ruff: noqa: PYI051
# for code-completion
type ClockName = (
    Literal[
        "monotonic",
        "perf",
        "process",
        "thread",
        "time",
        "children-system",
        "children-user",
        "elapsed",
        "system",
        "user",
    ]
    | str
)

CLOCK_REGISTRY = autoregistry.Registry()

CLOCK_REGISTRY["monotonic"] = time.monotonic
CLOCK_REGISTRY["perf"] = time.perf_counter
CLOCK_REGISTRY["process"] = time.process_time
CLOCK_REGISTRY["thread"] = time.thread_time
CLOCK_REGISTRY["time"] = time.time


CLOCK_REGISTRY["children-system"] = lambda: os.times().children_system
CLOCK_REGISTRY["children-user"] = lambda: os.times().children_user
CLOCK_REGISTRY["elapsed"] = lambda: os.times().elapsed
CLOCK_REGISTRY["system"] = lambda: os.times().system
CLOCK_REGISTRY["user"] = lambda: os.times().user


def clock(name: ClockName = "perf") -> float:
    return CLOCK_REGISTRY[name]()
