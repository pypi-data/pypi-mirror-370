from pathlib import Path

from liblaf.grapes import deps
from liblaf.grapes.typed import PathLike

with deps.optional_imports(extra="git"):
    import git
    import git.exc


def root(
    path: PathLike | None = None, *, search_parent_directories: bool = True
) -> Path:
    repo = git.Repo(path=path, search_parent_directories=search_parent_directories)
    return Path(repo.working_dir)


def root_safe(
    path: PathLike | None = None, *, search_parent_directories: bool = True
) -> Path:
    try:
        return root(path=path, search_parent_directories=search_parent_directories)
    except git.exc.InvalidGitRepositoryError:
        return Path()
