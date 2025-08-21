import inspect
from collections.abc import Callable


def pretty_func(func: Callable, /) -> str:
    func = inspect.unwrap(func)
    func_name: str = _get_name(func)
    return f"{func_name}()"


def _get_name(func: Callable) -> str:
    return (
        getattr(func, "__qualname__", None)
        or getattr(func, "__name__", None)
        or "<unknown>"
    )
