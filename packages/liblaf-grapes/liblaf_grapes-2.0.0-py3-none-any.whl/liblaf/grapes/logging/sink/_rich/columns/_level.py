from typing import override

import loguru
from rich.console import RenderableType
from rich.text import Text

from ._abc import RichSinkColumn


class RichSinkColumnLevel(RichSinkColumn):
    # TODO: custom width

    @override  # impl RichSinkColumn
    def render(self, record: "loguru.Record", /) -> RenderableType:
        level: str = record["level"].name
        return Text(f"{level:<8}", style=f"logging.level.{level.lower()}")
