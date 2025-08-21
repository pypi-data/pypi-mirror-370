from collections.abc import Buffer
from typing import Any, override

import msgspec

from ._abc import Serde


class TOML(Serde):
    @override  # impl Serde
    def decode(self, buf: Buffer | str, **kwargs) -> Any:
        return msgspec.toml.decode(buf, **kwargs)

    @override  # impl Serde
    def encode(self, obj: Any, **kwargs) -> bytes:
        return msgspec.toml.encode(obj, **kwargs)


toml = TOML()
