from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from kernel.engine.hashing import hash_data
from kernel.moment_runtime.loader import load_moment_runtime
from kernel.moment_runtime.model import Artifact, MomentRuntimeBundle, to_dict_list
from kernel.moment_runtime.trace import build_moment_trace
from kernel.moment_runtime.validate import validate_moment_runtime


def resolve_moment_runtime(root: Path) -> dict[str, Any]:
    bundle = load_moment_runtime(root)
    validate_moment_runtime(bundle)
    artifacts = _apply_commits(bundle)
    contracts = _contracts(bundle, artifacts)
    moments = to_dict_list(bundle.moments)
    derived_contexts = _derive_contexts(bundle, contracts, artifacts)
    state = _resolve_state(bundle, artifacts)

    result: dict[str, Any] = {
        "answer": _answer(state),
        "derived_contexts": derived_contexts,
        "contracts": contracts,
        "artifacts": [asdict(artifact) for artifact in artifacts],
        "commits": to_dict_list(bundle.commits),
        "moments": moments,
        "state": state,
        "trace": {"claims": [], "hash": ""},
        "layer_hashes": {
            "sources_hash": hash_data(to_dict_list(bundle.sources)),
            "profiles_hash": hash_data(to_dict_list(bundle.profiles)),
            "roles_hash": hash_data(to_dict_list(bundle.roles)),
            "teams_hash": hash_data(to_dict_list(bundle.teams)),
            "contracts_hash": hash_data(to_dict_list(bundle.contracts)),
            "artifacts_hash": hash_data(to_dict_list(bundle.artifacts)),
            "commits_hash": hash_data(to_dict_list(bundle.commits)),
            "moments_hash": hash_data(moments),
            "state_rules_hash": hash_data(to_dict_list(bundle.state_rules)),
        },
    }
    result["trace"] = build_moment_trace(result)
    result["layer_hashes"]["resolution_hash"] = hash_data(result)
    return result


def _apply_commits(bundle: MomentRuntimeBundle) -> list[Artifact]:
    artifacts = {artifact.id: artifact for artifact in bundle.artifacts}
    latest_by_artifact: dict[str, str] = {}
    for commit in bundle.commits:
        current = artifacts[commit.target]
        artifacts[commit.target] = Artifact(id=current.id, current_state=commit.to_state, latest_commit=commit.id)
        latest_by_artifact[commit.target] = commit.id
    return [artifacts[artifact.id] for artifact in bundle.artifacts]


def _contracts(bundle: MomentRuntimeBundle, artifacts: list[Artifact]) -> list[dict[str, Any]]:
    artifact_states = {artifact.id: artifact.current_state for artifact in artifacts}
    return [
        {
            "id": contract.id,
            "owner": contract.owner,
            "focus": contract.focus,
            "artifact": contract.artifact,
            "state": _contract_state(artifact_states[contract.artifact]),
            "derived_from": contract.derived_from,
        }
        for contract in bundle.contracts
    ]


def _derive_contexts(bundle: MomentRuntimeBundle, contracts: list[dict[str, Any]], artifacts: list[Artifact]) -> list[dict[str, Any]]:
    contexts = []
    contract_ids = [contract["id"] for contract in contracts]
    artifact_state = {artifact.id: artifact.current_state for artifact in artifacts}
    for root in [moment for moment in bundle.moments if moment.orientation.startswith("orchestrate.") and moment.previous is None]:
        context_id = f"context.{root.subject.removeprefix('source.').replace('_', '.')}.account_context"
        contexts.append(
            {
                "id": context_id,
                "orchestrator": root.initiator,
                "subject": root.subject,
                "moments": _reachable_moments(bundle, root.id),
                "contracts": contract_ids,
                "state": {
                    "coordination": "unresolved",
                    "neara_alignment": _state_for_required(
                        ["artifact.value_evidence", "artifact.roi_case", "artifact.technical_evidence", "artifact.integration_path"],
                        artifact_state,
                    ),
                    "customer_adoption": _state_for_required(
                        ["artifact.customer_sponsor_acceptance", "artifact.customer_technical_acceptance"],
                        artifact_state,
                    ),
                },
            }
        )
    return contexts


def _resolve_state(bundle: MomentRuntimeBundle, artifacts: list[Artifact]) -> dict[str, str]:
    artifact_state = {artifact.id: artifact.current_state for artifact in artifacts}
    return {rule.id: _state_for_required(rule.requires, artifact_state) for rule in bundle.state_rules}


def _state_for_required(required: list[str], artifact_state: dict[str, str]) -> str:
    return "ready" if all(artifact_state.get(artifact_id) in {"present", "validated"} for artifact_id in required) else "unresolved"


def _contract_state(artifact_state: str) -> str:
    if artifact_state in {"present", "validated"}:
        return "present"
    if artifact_state == "draft_present":
        return "draft_present"
    return "expected_missing"


def _reachable_moments(bundle: MomentRuntimeBundle, root_id: str) -> list[str]:
    previous_by_moment = {moment.id: _previous_ids(moment.previous) for moment in bundle.moments}
    reachable = []
    for moment in bundle.moments:
        if moment.id == root_id or _continues(moment.id, root_id, previous_by_moment, set()):
            reachable.append(moment.id)
    return reachable


def _continues(moment_id: str, root_id: str, previous_by_moment: dict[str, list[str]], seen: set[str]) -> bool:
    if moment_id in seen:
        return False
    seen.add(moment_id)
    previous = previous_by_moment.get(moment_id, [])
    if root_id in previous:
        return True
    return any(_continues(prev_id, root_id, previous_by_moment, seen) for prev_id in previous)


def _previous_ids(previous: str | list[str] | None) -> list[str]:
    if previous is None:
        return []
    if isinstance(previous, list):
        return previous
    return [previous]


def _answer(state: dict[str, str]) -> str:
    if state.get("state.neara_alignment") == "ready":
        if state.get("state.customer_adoption") == "ready":
            return (
                "RVO enters a Director-orchestrated account context. CVA and FDE contracts are satisfied through "
                "committed artifacts, and customer-side acceptance artifacts are present, so Neara-side alignment "
                "and customer adoption are ready."
            )
        return (
            "RVO enters a Director-orchestrated account context. CVA and FDE contracts are satisfied through "
            "committed artifacts, so Neara-side alignment is ready. Customer adoption remains unresolved until "
            "customer-side acceptance artifacts exist."
        )
    return (
        "RVO enters a Director-orchestrated account context. CVA and FDE contracts become visible inside that "
        "context: CVA is expected to produce value evidence and an ROI case; FDE is expected to produce technical "
        "evidence and an integration path. Those artifacts are still missing, so Neara-side alignment remains "
        "unresolved. Customer adoption also remains unresolved until customer-side acceptance artifacts exist."
    )
