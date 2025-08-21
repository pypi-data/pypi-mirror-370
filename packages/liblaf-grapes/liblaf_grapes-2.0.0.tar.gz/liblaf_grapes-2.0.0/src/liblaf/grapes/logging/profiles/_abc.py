import abc

import attrs
import autoregistry


@attrs.define
class Profile(abc.ABC, autoregistry.Registry, prefix="Profile"):
    @abc.abstractmethod
    def init(self) -> None: ...
