from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from kernel.engine.hashing import hash_data
from kernel.ledger.store import LedgerStore


@dataclass(frozen=True)
class ReadResult:
    data: dict[str, Any]


def read_active_context(store: LedgerStore, projection: dict[str, Any] | None = None) -> dict[str, Any]:
    store.verify_chain()
    entries = store.read_entries()
    payload_records = [{"entry": entry, "payload": store.read_payload(entry)} for entry in entries]

    validations: dict[str, dict[str, Any]] = {}
    interpreted: dict[str, dict[str, Any]] = {}
    contracts: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []
    outputs: list[dict[str, Any]] = []

    for record in payload_records:
        payload = record["payload"]
        if payload["act"] == "interpret" and payload["type"] == "candidate_claim":
            interpreted[payload["to"]] = record
        elif payload["act"] == "validate" and payload["type"] == "candidate_claim":
            validations[payload["to"]] = record
        elif payload["act"] == "declare" and payload["type"] == "contract":
            contracts.append(_record_summary(record))
        elif payload["act"] == "add":
            sources.append(_record_summary(record))
        elif payload["act"] == "generate":
            outputs.append(_record_summary(record))

    included = []
    excluded = []
    for claim_id, record in sorted(interpreted.items()):
        validation = validations.get(claim_id)
        if validation is None:
            excluded.append(_claim_summary(record, "unvalidated", None))
            continue
        admissible = bool(validation["payload"].get("data", {}).get("admissible"))
        if admissible:
            included.append(_claim_summary(record, "admissible true", validation))
        else:
            excluded.append(_claim_summary(record, "admissible false", validation))

    result = {
        "ledger_chain": store.verify_chain(),
        "included": included,
        "excluded": excluded,
        "declared_contracts": contracts,
        "sources": sources,
        "outputs": outputs,
        "projection": projection,
    }
    result["projection_hash"] = hash_data(
        {
            "included": included,
            "declared_contracts": contracts,
        }
    )
    return result


def _record_summary(record: dict[str, Any]) -> dict[str, Any]:
    entry = record["entry"]
    payload = record["payload"]
    return {
        "id": payload["to"],
        "act": payload["act"],
        "type": payload["type"],
        "entry_id": entry["id"],
        "entry_hash": entry["entry_hash"],
        "payload_hash": entry["payload_hash"],
        "data": payload.get("data", {}),
    }


def _claim_summary(
    interpret_record: dict[str, Any],
    reason: str,
    validation_record: dict[str, Any] | None,
) -> dict[str, Any]:
    summary = _record_summary(interpret_record)
    summary["claim"] = interpret_record["payload"].get("data", {}).get("claim")
    summary["reason"] = reason
    summary["validation_entry_id"] = validation_record["entry"]["id"] if validation_record else None
    summary["validation_entry_hash"] = validation_record["entry"]["entry_hash"] if validation_record else None
    summary["validation_payload_hash"] = validation_record["entry"]["payload_hash"] if validation_record else None
    return summary
