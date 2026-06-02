from __future__ import annotations

from kernel.profile.model import Profile
from kernel.profile.validate import validate_profile


class InitiationError(ValueError):
    pass


def initiate(profile: Profile | None) -> str:
    if profile is None:
        raise InitiationError("resolve_context requires a profile; only profile initiates inquiry")
    validate_profile(profile)
    return profile.core_question

