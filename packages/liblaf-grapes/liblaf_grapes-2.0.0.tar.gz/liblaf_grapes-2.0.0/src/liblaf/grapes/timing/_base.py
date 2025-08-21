import attrs

from liblaf.grapes.logging import depth_tracker
from liblaf.grapes.sentinel import NOP

from . import callback
from ._clock import clock
from ._timings import Callback, Timings


@attrs.define
class BaseTimer(Timings):
    cb_start: Callback | None = attrs.field(default=None)
    cb_stop: Callback | None = attrs.field(default=callback.log_record)
    cb_finish: Callback | None = attrs.field(default=callback.log_summary)

    def __bool__(self) -> bool:
        return True

    @depth_tracker
    def start(self) -> None:
        for clock_name in self.clocks:
            self._start_time[clock_name] = clock(clock_name)
        self._stop_time.clear()
        if self.cb_start is not None and self.cb_start is not NOP:
            self.cb_start(self)

    @depth_tracker
    def stop(self) -> None:
        for clock_name in self.clocks:
            stop_time: float = clock(clock_name)
            self._stop_time[clock_name] = stop_time
            self.timings[clock_name].append(stop_time - self._start_time[clock_name])
        if self.cb_stop is not None and self.cb_stop is not NOP:
            self.cb_stop(self)

    @depth_tracker
    def finish(self) -> None:
        if self.cb_finish is not None and self.cb_finish is not NOP:
            self.cb_finish(self)
