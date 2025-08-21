import inspect
import itertools
import logging
import types
from collections.abc import Iterable, Sequence

import attrs
import loguru
import loguru._logger
from loguru import logger


@attrs.define(slots=False)
class MixinLoguru:
    handlers: Sequence["loguru.HandlerConfig"] | None = attrs.field(default=None)
    levels: Sequence["loguru.LevelConfig"] | None = attrs.field(default=None)
    level: int | str | None = attrs.field(default=None)

    def add_level(
        self,
        name: str,
        no: int | None = None,
        color: str | None = None,
        icon: str | None = None,
    ) -> "loguru.Level":
        if name in self._core.levels and no == logger.level(name).no:
            no = None  # skip update severity no
        return logger.level(name=name, no=no, color=color, icon=icon)

    def configure_loguru(
        self,
        handlers: Sequence["loguru.HandlerConfig"] | None = None,
        levels: Sequence["loguru.LevelConfig"] | None = None,
        level: int | str | None = None,
    ) -> None:
        if handlers is None:
            handlers = self.handlers or []
        if levels is None:
            levels = self.levels or []
        if level is None:
            level = self.level

        if level is not None:
            for handler_config in handlers:
                if "level" not in handler_config:
                    handler_config["level"] = level

        self.handlers = handlers
        self.levels = levels
        self.level = level

        for level_config in levels:
            self.add_level(**level_config)
        logger.configure(handlers=handlers)
        self.setup_loguru_logging_intercept()

    def setup_loguru_logging_intercept(self, modules: Iterable[str] = ()) -> None:
        """Logs to loguru from Python logging module.

        References:
            1. [Entirely compatible with standard logging](https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging)
            2. [loguru-logging-intercept/loguru_logging_intercept.py at f358b75ef4162ea903bf7a3298c22b1be83110da · MatthewScholefield/loguru-logging-intercept](https://github.com/MatthewScholefield/loguru-logging-intercept/blob/f358b75ef4162ea903bf7a3298c22b1be83110da/loguru_logging_intercept.py)
        """
        for lvl in self._core.levels.values():
            logging.addLevelName(lvl.no, lvl.name)

        level: int = logging.NOTSET
        if isinstance(self.level, int):
            level = self.level
        elif isinstance(self.level, str):
            level = logger.level(self.level).no

        logging.basicConfig(handlers=[InterceptHandler()], level=level)
        for logger_name in itertools.chain(("",), modules):
            mod_logger: logging.Logger = logging.getLogger(logger_name)
            mod_logger.handlers = [InterceptHandler()]
            mod_logger.propagate = False

    @property
    def _core(self) -> loguru._logger.Core:
        return logger._core  # pyright: ignore[reportAttributeAccessIssue] # noqa: SLF001


class InterceptHandler(logging.Handler):
    """Logs to loguru from Python logging module.

    References:
        1. [Entirely compatible with standard logging](https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging)
        2. [loguru-logging-intercept/loguru_logging_intercept.py at f358b75ef4162ea903bf7a3298c22b1be83110da · MatthewScholefield/loguru-logging-intercept](https://github.com/MatthewScholefield/loguru-logging-intercept/blob/f358b75ef4162ea903bf7a3298c22b1be83110da/loguru_logging_intercept.py)
    """

    def emit(self, record: logging.LogRecord) -> None:
        if logger is None:  # logger has been cleaned up
            return

        # Get corresponding Loguru level if it exists.
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame: types.FrameType | None
        depth: int
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )
