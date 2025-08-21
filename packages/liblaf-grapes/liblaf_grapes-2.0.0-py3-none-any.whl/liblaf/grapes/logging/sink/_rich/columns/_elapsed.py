import datetime
from typing import override

import loguru
from rich.console import RenderableType
from rich.text import Text

from ._abc import RichSinkColumn


class RichSinkColumnElapsed(RichSinkColumn):
    @override  # impl RichSinkColumn
    def render(self, record: "loguru.Record", /) -> RenderableType:
        elapsed: datetime.timedelta = record["elapsed"]
        hh: int
        mm: int
        ss: int
        mm, ss = divmod(int(elapsed.total_seconds()), 60)
        hh, mm = divmod(mm, 60)
        # TODO: handle longer timedelta
        # ref: <https://docs.pydantic.dev/latest/api/standard_library_types/#datetimetimedelta>
        # format: [[DD]D,]HH:MM:SS[.ffffff]
        # Ex: '1d,01:02:03.000004' or '1D01:02:03.000004' or '01:02:03'
        return Text(
            f"{hh:02d}:{mm:02d}:{ss:02d}.{elapsed.microseconds:06d}", style="log.time"
        )
