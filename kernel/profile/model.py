from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


RELATION_TYPES = {
    "person_to_thing",
    "person_to_person",
    "person_to_thing_to_person",
}


@dataclass(frozen=True)
class Profile:
    id: str
    subject: str
    organization: str
    role_context: str
    core_question: str
    relation_type: str
    value_responsibility: str
    evidence_threshold: str
    action_authority: str
    lens_ref: str | None = None
    lens_generation_rule: dict[str, Any] | None = None

