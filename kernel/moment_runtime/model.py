from __future__ import annotations

from dataclasses import dataclass
from typing import Any


ALLOWED_PROFILE_TYPES = {"role", "team", "system"}
ALLOWED_ARTIFACT_STATES = {"expected_missing", "draft_present", "present", "validated", "rejected"}
ALLOWED_ORIENTATION_PREFIXES = ("orchestrate.", "contract.", "commit.", "resolve.")
MOMENT_KEYS = {"id", "timpo", "initiator", "orientation", "subject", "previous"}


@dataclass(frozen=True)
class Source:
    id: str
    type: str
    label: str | None
    status: str


@dataclass(frozen=True)
class Profile:
    id: str
    type: str
    role: str | None = None
    team: str | None = None
    system: str | None = None


@dataclass(frozen=True)
class Role:
    id: str
    label: str | None


@dataclass(frozen=True)
class Team:
    id: str
    label: str | None
    roles: list[str]


@dataclass(frozen=True)
class Contract:
    id: str
    owner: str
    focus: str
    artifact: str
    state: str
    derived_from: list[str]


@dataclass(frozen=True)
class Artifact:
    id: str
    current_state: str
    latest_commit: str | None


@dataclass(frozen=True)
class Commit:
    id: str
    target: str
    from_state: str
    to_state: str
    author: str
    timpo: str
    previous: str | None


@dataclass(frozen=True)
class Moment:
    id: str
    timpo: str
    initiator: str
    orientation: str
    subject: str
    previous: str | list[str] | None


@dataclass(frozen=True)
class StateRule:
    id: str
    requires: list[str]


@dataclass(frozen=True)
class MomentRuntimeBundle:
    sources: list[Source]
    profiles: list[Profile]
    roles: list[Role]
    teams: list[Team]
    contracts: list[Contract]
    artifacts: list[Artifact]
    commits: list[Commit]
    moments: list[Moment]
    state_rules: list[StateRule]


def to_dict_list(items: list[Any]) -> list[dict[str, Any]]:
    return [item.__dict__ for item in items]
