from collections.abc import Iterable
from typing import Any

from liblaf.grapes.typed import ClassInfo


def as_iterable(obj: Any, base_type: ClassInfo | None = (str, bytes)) -> Iterable:
    # https://more-itertools.readthedocs.io/en/stable/api.html#more_itertools.always_iterable
    if obj is None:
        return ()
    if base_type is not None and isinstance(obj, base_type):
        return (obj,)
    if isinstance(obj, Iterable):
        return obj
    return (obj,)
