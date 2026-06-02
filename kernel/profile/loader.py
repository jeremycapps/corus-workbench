from __future__ import annotations

from pathlib import Path

from kernel.profile.model import Profile
from kernel.verify.hash import read_yaml


def load_profile(path: Path) -> Profile:
    data = read_yaml(path)
    return Profile(
        id=str(data.get("id") or data.get("profile", "")),
        subject=str(data.get("subject", "")),
        organization=str(data.get("organization", "")),
        role_context=str(data.get("role_context", "")),
        core_question=str(data.get("core_question") or data.get("primary_question", "")),
        relation_type=str(data.get("relation_type", "")),
        value_responsibility=str(data.get("value_responsibility", "")),
        evidence_threshold=str(data.get("evidence_threshold", "")),
        action_authority=str(data.get("action_authority", "")),
        lens_ref=data.get("lens_ref"),
        lens_generation_rule=data.get("lens_generation_rule"),
    )


def profile_to_data(profile: Profile) -> dict:
    return {
        "id": profile.id,
        "subject": profile.subject,
        "organization": profile.organization,
        "role_context": profile.role_context,
        "core_question": profile.core_question,
        "relation_type": profile.relation_type,
        "value_responsibility": profile.value_responsibility,
        "evidence_threshold": profile.evidence_threshold,
        "action_authority": profile.action_authority,
        "lens_ref": profile.lens_ref,
        "lens_generation_rule": profile.lens_generation_rule,
    }

