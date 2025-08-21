from typing import Any

import attrs


@attrs.define
class MatchError(ValueError):
    value: Any
    cls: str | type = "match"

    def __str__(self) -> str:
        cls: str = self.cls if isinstance(self.cls, str) else self.cls.__qualname__
        return f"{self.value!r} is not a valid {cls}"
