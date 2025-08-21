from typing import Literal

from ._abc import Profile

# make sure profiles are registered
from ._cherries import ProfileCherries  # noqa: F401
from ._default import ProfileDefault

# for code-completion
type ProfileName = Literal["default", "cherries"] | str  # noqa: PYI051
type ProfileLike = ProfileName | Profile | type[Profile]


def factory(profile: ProfileLike | None = None, /, *args, **kwargs) -> Profile:
    if profile is None:
        return ProfileDefault(*args, **kwargs)
    if isinstance(profile, Profile):
        return profile
    if isinstance(profile, str):
        return Profile[profile](*args, **kwargs)
    return profile(*args, **kwargs)
