from __future__ import annotations

from kernel.lens.model import Lens
from kernel.profile.model import Profile


class LensResolutionError(ValueError):
    pass


def resolve_lens(profile: Profile, lenses: dict[str, Lens]) -> Lens:
    if profile.lens_ref:
        try:
            return lenses[profile.lens_ref]
        except KeyError as exc:
            raise LensResolutionError(f"profile {profile.id} references missing lens {profile.lens_ref}") from exc

    question = profile.core_question.lower()
    matches = [lens for lens in lenses.values() if lens.core_question_pattern.lower() in question]
    if not matches:
        raise LensResolutionError(f"no lens resolved for profile {profile.id}")
    return sorted(matches, key=lambda item: item.id)[0]

