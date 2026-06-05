from __future__ import annotations

from pathlib import Path
from typing import Any, TypeVar

from kernel.account_context.model import (
    AccountContextBundle,
    AccountProfile,
    Artifact,
    Context,
    Relation,
    Role,
    SourceRef,
    Surface,
    Team,
)
from kernel.verify.hash import read_yaml

T = TypeVar("T")


def load_account_context(root: Path) -> AccountContextBundle:
    root = root.resolve()
    sources_data = read_yaml(root / "neara_account.sources")
    context_data = read_yaml(root / "neara_account.context")
    team_data = read_yaml(root / "neara_account.team")
    roles_data = read_yaml(root / "neara_account.roles")
    surface_data = read_yaml(root / "neara_account.surface")
    relations_data = read_yaml(root / "neara_account.relations")
    artifacts_data = read_yaml(root / "neara_account.artifacts")
    profile_data = read_yaml(root / "neara_account.profile")

    return AccountContextBundle(
        sources=[_source_ref(item) for item in _list_at(sources_data, "sources")],
        context=_context(context_data),
        team=_team(team_data),
        roles=[_role(item) for item in _list_at(roles_data, "roles")],
        surface=_surface(surface_data),
        relations=[_relation(item) for item in _list_at(relations_data, "relations")],
        artifacts=[_artifact(item) for item in _list_at(artifacts_data, "artifacts")],
        profile=_profile(profile_data),
    )


def _source_ref(data: dict[str, Any]) -> SourceRef:
    _require_keys(data, {"id", "type", "label", "claims"}, "source")
    return SourceRef(id=str(data["id"]), type=str(data["type"]), label=_optional_str(data.get("label")), claims=_str_list(data["claims"], "claims"))


def _context(data: dict[str, Any]) -> Context:
    _require_keys(data, {"id", "label", "source_basis", "meaning"}, "context")
    return Context(
        id=str(data["id"]),
        label=_optional_str(data.get("label")),
        source_basis=_str_list(data["source_basis"], "source_basis"),
        meaning=str(data["meaning"]),
    )


def _team(data: dict[str, Any]) -> Team:
    _require_keys(data, {"id", "label", "contains"}, "team")
    return Team(id=str(data["id"]), label=_optional_str(data.get("label")), contains=_str_list(data["contains"], "contains"))


def _role(data: dict[str, Any]) -> Role:
    _require_keys(data, {"id", "label", "team", "source_basis"}, "role")
    return Role(
        id=str(data["id"]),
        label=_optional_str(data.get("label")),
        team=str(data["team"]),
        source_basis=_str_list(data["source_basis"], "source_basis"),
    )


def _surface(data: dict[str, Any]) -> Surface:
    _require_keys(data, {"id", "label", "context", "boundary"}, "surface", optional={"owner"})
    return Surface(
        id=str(data["id"]),
        label=_optional_str(data.get("label")),
        owner=_optional_str(data.get("owner")),
        context=str(data["context"]),
        boundary=str(data["boundary"]),
    )


def _relation(data: dict[str, Any]) -> Relation:
    _require_keys(data, {"id", "from_role", "to_surface", "semantic", "source_basis", "produces"}, "relation")
    return Relation(
        id=str(data["id"]),
        from_role=str(data["from_role"]),
        to_surface=str(data["to_surface"]),
        semantic=str(data["semantic"]),
        source_basis=_str_list(data["source_basis"], "source_basis"),
        produces=_str_list(data["produces"], "produces"),
    )


def _artifact(data: dict[str, Any]) -> Artifact:
    _require_keys(data, {"id", "label", "produced_by", "used_by"}, "artifact")
    return Artifact(
        id=str(data["id"]),
        label=_optional_str(data.get("label")),
        produced_by=str(data["produced_by"]),
        used_by=_str_list(data["used_by"], "used_by"),
    )


def _profile(data: dict[str, Any]) -> AccountProfile:
    _require_keys(data, {"id", "label", "role", "core_question", "lens"}, "profile")
    lens = data["lens"]
    if not isinstance(lens, dict):
        raise ValueError("profile lens must be an object")
    return AccountProfile(
        id=str(data["id"]),
        label=_optional_str(data.get("label")),
        role=str(data["role"]),
        core_question=str(data["core_question"]).strip(),
        lens=lens,
    )


def _list_at(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
    values = data.get(key)
    if not isinstance(values, list):
        raise ValueError(f"{key} must be a list")
    for value in values:
        if not isinstance(value, dict):
            raise ValueError(f"{key} entries must be objects")
    return values


def _require_keys(data: dict[str, Any], expected: set[str], label: str, optional: set[str] | None = None) -> None:
    optional = optional or set()
    actual = set(data)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected - optional)
    if missing:
        raise ValueError(f"{label} is missing required keys: {missing}")
    if extra:
        raise ValueError(f"{label} has unsupported keys: {extra}")


def _str_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    return [str(item) for item in value]


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)
