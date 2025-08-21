from .profiles import Profile, ProfileName, factory


def init(profile: ProfileName | Profile = "default") -> None:
    if isinstance(profile, str):
        profile = factory(profile)
    profile.init()
