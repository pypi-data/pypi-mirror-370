from typing import override

import attrs
import loguru
from rich.console import RenderableType
from rich.text import Text

from liblaf.grapes import pretty

from ._abc import RichSinkColumn


@attrs.define
class RichSinkColumnLocation(RichSinkColumn):
    enable_link: bool = attrs.field(default=True)

    @override  # impl RichSinkColumn
    def render(self, record: "loguru.Record", /) -> RenderableType:
        location: Text = pretty.rich_location(
            name=record["name"],
            function=record["function"],
            line=record["line"],
            file=record["file"].path,
            enable_link=self.enable_link,
        )
        location.style = "log.path"
        return location
