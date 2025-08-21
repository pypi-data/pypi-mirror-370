from collections.abc import Sequence

import attrs
import loguru

from liblaf.grapes.logging import handlers

from ._default import ProfileDefault
from ._default import default_handlers as _default_handlers


def default_handlers() -> Sequence["loguru.HandlerConfig"]:
    return [*_default_handlers(), handlers.file_handler()]


@attrs.define
class ProfileCherries(ProfileDefault):
    # overrides mixins.LoggingProfileMixinLoguru
    handlers: Sequence["loguru.HandlerConfig"] | None = attrs.field(
        factory=default_handlers
    )
