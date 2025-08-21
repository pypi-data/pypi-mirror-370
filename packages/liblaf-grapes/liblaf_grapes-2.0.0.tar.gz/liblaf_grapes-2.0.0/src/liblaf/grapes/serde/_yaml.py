from collections.abc import Buffer
from typing import Any, override

import msgspec

from ._abc import Serde


class YAML(Serde):
    @override  # impl Serde
    def decode(self, buf: Buffer | str, **kwargs) -> Any:
        return msgspec.yaml.decode(buf, **kwargs)

    @override  # impl Serde
    def encode(self, obj: Any, **kwargs) -> bytes:
        return msgspec.yaml.encode(obj, **kwargs)


yaml = YAML()
