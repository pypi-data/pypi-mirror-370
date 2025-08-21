from typing import Any

from liblaf.grapes import functools as _ft

from ._base import BaseTimer


def get_timer(wrapper: Any) -> BaseTimer:
    return _ft.unbind_getattr(wrapper, "_self_timer")
