from typing import Unpack

import loguru

from liblaf.grapes._config import config
from liblaf.grapes.logging.filters import make_filter


def file_handler(
    **kwargs: Unpack["loguru.FileHandlerConfig"],
) -> "loguru.FileHandlerConfig":
    if "sink" not in kwargs:
        kwargs["sink"] = config.log_file
    kwargs["filter"] = make_filter(kwargs.get("filter"))
    kwargs.setdefault("mode", "w")
    return kwargs
