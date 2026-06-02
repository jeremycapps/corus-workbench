from __future__ import annotations

from typing import Any

from kernel.ledger.store import LedgerStore


OBJECT_PREFIXES = ("domain.", "surface.", "edge.", "profile.", "value.")
OBJECT_SUFFIXES = (".source", ".extent", ".validation", ".nodes", ".rules", ".context")


def resolve_audit_target(store: LedgerStore, target: str) -> dict[str, Any]:
    descriptor = _target_descriptor(store, target)
    if descriptor["type"] == "object":
        return {
            "status": "not_implemented",
            "target": descriptor,
            "history": "unknown",
            "records": [],
            "reason": "Object-level payload path resolution is not implemented yet. TODO[AUDIT-007B].",
            "check": {
                "status": "not_implemented",
                "reason": "Object-level payload path resolution is not implemented yet. TODO[AUDIT-007B].",
            },
        }

    records = _records_for_descriptor(store, target, descriptor)
    status = "pass" if records else "not_found"
    reason = (
        "Target resolved to ledger payload records."
        if records
        else "No ledger payload or ledger entry resolved for target."
    )
    return {
        "status": status,
        "target": descriptor,
        "history": "found" if records else "not_found",
        "records": records,
        "reason": reason,
        "check": {
            "status": status,
            "reason": reason,
            "target_type": descriptor["type"],
            "record_count": len(records),
        },
    }


def _target_descriptor(store: LedgerStore, target: str) -> dict[str, str]:
    if target.startswith("claim."):
        return {"type": "claim", "id": target}
    if target.startswith("output."):
        return {"type": "output", "id": target}
    if target.startswith("ledger."):
        return {"type": "ledger_entry", "id": target}
    for entry in store.read_entries():
        if entry.get("entry_hash") == target:
            return {"type": "ledger_entry", "id": target}
        if entry.get("payload_hash") == target:
            return {"type": "payload", "id": target}
    if target.startswith(OBJECT_PREFIXES):
        return {"type": "object", "id": target}
    if target.endswith(OBJECT_SUFFIXES):
        return {"type": target.rsplit(".", 1)[1], "id": target}
    return {"type": "unknown", "id": target}


def _records_for_descriptor(store: LedgerStore, target: str, descriptor: dict[str, str]) -> list[dict[str, Any]]:
    records = []
    for entry in store.read_entries():
        payload = store.read_payload(entry)
        match_reasons = _match_reasons(entry, payload, target, descriptor["type"])
        for match_reason in match_reasons:
            records.append(_record(entry, payload, match_reason))
    return records


def _match_reasons(
    entry: dict[str, Any],
    payload: dict[str, Any],
    target: str,
    target_type: str,
) -> list[str]:
    if target_type == "claim":
        reasons = []
        if payload.get("to") == target:
            reasons.append("payload.to")
        if target in payload.get("inputs", []):
            reasons.append("payload.inputs")
        return reasons
    if target_type == "output":
        reasons = []
        if payload.get("act") == "generate" and payload.get("type") == "output" and payload.get("to") == target:
            reasons.append("payload.to")
        if target in payload.get("inputs", []):
            reasons.append("payload.inputs")
        return reasons
    if target_type == "ledger_entry" and target in {entry.get("id"), entry.get("entry_hash")}:
        return ["entry.id" if entry.get("id") == target else "entry.entry_hash"]
    if target_type == "payload" and entry.get("payload_hash") == target:
        return ["entry.payload_hash"]
    if target_type in {"source", "extent", "validation", "nodes", "rules", "context", "unknown"}:
        reasons = []
        if payload.get("to") == target:
            reasons.append("payload.to")
        if target in payload.get("inputs", []):
            reasons.append("payload.inputs")
        return reasons
    return []


def _record(entry: dict[str, Any], payload: dict[str, Any], match_reason: str) -> dict[str, Any]:
    missing_required = sorted({"from", "act", "type", "to"} - set(payload))
    return {
        "entry_id": entry["id"],
        "entry_hash": entry["entry_hash"],
        "payload_hash": entry["payload_hash"],
        "payload_ref": entry["payload_ref"],
        "payload_act": payload.get("act"),
        "payload_type": payload.get("type"),
        "payload_to": payload.get("to"),
        "match_reason": match_reason,
        "schema_status": "missing_required_fields" if missing_required else "ok",
        "schema_warnings": [f"missing field {field}" for field in missing_required],
    }
