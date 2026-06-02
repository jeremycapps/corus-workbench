from __future__ import annotations

from typing import Any

from kernel.audit.admissibility import resolve_claim_admissibility
from kernel.audit.permissions import verify_profile_permissions
from kernel.audit.replay import replay_read_projection
from kernel.audit.target import resolve_audit_target
from kernel.engine.hashing import hash_data
from kernel.ledger.read import read_active_context
from kernel.ledger.store import LedgerStore
from kernel.verify.hash import read_yaml


def audit_target(store: LedgerStore, target: str, projection: dict[str, Any] | None = None) -> dict[str, Any]:
    ledger_check = verify_ledger_chain_check(store)
    read_result = read_active_context(store)
    read_replay_check = replay_read_projection(store, claimed_projection=projection)
    target_resolution = resolve_audit_target(store, target)
    records = target_resolution["records"]
    included_ids = {item["id"] for item in read_result["included"]}
    excluded_by_id = {item["id"]: item for item in read_result["excluded"]}
    target_status = _target_status(target_resolution, included_ids, excluded_by_id)
    checks = {
        "target_resolver": target_resolution["check"],
        "ledger_chain": ledger_check,
        "payload_hashes": verify_payload_hashes(store),
        "admissibility": resolve_claim_admissibility(store, target, read_result),
        "read_replay": read_replay_check,
        "diff_comparison": compare_projection_placeholder(read_replay_check),
        "profile_permissions": verify_profile_permissions(store, target, target_resolution),
    }

    proof = {
        "target": target_resolution["target"],
        "valid": _compute_valid(checks),
        "status": target_status["active_context"],
        "target_status": target_status,
        "checks": checks,
        "ledger_references": records,
        "included": read_result["included"],
        "excluded": read_result["excluded"],
        "replay": {
            "claimed_projection_hash": read_replay_check["claimed_projection_hash"],
            "replayed_projection_hash": read_replay_check["replayed_projection_hash"],
            "matches": read_replay_check["matches"],
            "included_payloads": [item["payload_hash"] for item in read_result["included"]],
            "excluded_payloads": [item["payload_hash"] for item in read_result["excluded"]],
        },
    }
    if target in excluded_by_id:
        proof["reason"] = excluded_by_id[target]["reason"]
    proof["proof_hash"] = hash_data(proof)
    return proof


def _compute_valid(checks: dict[str, dict[str, Any]]) -> bool:
    return all(check["status"] in {"pass", "not_applicable"} for check in checks.values())


def _target_status(
    target_resolution: dict[str, Any],
    included_ids: set[str],
    excluded_by_id: dict[str, dict[str, Any]],
) -> dict[str, str]:
    target = target_resolution["target"]["id"]
    if target in included_ids:
        return {
            "history": "found",
            "active_context": "included",
            "reason": "Target claim exists in ledger history and is included in active READ context.",
        }
    if target in excluded_by_id:
        return {
            "history": "found",
            "active_context": "excluded",
            "reason": excluded_by_id[target]["reason"],
        }
    if target_resolution["target"]["type"] == "object":
        return {
            "history": "unknown",
            "active_context": "unknown",
            "reason": target_resolution["reason"],
        }
    if target_resolution["history"] == "found":
        return {
            "history": "found",
            "active_context": "not_applicable",
            "reason": "Target exists in ledger history but is not a READ candidate claim target.",
        }
    return {
        "history": "not_found",
        "active_context": "unknown",
        "reason": target_resolution["reason"],
    }


def verify_ledger_chain_check(store: LedgerStore) -> dict[str, str]:
    verified = []
    previous_entry_hash = None
    for entry in store.read_entries():
        expected_entry_hash = entry.get("entry_hash")
        actual_entry_hash = hash_data({key: entry[key] for key in entry if key != "entry_hash"})
        prev_hash_matches = entry.get("prev_hash") == previous_entry_hash
        entry_hash_matches = expected_entry_hash == actual_entry_hash
        status = "pass" if prev_hash_matches and entry_hash_matches else "fail"
        evidence = {
            "entry_id": entry.get("id"),
            "timpo": entry.get("timpo"),
            "prev_hash": entry.get("prev_hash"),
            "prev_hash_matches": prev_hash_matches,
            "expected_entry_hash": expected_entry_hash,
            "actual_entry_hash": actual_entry_hash,
            "status": status,
        }
        if not prev_hash_matches:
            evidence["reason"] = "prev_hash does not match previous entry_hash"
        elif not entry_hash_matches:
            evidence["reason"] = "entry_hash does not match recomputed ledger entry hash"
        verified.append(evidence)
        previous_entry_hash = expected_entry_hash

    failed = [item for item in verified if item["status"] != "pass"]
    if failed:
        return {
            "status": "fail",
            "reason": "One or more ledger entries failed entry_hash recomputation or prev_hash continuity.",
            "verified": verified,
        }
    return {
        "status": "pass",
        "reason": "All referenced ledger entries recomputed successfully and prev_hash continuity was intact.",
        "verified": verified,
    }


def verify_payload_hashes(store: LedgerStore) -> dict[str, Any]:
    verified = []
    for entry in store.read_entries():
        payload_ref = str(entry.get("payload_ref"))
        payload_path = store.root / payload_ref
        if not payload_path.exists():
            verified.append(
                {
                    "entry_id": entry.get("id"),
                    "payload_ref": payload_ref,
                    "expected_hash": entry.get("payload_hash"),
                    "actual_hash": None,
                    "status": "fail",
                    "reason": "payload_ref does not resolve",
                }
            )
            continue

        payload = read_yaml(payload_path)
        actual_hash = hash_data(payload)
        expected_hash = entry.get("payload_hash")
        status = "pass" if actual_hash == expected_hash else "fail"
        verified.append(
            {
                "entry_id": entry.get("id"),
                "payload_ref": payload_ref,
                "expected_hash": expected_hash,
                "actual_hash": actual_hash,
                "status": status,
            }
        )

    failed = [item for item in verified if item["status"] != "pass"]
    if failed:
        return {
            "status": "fail",
            "reason": "One or more payloads did not match their recorded payload_hash.",
            "verified": verified,
        }
    return {
        "status": "pass",
        "reason": "All referenced payloads matched their recorded payload_hash.",
        "verified": verified,
    }


def compare_projection_placeholder(read_replay_check: dict[str, Any]) -> dict[str, str]:
    # TODO[AUDIT-006]: Implement diff/comparison for projection/output mismatches.
    if read_replay_check["claimed_projection_hash"] is None:
        return {
            "status": "not_applicable",
            "reason": "No claimed projection was provided, so there is no mismatch to diff.",
        }
    if read_replay_check["matches"]:
        return {
            "status": "not_applicable",
            "reason": "Claimed projection matched replay; detailed diff is not needed.",
        }
    return {
        "status": "not_implemented",
        "reason": "Claimed projection differs from replay, but detailed projection diff is not implemented yet.",
    }
