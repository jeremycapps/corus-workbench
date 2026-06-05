from __future__ import annotations

from dataclasses import dataclass


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
    owner: str
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
class AccountContextBundle:
    sources: list[SourceRef]
    context: Context
    team: Team
    roles: list[Role]
    surface: Surface
    relations: list[Relation]
    artifacts: list[Artifact]


@dataclass(frozen=True)
class AccountContextResolution:
    context: dict[str, object]
    team: dict[str, object]
    surface: dict[str, object]
    relations: list[dict[str, object]]
    artifacts: list[dict[str, object]]
    answer: str
    trace: dict[str, object]
    layer_hashes: dict[str, str]
