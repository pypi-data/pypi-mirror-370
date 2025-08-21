from collections.abc import Mapping
from typing import Any

import pydantic

from ._base import BaseModel


class ConfigPretty(BaseModel):
    """.

    References:
        1. <https://docs.kidger.site/wadler_lindig/api/#wadler_lindig.pformat>
    """

    width: int | None = pydantic.Field(default=None)
    indent: int = pydantic.Field(default=2)
    short_arrays: bool = pydantic.Field(default=True)
    hide_defaults: bool = pydantic.Field(default=True)
    show_type_module: bool = pydantic.Field(default=True)
    show_dataclass_module: bool = pydantic.Field(default=False)
    show_function_module: bool = pydantic.Field(default=False)
    respect_pdoc: bool = pydantic.Field(default=True)

    @property
    def kwargs(self) -> Mapping[str, Any]:
        return self.model_dump(mode="python", exclude_unset=True, exclude_none=True)
