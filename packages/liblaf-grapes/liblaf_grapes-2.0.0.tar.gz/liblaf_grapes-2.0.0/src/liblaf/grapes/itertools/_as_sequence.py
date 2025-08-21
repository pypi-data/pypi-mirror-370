from collections.abc import Sequence
from typing import Any

from liblaf.grapes.typed import ClassInfo

from ._as_iterable import as_iterable


def as_sequence(obj: Any, base_type: ClassInfo | None = (str, bytes)) -> Sequence:
    return tuple(as_iterable(obj, base_type))
