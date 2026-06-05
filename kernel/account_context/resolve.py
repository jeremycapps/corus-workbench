from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from kernel.account_context.model import AccountContextBundle
from kernel.account_context.loader import load_account_context
from kernel.account_context.trace import build_account_context_trace
from kernel.engine.hashing import hash_data


def resolve_account_context(root: Path) -> dict[str, Any]:
    bundle = load_account_context(root)
    unresolved = _unresolved_items(bundle)
    events = _alignment_events(bundle, unresolved)
    state_transitions = _state_transitions(events)
    trace = build_account_context_trace(events)
    alignment_ready = not any(item.startswith("missing.") and not item.startswith("missing.customer_") for item in unresolved)

    layer_hashes = {
        "sources_hash": hash_data([asdict(item) for item in bundle.sources]),
        "context_hash": hash_data(asdict(bundle.context)),
        "team_hash": hash_data(asdict(bundle.team)),
        "roles_hash": hash_data([asdict(item) for item in bundle.roles]),
        "surface_hash": hash_data(asdict(bundle.surface)),
        "relations_hash": hash_data([asdict(item) for item in bundle.relations]),
        "artifacts_hash": hash_data([asdict(item) for item in bundle.artifacts]),
        "profile_hash": hash_data(asdict(bundle.profile)),
    }

    result: dict[str, Any] = {
        "answer": _answer(bundle, alignment_ready),
        "initiator": {
            "profile": bundle.profile.id,
            "role": bundle.profile.role,
            "core_question": bundle.profile.core_question,
            "lens": bundle.profile.lens,
        },
        "context": {"id": bundle.context.id, "source_basis": bundle.context.source_basis},
        "team": {"id": bundle.team.id, "roles": bundle.team.contains},
        "surface": {
            "id": bundle.surface.id,
            "owner": bundle.surface.owner,
            "context": bundle.surface.context,
            "boundary": bundle.surface.boundary,
        },
        "relations": [
            {
                "id": relation.id,
                "from_role": relation.from_role,
                "semantic": relation.semantic,
                "produces": relation.produces,
            }
            for relation in bundle.relations
        ],
        "artifacts": [
            {
                "id": artifact.id,
                "produced_by": artifact.produced_by,
            }
            for artifact in bundle.artifacts
        ],
        "events": events,
        "state_transitions": state_transitions,
        "state": {
            "neara_alignment": "ready" if alignment_ready else "unresolved",
            "customer_adoption": "unresolved",
            "reason": (
                "customer-side acceptance nodes are not represented"
                if alignment_ready
                else "account-context prerequisites are missing; customer-side acceptance nodes are not represented"
            ),
        },
        "unresolved": unresolved,
        "trace": trace,
        "layer_hashes": layer_hashes,
    }
    result["layer_hashes"]["resolution_hash"] = hash_data(result)
    return result


def _alignment_events(bundle: AccountContextBundle, unresolved: list[str]) -> list[dict[str, Any]]:
    value_relation = _relation_with_semantic(bundle, "value_translation")
    technical_relation = _relation_with_semantic(bundle, "technical_implementation")
    director_relation = _relation_with_semantic(bundle, "account_coherence")
    value_artifact = _first_produced(value_relation)
    technical_artifact = _first_produced(technical_relation)
    delivery_artifact = _first_produced(director_relation)

    events = [
        {
            "id": "event.director_initiates_account_context_question",
            "claim": "Director initiates the account-context question.",
            "caused_by": [bundle.profile.id, bundle.profile.role],
            "produces_state": "alignment.question_initiated",
            "lineage": [bundle.profile.id, bundle.profile.role, bundle.surface.id],
        },
        {
            "id": "event.rvo_context_enters_account_team",
            "claim": "RVO context enters the Neara account team.",
            "caused_by": [bundle.context.id, bundle.team.id],
            "produces_state": "alignment.context_available",
            "lineage": [*bundle.context.source_basis, bundle.context.id, bundle.team.id],
        },
    ]
    if value_relation and value_artifact and "missing.artifact.value_evidence" not in unresolved:
        events.append(
            {
                "id": "event.cva_value_evidence_contributed",
                "claim": "CVA contributes value evidence.",
                "caused_by": [value_relation.from_role, value_relation.id],
                "produces_state": "alignment.value_evidence_available",
                "lineage": [value_relation.from_role, value_relation.id, value_artifact],
            }
        )
    if technical_relation and technical_artifact and "missing.artifact.technical_evidence" not in unresolved:
        events.append(
            {
                "id": "event.fde_technical_evidence_contributed",
                "claim": "FDE contributes technical evidence.",
                "caused_by": [technical_relation.from_role, technical_relation.id],
                "produces_state": "alignment.technical_evidence_available",
                "lineage": [technical_relation.from_role, technical_relation.id, technical_artifact],
            }
        )
    if bundle.surface.owner and "missing.surface.owner" not in unresolved:
        events.append(
            {
                "id": "event.director_surface_ownership_established",
                "claim": "Director owns the account surface.",
                "caused_by": [bundle.surface.owner, bundle.surface.id],
                "produces_state": "alignment.account_surface_owned",
                "lineage": [bundle.surface.owner, bundle.surface.id],
            }
        )
    if _alignment_ready(unresolved):
        events.append(
            {
                "id": "event.delivery_alignment_resolved",
                "claim": "Corus resolves delivery alignment.",
                "caused_by": [
                    value_artifact,
                    technical_artifact,
                    director_relation.id,
                ],
                "produces_state": "neara_alignment.ready",
                "lineage": [
                    value_artifact,
                    technical_artifact,
                    bundle.surface.id,
                    director_relation.id,
                    delivery_artifact,
                ],
            }
        )
    return events


def _relation_with_semantic(bundle: AccountContextBundle, semantic: str) -> Any:
    for relation in bundle.relations:
        if relation.semantic == semantic:
            return relation
    return None


def _first_produced(relation: Any) -> str | None:
    if relation and relation.produces:
        return relation.produces[0]
    return None


def _state_transitions(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    current_state = "neara_alignment.unresolved"
    transitions = []
    for index, event in enumerate(events):
        transitions.append(
            {
                "id": f"transition.{index + 1}",
                "from": current_state,
                "event": event["id"],
                "to": event["produces_state"],
                "lineage": event["lineage"],
            }
        )
        current_state = str(event["produces_state"])
    return transitions


def _unresolved_items(bundle: AccountContextBundle) -> list[str]:
    unresolved: list[str] = []
    role_ids = {role.id for role in bundle.roles}
    artifact_ids = {artifact.id for artifact in bundle.artifacts}
    value_relation = _relation_with_semantic(bundle, "value_translation")
    technical_relation = _relation_with_semantic(bundle, "technical_implementation")
    director_relation = _relation_with_semantic(bundle, "account_coherence")

    if not bundle.context:
        unresolved.append("missing.context")
    if not bundle.team:
        unresolved.append("missing.team")
    if bundle.profile.role not in role_ids:
        unresolved.append("missing.profile.role")
    if not bundle.surface.owner or bundle.surface.owner not in role_ids:
        unresolved.append("missing.surface.owner")
    if value_relation is None:
        unresolved.append("missing.relation.cva.value_translation")
    elif "artifact.value_evidence" not in artifact_ids:
        unresolved.append("missing.artifact.value_evidence")
    if technical_relation is None:
        unresolved.append("missing.relation.fde.technical_implementation")
    elif "artifact.technical_evidence" not in artifact_ids:
        unresolved.append("missing.artifact.technical_evidence")
    if director_relation is None:
        unresolved.append("missing.relation.director.account_coherence")
    elif "artifact.delivery_alignment" not in artifact_ids:
        unresolved.append("missing.artifact.delivery_alignment")

    unresolved.extend(
        [
            "missing.customer_sponsor_acceptance",
            "missing.customer_technical_acceptance",
            "missing.customer_user_workflow",
        ]
    )
    return unresolved


def _alignment_ready(unresolved: list[str]) -> bool:
    return not any(item.startswith("missing.") and not item.startswith("missing.customer_") for item in unresolved)


def _answer(bundle: AccountContextBundle, alignment_ready: bool) -> str:
    initiator_label = (bundle.profile.label or bundle.profile.id).replace(" profile", "")
    if alignment_ready:
        return (
            f"{initiator_label} asks whether RVO context can become aligned delivery context for the account team. "
            "Corus resolves Neara-side alignment when CVA value evidence and FDE technical evidence produce "
            "Director-owned delivery alignment; customer adoption remains unresolved until customer-side acceptance "
            "is represented."
        )
    return (
        f"{initiator_label} asks whether RVO context can become aligned delivery context for the account team. "
        "Corus cannot mark Neara-side alignment ready until required account-context contributions and delivery "
        "alignment artifacts are represented; customer adoption remains unresolved until customer-side acceptance "
        "is represented."
    )
