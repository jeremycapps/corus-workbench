from __future__ import annotations

from typing import Any

from kernel.engine.hashing import hash_data
from kernel.ledger.read import read_active_context
from kernel.ledger.store import LedgerStore


def projection_fingerprint(read_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "included": read_result["included"],
        "declared_contracts": read_result["declared_contracts"],
    }


def replay_read_projection(
    store: LedgerStore,
    claimed_projection: dict[str, Any] | None = None,
) -> dict[str, Any]:
    replayed_read = read_active_context(store)
    replayed_projection = projection_fingerprint(replayed_read)
    replayed_projection_hash = hash_data(replayed_projection)

    if claimed_projection is None:
        return {
            "status": "not_applicable",
            "reason": "No claimed projection was provided; audit emitted a replay projection but did not compare against a claim.",
            "claimed_projection_hash": None,
            "replayed_projection_hash": replayed_projection_hash,
            "matches": None,
            "replayed_projection": replayed_projection,
        }

    claimed_projection_hash = hash_data(claimed_projection)
    matches = claimed_projection_hash == replayed_projection_hash
    return {
        "status": "pass" if matches else "fail",
        "reason": (
            "Claimed projection hash matches independently replayed projection hash."
            if matches
            else "Claimed projection hash does not match independently replayed projection hash."
        ),
        "claimed_projection_hash": claimed_projection_hash,
        "replayed_projection_hash": replayed_projection_hash,
        "matches": matches,
        "replayed_projection": replayed_projection,
    }
