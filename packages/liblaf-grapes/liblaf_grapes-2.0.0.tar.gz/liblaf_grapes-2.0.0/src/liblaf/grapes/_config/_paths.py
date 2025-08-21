import functools
import os
import sys
from pathlib import Path

import attrs


@attrs.define
class Paths:
    def data(self, path: str | os.PathLike = "", *, mkdir: bool = False) -> Path:
        path = self.working_dir / "data" / path
        if mkdir:
            path.mkdir(parents=True, exist_ok=True)
        return path

    def fig(self, path: str | os.PathLike = "", *, mkdir: bool = False) -> Path:
        path = self.working_dir / "fig" / path
        if mkdir:
            path.mkdir(parents=True, exist_ok=True)
        return path

    @functools.cached_property
    def entrypoint(self) -> Path:
        return Path(sys.argv[0])

    @functools.cached_property
    def log_file(self) -> Path:
        return self.working_dir / "run.log"

    @functools.cached_property
    def working_dir(self) -> Path:
        working_dir: Path = self.entrypoint.resolve().parent
        while working_dir.parts[-1] in {"src"}:
            working_dir = working_dir.parent
        return working_dir


paths: Paths = Paths()
