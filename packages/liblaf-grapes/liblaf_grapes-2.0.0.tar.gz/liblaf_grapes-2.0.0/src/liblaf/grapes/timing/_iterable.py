from collections.abc import Generator, Iterable

import wrapt

from liblaf.grapes.logging import depth_tracker

from ._base import BaseTimer


class TimedIterable[T](wrapt.ObjectProxy):
    __wrapped__: Iterable[T]
    _self_timer: BaseTimer

    def __init__(self, wrapped: Iterable[T], timer: BaseTimer) -> None:
        super().__init__(wrapped)
        if timer.name is None:
            timer.name = "Iterable"
        self._self_timer = timer

    def __iter__(self) -> Generator[T]:
        with depth_tracker():
            self._self_timer.start()
            try:
                for item in self.__wrapped__:
                    self._self_timer.start()
                    yield item
                    self._self_timer.stop()
            finally:
                # When the `for` loop is exhausted, it does not re-enter the loop
                # body. Therefore, the `start()` call after the *last* item is
                # redundant. However, since `timer._start_time` is not used anywhere
                # else, we can safely leave it out.
                self._self_timer.finish()
