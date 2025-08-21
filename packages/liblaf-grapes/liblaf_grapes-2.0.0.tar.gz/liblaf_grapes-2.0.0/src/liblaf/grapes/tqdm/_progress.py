from collections.abc import Iterable
from typing import Literal, override

from rich.console import Console, RenderableType
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    ProgressColumn,
    SpinnerColumn,
    Task,
    TaskID,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.progress import Progress as RichProgress
from rich.table import Column
from rich.text import Text

from liblaf.grapes import human, pretty, timing
from liblaf.grapes.logging import depth_tracker


class RateColumn(ProgressColumn):
    """RateColumn is a subclass of ProgressColumn that represents the rate of progress for a given task."""

    unit: str = "it"
    """The unit of measurement for the progress bar."""

    def __init__(self, unit: str = "it", table_column: Column | None = None) -> None:
        """.

        Args:
            unit: The unit of measurement for the progress bar.
            table_column: The table column associated with the progress bar.
        """
        super().__init__(table_column)
        self.unit = unit

    def render(self, task: Task) -> RenderableType:
        """Render the progress speed of a given task.

        Args:
            task: The task for which the speed is to be rendered.

        Returns:
            A text object representing the speed of the task.
        """
        if not task.speed:
            return Text(f"?{self.unit}/s", style="progress.data.speed")
        throughput: str = human.human_throughput(task.speed, self.unit)
        return Text(throughput, style="progress.data.speed")


class Progress(RichProgress):
    timer: timing.Timer | Literal[False]

    def __init__(
        self,
        *columns: str | ProgressColumn,
        console: Console | None = None,
        timer: timing.Timer | Literal[False] | None = None,
    ) -> None:
        if console is None:
            console = pretty.get_console(stderr=True)
        if timer is None:
            timer = timing.timer()
        self.timer = timer
        super().__init__(*columns, console=console)

    @override
    @classmethod
    def get_default_columns(cls) -> tuple[str | ProgressColumn, ...]:  # pyright: ignore[reportIncompatibleMethodOverride]
        return (
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            MofNCompleteColumn(),
            "[",
            TimeElapsedColumn(),
            "<",
            TimeRemainingColumn(),
            ",",
            RateColumn(),
            "]",
        )

    @override
    @depth_tracker
    def track[T](
        self,
        sequence: Iterable[T],
        total: float | None = None,
        completed: int = 0,
        task_id: TaskID | None = None,
        description: str = "Working...",
        update_period: float = 0.1,
        *,
        timer: timing.Timer | Literal[False] | None = None,
    ) -> Iterable[T]:
        if total is None:
            total = len_safe(sequence)
        if timer := (timer or self.timer):
            sequence = timer(sequence)
            timing.get_timer(sequence).name = description
        with depth_tracker(depth=2):
            yield from super().track(
                sequence,
                total=total,
                completed=completed,
                task_id=task_id,
                description=description,
                update_period=update_period,
            )


def len_safe(iterable: Iterable) -> int | None:
    try:
        return len(iterable)  # pyright: ignore[reportArgumentType]
    except TypeError:
        return None
