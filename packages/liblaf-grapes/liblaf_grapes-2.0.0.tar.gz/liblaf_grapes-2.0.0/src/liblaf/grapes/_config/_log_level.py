import enum
from typing import override


class LogLevel(enum.StrEnum):
    """.

    References:
        1. <https://github.com/Delgan/loguru/blob/master/loguru/_defaults.py>
    """

    @override
    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[str]
    ) -> str:
        return name.upper()

    TRACE = enum.auto()
    DEBUG = enum.auto()
    INFO = enum.auto()
    SUCCESS = enum.auto()
    WARNING = enum.auto()
    ERROR = enum.auto()
    CRITICAL = enum.auto()
