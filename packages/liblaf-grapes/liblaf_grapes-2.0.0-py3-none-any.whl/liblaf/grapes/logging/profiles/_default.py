from collections.abc import Sequence
from typing import override

import attrs
import loguru

from liblaf.grapes.logging import handlers

from . import mixins
from ._abc import Profile


def default_handlers() -> Sequence["loguru.HandlerConfig"]:
    return [handlers.rich_handler()]


def default_levels() -> Sequence["loguru.LevelConfig"]:
    return [{"name": "ICECREAM", "no": 15, "color": "<magenta><bold>", "icon": "🍦"}]


@attrs.define
class ProfileDefault(
    mixins.MixinLoguru,
    mixins.MixinStdlib,
    mixins.MixinIcecream,
    mixins.MixinExceptHook,
    mixins.MixinUnraisableHook,
    Profile,
):
    # overrides mixins.LoggingProfileMixinLoguru
    handlers: Sequence["loguru.HandlerConfig"] | None = attrs.field(
        factory=default_handlers
    )
    levels: Sequence["loguru.LevelConfig"] | None = attrs.field(factory=default_levels)
    level: int | str | None = attrs.field(default=None)

    @override
    def init(self) -> None:
        self.configure_loguru()
        self.clear_stdlib_handlers()
        self.configure_icecream()
        self.configure_excepthook()
        self.configure_unraisablehook()
