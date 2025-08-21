"""This module provides functions for serialization and deserialization of various data formats, including JSON, TOML, YAML, and Pydantic models. It also includes registries for mapping file extensions to their respective serialization and deserialization functions."""

import lazy_loader as lazy

__getattr__, __dir__, __all__ = lazy.attach_stub(__name__, __file__)
