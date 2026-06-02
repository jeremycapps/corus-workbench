from __future__ import annotations

from typing import Any

from kernel.ledger.store import LedgerStore


def resolve_claim_admissibility(store: LedgerStore, target: str, read_result: dict[str, Any]) -> dict[str, Any]:
    if not target.startswith("claim."):
        return {
            "status": "not_applicable",
            "reason": "Claim-level admissibility applies only to claim targets.",
            "target": target,
        }

    included_ids = {item["id"] for item in read_result["included"]}
    excluded_by_id = {item["id"]: item for item in read_result["excluded"]}
    active_context = "included" if target in included_ids else "excluded" if target in excluded_by_id else "unknown"

    interpretation = {"status": "not_found"}
    validation = {"status": "not_found", "admissible": False, "reason": "unvalidated"}
    for entry in store.read_entries():
        payload = store.read_payload(entry)
        if payload.get("type") != "candidate_claim" or payload.get("to") != target:
            continue
        if payload.get("act") == "interpret":
            interpretation = _payload_reference(entry)
        elif payload.get("act") == "validate":
            validation = {
                **_payload_reference(entry),
                "admissible": bool(payload.get("data", {}).get("admissible")),
                "reason": "admissible true" if payload.get("data", {}).get("admissible") else "admissible false",
            }

    if interpretation["status"] == "not_found":
        return {
            "status": "not_found",
            "reason": "No interpret payload was found for target claim.",
            "target": target,
            "history": "not_found",
            "active_context": active_context,
            "interpretation": interpretation,
            "validation": validation,
        }

    if validation["status"] == "not_found":
        expected_active_context = "excluded"
        reason = "Target has an interpretation payload but no validation payload; READ excludes it as unvalidated."
    elif validation["admissible"]:
        expected_active_context = "included"
        reason = "Latest validation marks target admissible true and READ includes the claim."
    else:
        expected_active_context = "excluded"
        reason = "Latest validation marks target admissible false and READ excludes the claim."

    status = "pass" if active_context == expected_active_context else "fail"
    if status == "fail":
        reason = f"Latest validation expected READ active_context={expected_active_context}, but READ returned active_context={active_context}."

    return {
        "status": status,
        "reason": reason,
        "target": target,
        "history": "found",
        "active_context": active_context,
        "interpretation": interpretation,
        "validation": validation,
    }


def _payload_reference(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "found",
        "entry_id": entry["id"],
        "entry_hash": entry["entry_hash"],
        "payload_hash": entry["payload_hash"],
        "payload_ref": entry["payload_ref"],
    }
