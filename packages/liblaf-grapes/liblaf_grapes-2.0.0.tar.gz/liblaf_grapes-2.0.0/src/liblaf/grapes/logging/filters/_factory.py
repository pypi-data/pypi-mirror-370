import functools
import types
from collections.abc import Mapping

import loguru

from ._composite import CompositeFilter
from .typed import FilterLike


@functools.singledispatch
def make_filter(f: FilterLike, /) -> FilterLike:
    return f


@make_filter.register(types.NoneType)
def _make_filter_none(_: None, /) -> "loguru.FilterFunction":
    return CompositeFilter()


@make_filter.register(Mapping)
def _make_filter_mapping(by_level: "loguru.FilterDict", /) -> "loguru.FilterFunction":
    return CompositeFilter(by_level=by_level)
