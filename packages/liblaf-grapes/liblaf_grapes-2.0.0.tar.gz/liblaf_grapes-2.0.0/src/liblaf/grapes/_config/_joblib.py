from pathlib import Path

import platformdirs
import pydantic

from ._base import BaseModel


def _default_joblib_memory_location() -> Path:
    return platformdirs.user_cache_path(appname="joblib")


class ConfigJoblibMemory(BaseModel):
    bytes_limit: int | str | None = pydantic.Field(default="4G")
    location: Path = pydantic.Field(default_factory=_default_joblib_memory_location)


class ConfigJoblib(BaseModel):
    memory: ConfigJoblibMemory = pydantic.Field(default_factory=ConfigJoblibMemory)
