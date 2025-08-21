import abc

import loguru
from rich.console import RenderableType


class RichSinkColumn(abc.ABC):
    @abc.abstractmethod
    def render(self, record: "loguru.Record", /) -> RenderableType: ...
