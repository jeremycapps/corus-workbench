from __future__ import annotations

from pathlib import Path
from typing import Any

from kernel.moment_runtime.model import (
    Artifact,
    Commit,
    Contract,
    Moment,
    MomentRuntimeBundle,
    Profile,
    Role,
    Source,
    StateRule,
    Team,
)
from kernel.verify.hash import read_yaml


def load_moment_runtime(root: Path) -> MomentRuntimeBundle:
    root = root.resolve()
    return MomentRuntimeBundle(
        sources=[_source(item) for item in _list_at(read_yaml(root / "sources.yaml"), "sources")],
        profiles=[_profile(item) for item in _list_at(read_yaml(root / "profiles.yaml"), "profiles")],
        roles=[_role(item) for item in _list_at(read_yaml(root / "roles.yaml"), "roles")],
        teams=[_team(item) for item in _list_at(read_yaml(root / "teams.yaml"), "teams")],
        contracts=[_contract(item) for item in _list_at(read_yaml(root / "contracts.yaml"), "contracts")],
        artifacts=[_artifact(item) for item in _list_at(read_yaml(root / "artifacts.yaml"), "artifacts")],
        commits=[_commit(item) for item in _list_at(read_yaml(root / "commits.yaml"), "commits")],
        moments=[_moment(item) for item in _list_at(read_yaml(root / "moments.yaml"), "moments")],
        state_rules=[_state_rule(item) for item in _list_at(read_yaml(root / "state_rules.yaml"), "states")],
    )


def _source(data: dict[str, Any]) -> Source:
    _require_keys(data, {"id", "type", "label", "status"}, "source")
    return Source(id=str(data["id"]), type=str(data["type"]), label=_optional_str(data.get("label")), status=str(data["status"]))


def _profile(data: dict[str, Any]) -> Profile:
    _require_keys(data, {"id", "type"}, "profile", optional={"role", "team", "system"})
    return Profile(
        id=str(data["id"]),
        type=str(data["type"]),
        role=_optional_str(data.get("role")),
        team=_optional_str(data.get("team")),
        system=_optional_str(data.get("system")),
    )


def _role(data: dict[str, Any]) -> Role:
    _require_keys(data, {"id", "label"}, "role")
    return Role(id=str(data["id"]), label=_optional_str(data.get("label")))


def _team(data: dict[str, Any]) -> Team:
    _require_keys(data, {"id", "label", "roles"}, "team")
    return Team(id=str(data["id"]), label=_optional_str(data.get("label")), roles=_str_list(data["roles"], "roles"))


def _contract(data: dict[str, Any]) -> Contract:
    _require_keys(data, {"id", "owner", "focus", "artifact", "state", "derived_from"}, "contract")
    if isinstance(data["artifact"], list):
        raise ValueError(f"contract {data['id']} must reference exactly one artifact")
    return Contract(
        id=str(data["id"]),
        owner=str(data["owner"]),
        focus=str(data["focus"]),
        artifact=str(data["artifact"]),
        state=str(data["state"]),
        derived_from=_str_list(data["derived_from"], "derived_from"),
    )


def _artifact(data: dict[str, Any]) -> Artifact:
    _require_keys(data, {"id", "current_state", "latest_commit"}, "artifact")
    return Artifact(id=str(data["id"]), current_state=str(data["current_state"]), latest_commit=_optional_str(data.get("latest_commit")))


def _commit(data: dict[str, Any]) -> Commit:
    _require_keys(data, {"id", "target", "from_state", "to_state", "author", "timpo", "previous"}, "commit")
    return Commit(
        id=str(data["id"]),
        target=str(data["target"]),
        from_state=str(data["from_state"]),
        to_state=str(data["to_state"]),
        author=str(data["author"]),
        timpo=str(data["timpo"]),
        previous=_optional_str(data.get("previous")),
    )


def _moment(data: dict[str, Any]) -> Moment:
    _require_keys(data, {"id", "timpo", "initiator", "orientation", "subject", "previous"}, "moment")
    return Moment(
        id=str(data["id"]),
        timpo=str(data["timpo"]),
        initiator=str(data["initiator"]),
        orientation=str(data["orientation"]),
        subject=str(data["subject"]),
        previous=_previous(data.get("previous")),
    )


def _state_rule(data: dict[str, Any]) -> StateRule:
    _require_keys(data, {"id", "requires"}, "state")
    return StateRule(id=str(data["id"]), requires=_str_list(data["requires"], "requires"))


def _list_at(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
    values = data.get(key)
    if not isinstance(values, list):
        raise ValueError(f"{key} must be a list")
    if not all(isinstance(item, dict) for item in values):
        raise ValueError(f"{key} entries must be objects")
    return values


def _require_keys(data: dict[str, Any], expected: set[str], label: str, optional: set[str] | None = None) -> None:
    optional = optional or set()
    missing = sorted(expected - set(data))
    extra = sorted(set(data) - expected - optional)
    if missing:
        raise ValueError(f"{label} is missing required keys: {missing}")
    if extra:
        raise ValueError(f"{label} has unsupported keys: {extra}")


def _str_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    return [str(item) for item in value]


def _previous(value: Any) -> str | list[str] | None:
    if value is None:
        return None
    if isinstance(value, list):
        return [str(item) for item in value]
    return str(value)


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)
