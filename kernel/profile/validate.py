from __future__ import annotations

from kernel.profile.model import RELATION_TYPES, Profile


class ProfileValidationError(ValueError):
    pass


def validate_profile(profile: Profile) -> None:
    if not profile.id:
        raise ProfileValidationError("profile must have an id")
    if not profile.subject:
        raise ProfileValidationError(f"profile {profile.id} must have a subject")
    if not profile.core_question:
        raise ProfileValidationError(f"profile {profile.id} must have a core question")
    if profile.relation_type not in RELATION_TYPES:
        raise ProfileValidationError(f"profile {profile.id} has invalid relation type {profile.relation_type}")
    if not profile.action_authority:
        raise ProfileValidationError(f"profile {profile.id} must define action authority")
    if not (profile.lens_ref or profile.lens_generation_rule):
        raise ProfileValidationError(f"profile {profile.id} must define lens_ref or lens_generation_rule")
