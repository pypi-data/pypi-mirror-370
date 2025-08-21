import os
import types
from collections.abc import Iterable

import attrs
from rich.traceback import LOCALS_MAX_LENGTH, LOCALS_MAX_STRING, Traceback

from liblaf.grapes import deps


def default_suppress() -> Iterable[str | types.ModuleType]:
    return suppress_converter(
        (deps.try_import("liblaf.cherries"), deps.try_import("pydantic")),
    )


def suppress_converter(
    value: str
    | os.PathLike
    | types.ModuleType
    | Iterable[str | os.PathLike | types.ModuleType | None]
    | None,
) -> Iterable[str | types.ModuleType]:
    if value is None:
        return ()
    if not isinstance(value, Iterable) or isinstance(
        value, (str, os.PathLike, types.ModuleType)
    ):
        value = (value,)
    return [
        val for item in value if (val := _suppress_converter_single(item)) is not None
    ]


def _suppress_converter_single(
    value: str | os.PathLike | types.ModuleType | None,
) -> str | types.ModuleType | None:
    if value is None:
        return None
    if isinstance(value, types.ModuleType):
        return value
    if isinstance(value, str):
        module: types.ModuleType | None = deps.try_import(value)
        if module is not None:
            return module
    return str(value)


@attrs.define
class RichTracebackConfig:
    width: int | None = attrs.field(default=None)
    code_width: int | None = attrs.field(default=None)
    extra_lines: int = attrs.field(default=3)
    theme: str | None = attrs.field(default=None)
    word_wrap: bool = attrs.field(default=False)
    show_locals: bool = attrs.field(default=True)
    locals_max_length: int = attrs.field(default=LOCALS_MAX_LENGTH)
    locals_max_string: int = attrs.field(default=LOCALS_MAX_STRING)
    locals_hide_dunder: bool = attrs.field(default=True)
    locals_hide_sunder: bool = attrs.field(default=False)
    indent_guides: bool = attrs.field(default=True)
    suppress: Iterable[str | types.ModuleType] = attrs.field(
        converter=suppress_converter, factory=default_suppress
    )
    max_frames: int = attrs.field(default=100)

    def from_exception(
        self,
        exc_type: type[BaseException],
        exc_value: BaseException,
        traceback: types.TracebackType | None,
        /,
    ) -> Traceback:
        return Traceback.from_exception(
            exc_type,
            exc_value,
            traceback,
            width=self.width,
            code_width=self.code_width,
            extra_lines=self.extra_lines,
            theme=self.theme,
            word_wrap=self.word_wrap,
            show_locals=self.show_locals,
            locals_max_length=self.locals_max_length,
            locals_max_string=self.locals_max_string,
            locals_hide_dunder=self.locals_hide_dunder,
            locals_hide_sunder=self.locals_hide_sunder,
            indent_guides=self.indent_guides,
            suppress=self.suppress,
            max_frames=self.max_frames,
        )
