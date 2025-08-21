import functools
from typing import IO

import rich
from rich.console import Console
from rich.style import Style
from rich.theme import Theme

from liblaf.grapes import env
from liblaf.grapes.typed import clone_param_spec


def default_theme() -> Theme:
    """.

    References:
        1. <https://github.com/Delgan/loguru/blob/master/loguru/_defaults.py>
    """
    return Theme(
        {
            "logging.level.notset": Style(dim=True),
            "logging.level.trace": Style(color="cyan", bold=True),
            "logging.level.debug": Style(color="blue", bold=True),
            "logging.level.icecream": Style(color="magenta", bold=True),
            "logging.level.info": Style(bold=True),
            "logging.level.success": Style(color="green", bold=True),
            "logging.level.warning": Style(color="yellow", bold=True),
            "logging.level.error": Style(color="red", bold=True),
            "logging.level.critical": Style(color="red", bold=True, reverse=True),
        },
        inherit=True,
    )


@clone_param_spec(Console)
@functools.cache
def get_console(**kwargs) -> Console:
    if kwargs.get("theme") is None:
        kwargs["theme"] = default_theme()
    file: IO[str] | None = kwargs.get("file")
    if file is None and env.in_ci():
        kwargs.setdefault("width", 128)
    if not kwargs.get("stderr", False) and file is None:
        rich.reconfigure(**kwargs)
        return rich.get_console()
    return Console(**kwargs)
