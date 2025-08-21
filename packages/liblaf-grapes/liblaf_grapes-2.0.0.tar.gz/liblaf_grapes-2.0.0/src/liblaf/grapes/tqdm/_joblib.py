import contextlib
import functools
from collections.abc import Callable, Generator, Iterable
from typing import Literal, overload

from rich.progress import Progress as RichProgress
from rich.progress import TaskID

from liblaf.grapes import deps

from ._progress import Progress, len_safe

with deps.optional_imports():
    import joblib


@overload
def parallel[T](
    fn: Callable[..., T],
    *iterables: Iterable,
    description: str = "Working...",
    progress: Progress | Literal[False] | None = None,
    return_as: Literal["list"] = "list",
    total: int | None = None,
) -> list[T]: ...
@overload
def parallel[T](
    fn: Callable[..., T],
    *iterables: Iterable,
    description: str = "Working...",
    progress: Progress | Literal[False] | None = None,
    return_as: Literal["generator", "generator_unordered"],
    total: int | None = None,
) -> Generator[T]: ...
def parallel[T](
    fn: Callable[..., T],
    *iterables: Iterable,
    description: str = "Working...",
    progress: Progress | Literal[False] | None = None,
    return_as: Literal["list", "generator", "generator_unordered"] = "list",
    total: int | None = None,
) -> list[T] | Generator[T]:
    for iterable in iterables:
        if total is not None:
            break
        total = len_safe(iterable)

    parallel = joblib.Parallel(return_as=return_as)

    task_id: TaskID | None = None
    if progress is None:
        progress = Progress()
    progress: Progress | contextlib.nullcontext
    if progress:
        task_id = progress.add_task(description=description, total=total)
    else:
        progress = contextlib.nullcontext()
    parallel.print_progress = functools.partial(
        print_progress, self=parallel, progress=progress, task_id=task_id
    )

    jobs = map(joblib.delayed(fn), *iterables)
    match return_as:
        case "list":
            return as_list(parallel, jobs, progress=progress)
        case "generator" | "generator_unordered":
            return as_generator(parallel, jobs, progress=progress)


def print_progress(
    self: joblib.Parallel,
    progress: RichProgress | contextlib.nullcontext,
    task_id: TaskID | None,
) -> None:
    if isinstance(progress, RichProgress):
        assert task_id is not None
        progress.update(task_id, total=self.n_tasks, completed=self.n_completed_tasks)


def as_list(
    parallel: joblib.Parallel,
    jobs: Iterable,
    *,
    progress: contextlib.AbstractContextManager,
) -> list:
    with progress, parallel:
        return parallel(jobs)  # pyright: ignore[reportReturnType]


def as_generator(
    parallel: joblib.Parallel,
    jobs: Iterable,
    *,
    progress: contextlib.AbstractContextManager,
) -> Generator:
    with progress, parallel:
        yield from parallel(jobs)
