import contextlib
from collections.abc import Generator
from typing import Any

import etils.epy


@contextlib.contextmanager
def optional_imports(
    name: str = "liblaf-grapes", extra: str | None = None
) -> Generator[None, Any, None]:
    """Context manager to handle optional imports gracefully.

    This context manager allows you to attempt to import optional dependencies
    and handle `ImportError` exceptions in a user-friendly manner. If an import
    fails, it provides a helpful message indicating the missing dependency and
    suggests how to install it.

    Args:
        name: The name of the package that contains the optional dependency.
        extra: An optional string specifying the extra requirements to install the missing dependency.

    Raises:
        ImportError: If an optional dependency is missing, an `ImportError` is raised with a helpful message suggesting how to install it.
    """
    try:
        yield
    except ImportError as err:
        suffix: str = f"Missing optional dependency `{err.name}`."
        if extra is not None:
            suffix += (
                f"\nMake sure to install `{name}` using `pip install {name}[{extra}]`."
            )
        etils.epy.reraise(err, suffix=suffix)
