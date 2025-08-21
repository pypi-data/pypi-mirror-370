import functools
from collections.abc import Hashable
from typing import overload

import attrs
import cytoolz as toolz
import loguru
from loguru import logger

from liblaf.grapes import error


@overload
def normalize_filter_dict(
    value: "loguru.FilterDict", /
) -> dict[str | None, int | bool]: ...
@overload
def normalize_filter_dict(value: None, /) -> None: ...
def normalize_filter_dict(
    value: "loguru.FilterDict | None", /
) -> dict[str | None, int | bool] | None:
    if value is None:
        return None
    return {k: get_level_no(v) for k, v in value.items()}


@functools.singledispatch
def get_level_no(level: str | int | bool) -> int | bool:  # noqa: FBT001
    raise error.DispatchLookupError(get_level_no, (level,))


@get_level_no.register
def _get_level_no_str(level: str) -> int:
    return logger.level(level).no


@get_level_no.register
def _get_level_no_int(level: int) -> int:
    return level


@get_level_no.register
def _get_level_no_bool(level: bool) -> int | bool:  # noqa: FBT001
    return 0 if level else False


def default_filter_by_level() -> dict[str | None, int | bool]:
    return normalize_filter_dict(
        {
            "": "INFO",
            "__main__": "TRACE",
            "liblaf": "DEBUG",
        }
    )


@attrs.define
class CompositeFilter:
    by_level: dict[str | None, int | bool] | None = attrs.field(
        factory=default_filter_by_level, converter=normalize_filter_dict
    )
    by_name: str | None = attrs.field(default=None)
    none: bool = attrs.field(default=False)
    once: bool = attrs.field(default=True)
    inherit: bool = attrs.field(default=True)
    _cache_record_id: int | None = attrs.field(default=None, init=False)
    _cache_result: bool | None = attrs.field(default=None, init=False)
    _once_history: set[Hashable] = attrs.field(factory=set, init=False)

    def __attrs_post_init__(self) -> None:
        if self.inherit:
            self.by_level = toolz.merge(default_filter_by_level(), self.by_level or {})

    def __call__(self, record: "loguru.Record", /) -> bool:
        # When a filter is used by multiple handlers, it will be called multiple
        # times with the same record. We have to cache the result to make
        # `filter_once` work correctly.
        if id(record) == self._cache_record_id:
            assert self._cache_result is not None
            return self._cache_result
        self._cache_record_id = id(record)
        self._cache_result = (
            self.filter_by_level(record)
            and self.filter_by_name(record)
            and self.filter_none(record)
            and self.filter_once(record)
        )
        return self._cache_result

    def filter_by_level(self, record: "loguru.Record") -> bool:
        if self.by_level is None:
            return True
        name: str | None = record["name"]
        while True:
            level: int | bool | None = self.by_level.get(name, None)
            if level is False:
                return False
            if level is not None:
                return record["level"].no >= level
            if not name:
                return True
            index: int = name.rfind(".")
            name = "" if index < 0 else name[:index]

    def filter_by_name(self, record: "loguru.Record") -> bool:
        if self.by_name is None:
            return True
        name: str | None = record["name"]
        if name is None:
            return False
        return f"{name}.".startswith(self.by_name)

    def filter_none(self, record: "loguru.Record") -> bool:
        if not self.none:
            return True
        return record["name"] is not None

    def filter_once(self, record: "loguru.Record") -> bool:
        if not self.once:
            return True
        if not record["extra"].get("once", False):
            return True
        key: Hashable = self._hash_record(record)
        if key in self._once_history:
            return False
        self._once_history.add(key)
        return True

    def set_level(self, module: str | None, level: str | int | bool | None) -> None:  # noqa: FBT001
        if self.by_level is None:
            self.by_level = {}
        if level is None:
            del self.by_level[module]
            return
        self.by_level[module] = get_level_no(level)

    def _hash_record(self, record: "loguru.Record") -> Hashable:
        return (
            record["function"],
            record["level"].no,
            record["line"],
            record["message"],
            record["name"],
        )
