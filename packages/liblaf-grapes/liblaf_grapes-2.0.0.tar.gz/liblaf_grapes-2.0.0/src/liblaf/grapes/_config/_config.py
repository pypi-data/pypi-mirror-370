from pathlib import Path

import pydantic
import pydantic_settings

from ._base import BaseConfig
from ._joblib import ConfigJoblib
from ._log_level import LogLevel
from ._paths import paths
from ._pretty import ConfigPretty


class Config(BaseConfig):
    model_config = pydantic_settings.SettingsConfigDict(env_prefix="LIBLAF_GRAPES_")

    joblib: ConfigJoblib = pydantic.Field(default_factory=ConfigJoblib)
    log_file: Path = pydantic.Field(default=paths.log_file)
    log_level: LogLevel = pydantic.Field(default=LogLevel.INFO)
    pretty: ConfigPretty = pydantic.Field(default_factory=ConfigPretty)


config = Config()
