import sys
import types
from typing import Any

import attrs
from loguru import logger


@attrs.define(slots=False)
class MixinExceptHook:
    excepthook_level: int | str = attrs.field(default="CRITICAL")
    excepthook_message: Any = attrs.field(default="")

    def configure_excepthook(
        self, level: int | str | None = None, message: Any = None
    ) -> None:
        if level is not None:
            self.excepthook_level = level
        if message is not None:
            self.excepthook_message = message
        sys.excepthook = self.excepthook

    def excepthook(
        self,
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_traceback: types.TracebackType | None,
        /,
    ) -> None:
        logger.opt(exception=(exc_type, exc_value, exc_traceback)).log(
            self.excepthook_level, self.excepthook_message
        )
