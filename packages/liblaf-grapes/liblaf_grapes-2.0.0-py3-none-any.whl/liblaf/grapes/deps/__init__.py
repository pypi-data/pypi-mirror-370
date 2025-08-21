"""This module provides utility functions for handling optional imports and checking module availability."""

import lazy_loader as lazy

__getattr__, __dir__, __all__ = lazy.attach_stub(__name__, __file__)
