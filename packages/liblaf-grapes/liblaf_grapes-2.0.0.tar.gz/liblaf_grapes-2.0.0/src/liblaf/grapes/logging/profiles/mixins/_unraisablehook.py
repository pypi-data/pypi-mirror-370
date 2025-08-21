import sys

import attrs
from loguru import logger


@attrs.define(slots=False)
class MixinUnraisableHook:
    unraisablehook_level: int | str = attrs.field(default="ERROR")

    def configure_unraisablehook(self, level: int | str | None = None) -> None:
        if level is not None:
            self.unraisablehook_level = level
        sys.unraisablehook = self.unraisablehook

    def unraisablehook(self, args: "sys.UnraisableHookArgs", /) -> None:
        if logger is None:  # logger has been cleaned up
            return
        logger.opt(exception=(args.exc_type, args.exc_value, args.exc_traceback)).log(
            self.unraisablehook_level,
            "{err_msg}: {object!r}",
            err_msg=args.err_msg or "Exception ignored in",
            object=args.object,
        )
