from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from kernel.account_context.loader import load_account_context
from kernel.account_context.trace import build_account_context_trace
from kernel.account_context.validate import validate_account_context
from kernel.engine.hashing import hash_data


def resolve_account_context(root: Path) -> dict[str, Any]:
    bundle = load_account_context(root)
    validate_account_context(bundle)
    trace = build_account_context_trace(bundle)

    layer_hashes = {
        "sources_hash": hash_data([asdict(item) for item in bundle.sources]),
        "context_hash": hash_data(asdict(bundle.context)),
        "team_hash": hash_data(asdict(bundle.team)),
        "roles_hash": hash_data([asdict(item) for item in bundle.roles]),
        "surface_hash": hash_data(asdict(bundle.surface)),
        "relations_hash": hash_data([asdict(item) for item in bundle.relations]),
        "artifacts_hash": hash_data([asdict(item) for item in bundle.artifacts]),
    }

    result: dict[str, Any] = {
        "context": {"id": bundle.context.id, "source_basis": bundle.context.source_basis},
        "team": {"id": bundle.team.id, "roles": bundle.team.contains},
        "surface": {"id": bundle.surface.id, "owner": bundle.surface.owner, "boundary": bundle.surface.boundary},
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
        "answer": (
            "RVO account context is adoption-ready when CVA value evidence and FDE technical evidence "
            "resolve into Director-owned delivery alignment."
        ),
        "trace": trace,
        "layer_hashes": layer_hashes,
    }
    result["layer_hashes"]["resolution_hash"] = hash_data(result)
    return result
