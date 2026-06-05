from __future__ import annotations

from dataclasses import dataclass
from typing import Any


# Account-context v1 keeps these roles narrow:
# Team = hub of roles.
# Role = hub of relations.
# Surface = accountable context boundary.
# Relation = role contribution into the surface.
# Artifact = durable output of a relation or surface.
# Profile/initiator = person-position that asks the core question.
# Events = how context becomes consequence over time.
# State transitions = proof that alignment changed.
# Ledger/trace = proof.


@dataclass(frozen=True)
class SourceRef:
    id: str
    type: str
    label: str | None
    claims: list[str]


@dataclass(frozen=True)
class Context:
    id: str
    label: str | None
    source_basis: list[str]
    meaning: str


@dataclass(frozen=True)
class Team:
    id: str
    label: str | None
    contains: list[str]


@dataclass(frozen=True)
class Role:
    id: str
    label: str | None
    team: str
    source_basis: list[str]


@dataclass(frozen=True)
class Surface:
    id: str
    label: str | None
    owner: str | None
    context: str
    boundary: str


@dataclass(frozen=True)
class Relation:
    id: str
    from_role: str
    to_surface: str
    semantic: str
    source_basis: list[str]
    produces: list[str]


@dataclass(frozen=True)
class Artifact:
    id: str
    label: str | None
    produced_by: str
    used_by: list[str]


@dataclass(frozen=True)
class AccountProfile:
    id: str
    label: str | None
    role: str
    core_question: str
    lens: dict[str, Any]


@dataclass(frozen=True)
class AccountContextBundle:
    sources: list[SourceRef]
    context: Context
    team: Team
    roles: list[Role]
    surface: Surface
    relations: list[Relation]
    artifacts: list[Artifact]
    profile: AccountProfile


@dataclass(frozen=True)
class AccountContextResolution:
    context: dict[str, object]
    team: dict[str, object]
    surface: dict[str, object]
    relations: list[dict[str, object]]
    artifacts: list[dict[str, object]]
    initiator: dict[str, object]
    answer: str
    trace: dict[str, object]
    events: list[dict[str, object]]
    state_transitions: list[dict[str, object]]
    layer_hashes: dict[str, str]
