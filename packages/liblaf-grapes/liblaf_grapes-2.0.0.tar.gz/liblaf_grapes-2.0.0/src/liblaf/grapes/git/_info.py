from typing import Protocol

from liblaf.grapes import deps
from liblaf.grapes.typed import PathLike

with deps.optional_imports(extra="git"):
    import git
    import giturlparse


class GitInfo(Protocol):
    """...

    References:
        1. [nephila/giturlparse: Parse & rewrite git urls (supports GitHub, Bitbucket, Assembla ...)](https://github.com/nephila/giturlparse#exposed-attributes)
    """

    platform: str
    """platform codename"""
    host: str
    """server hostname"""
    resource: str
    """same as `host`"""
    port: str
    """URL port (only if explicitly defined in URL)"""
    protocol: str
    """URL protocol (git, ssh, http/https)"""
    protocols: list[str]
    """list of protocols explicitly defined in URL"""
    user: str
    """repository user"""
    owner: str
    """repository owner (user or organization)"""
    repo: str
    """repository name"""
    name: str
    """same as `repo`"""
    groups: list[str]
    """list of groups - gitlab only"""
    path: str
    """path to file or directory (includes the branch name) - gitlab / github only"""
    path_raw: str
    """raw path starting from the repo name (might include platform keyword) - gitlab / github only"""
    branch: str
    """branch name (when parseable) - gitlab / github only"""
    username: str
    """username from `<username>:<access_token>@<url>` gitlab / github urls"""
    access_token: str
    """access token from `<username>:<access_token>@<url>` gitlab / github urls"""


def info(
    path: PathLike | None = None, *, search_parent_directories: bool = True
) -> GitInfo:
    repo = git.Repo(path=path, search_parent_directories=search_parent_directories)
    url: str = repo.remote().url
    return giturlparse.parse(url)  # pyright: ignore[reportReturnType]
