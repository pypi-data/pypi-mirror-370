from collections.abc import Buffer
from pathlib import Path
from typing import Any

from liblaf.grapes.typed import PathLike


class Serde:
    def decode(self, buf: Buffer | str, /, **kwargs) -> Any:
        raise NotImplementedError

    def encode(self, obj: Any, /, **kwargs) -> bytes:
        raise NotImplementedError

    def load(self, path: PathLike, /, **kwargs) -> Any:
        path = Path(path)
        return self.decode(path.read_bytes(), **kwargs)

    def save(self, path: PathLike, obj: Any, /, **kwargs) -> None:
        path = Path(path)
        path.write_bytes(self.encode(obj, **kwargs))
