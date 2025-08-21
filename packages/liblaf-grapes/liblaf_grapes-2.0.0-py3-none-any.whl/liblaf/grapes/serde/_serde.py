from pathlib import Path
from typing import Any, override

import autoregistry

from liblaf.grapes.typed import PathLike

from ._abc import Serde
from ._json import json
from ._toml import toml
from ._yaml import yaml

SERIALIZERS = autoregistry.Registry()
SERIALIZERS["json"] = json
SERIALIZERS["toml"] = toml
SERIALIZERS["yaml"] = yaml
SERIALIZERS["yml"] = yaml


class Auto(Serde):
    @override
    def load(self, fpath: PathLike, *, ext: str | None = None, **kwargs) -> Any:
        serde: Serde = self.get_serde(fpath, ext=ext)
        return serde.load(fpath, **kwargs)

    @override
    def save(
        self, path: PathLike, obj: Any, *, ext: str | None = None, **kwargs
    ) -> None:
        serde: Serde = self.get_serde(path, ext=ext)
        serde.save(path, obj, **kwargs)

    def get_serde(self, path: PathLike, *, ext: str | None = None) -> Serde:
        if ext is None:
            path: Path = Path(path)
            ext = path.suffix
        ext = ext.lstrip(".")
        return SERIALIZERS[ext]  # pyright: ignore[reportReturnType]


auto = Auto()


def load(path: PathLike, *, ext: str | None = None, **kwargs) -> Any:
    return auto.load(path, ext=ext, **kwargs)


def save(path: PathLike, obj: Any, *, ext: str | None = None, **kwargs) -> None:
    auto.save(path, obj, ext=ext, **kwargs)
