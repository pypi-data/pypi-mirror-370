import functools
import importlib.util


@functools.lru_cache
def has_module(name: str, package: str | None = None) -> bool:
    """Check if a module can be imported.

    Args:
        name: The name of the module to check.
        package: The package name to use as the anchor point from which to resolve the relative module name. Defaults to `None`.

    Returns:
        `True` if the module can be imported, `False` otherwise.
    """
    return importlib.util.find_spec(name, package) is not None
