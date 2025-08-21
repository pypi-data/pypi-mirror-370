from collections.abc import Sequence
from typing import Unpack

import loguru
from rich.console import Console

from liblaf.grapes.logging.filters import make_filter
from liblaf.grapes.logging.sink import (
    RichSink,
    RichSinkColumn,
    RichTracebackConfig,
    default_columns,
)


def rich_handler(
    columns: Sequence[RichSinkColumn] | None = None,
    console: Console | None = None,
    *,
    enable_link: bool = True,
    traceback: RichTracebackConfig | None = None,
    **kwargs: Unpack["loguru.BasicHandlerConfig"],
) -> "loguru.BasicHandlerConfig":
    if columns is None:
        columns = default_columns(enable_link=enable_link)
    kwargs["sink"] = RichSink(console=console, columns=columns, traceback=traceback)
    kwargs["format"] = ""
    kwargs["filter"] = make_filter(kwargs.get("filter"))
    return kwargs
