from typing import override

import attrs
import loguru
from rich.console import RenderableType
from rich.highlighter import Highlighter, ReprHighlighter
from rich.text import Text

from ._abc import RichSinkColumn


@attrs.define
class RichSinkColumnMessage(RichSinkColumn):
    highlighter: Highlighter = attrs.field(factory=ReprHighlighter)

    @override  # impl RichSinkColumn
    def render(self, record: "loguru.Record") -> RenderableType:
        if (rich := record["extra"].get("rich")) is not None:
            return rich
        message: RenderableType = record["message"].strip()
        if "\x1b" in message:
            return Text.from_ansi(message)
        if record["extra"].get("markup", True):
            message = Text.from_markup(message)
        if highlighter := record["extra"].get("highlighter", self.highlighter):
            message = highlighter(message)
        return message
