from pathlib import Path

from rich.style import Style
from rich.text import Text

from liblaf.grapes.typed import PathLike


def rich_location(
    name: str | None,
    function: str | None,
    line: int | None,
    file: PathLike | None = None,
    *,
    enable_link: bool = True,
) -> Text:
    text = Text()
    file: Path | None = Path(file) if file is not None else None
    function = function or "<unknown>"
    line = line or 0
    if enable_link and file is not None and file.exists():
        text.append(
            f"{name}:{function}:{line}", style=Style(link=f"{file.as_uri()}#{line}")
        )
    else:
        text.append(f"{name}:{function}:{line}")
    return text
