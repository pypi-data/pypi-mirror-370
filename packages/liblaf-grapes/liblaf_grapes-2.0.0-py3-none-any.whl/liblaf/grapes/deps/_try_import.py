import importlib
import types


def try_import(name: str, package: str | None = None) -> types.ModuleType | None:
    try:
        return importlib.import_module(name=name, package=package)
    except ImportError:
        return None
