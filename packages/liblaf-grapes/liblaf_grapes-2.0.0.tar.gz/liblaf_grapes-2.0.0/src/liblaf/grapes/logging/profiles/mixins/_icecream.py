import functools
from typing import Any

import attrs
from loguru import logger

from liblaf.grapes import pretty


@attrs.define(slots=False)
class MixinIcecream:
    ic_prefix: str = attrs.field(default="")

    def configure_icecream(self, prefix: str | None = None) -> None:
        try:
            from icecream import ic
        except ImportError:
            return

        if prefix is None:
            prefix = self.ic_prefix

        self.ic_prefix = prefix

        ic.configureOutput(
            prefix=prefix,
            argToStringFunction=ic_arg_to_string_function,
            outputFunction=self.ic_output_function,
        )

    def ic_output_function(self, s: str) -> None:
        logger.opt(depth=2).log("ICECREAM", s)


@functools.singledispatch
def ic_arg_to_string_function(obj: Any) -> str:
    return pretty.pformat(obj)
