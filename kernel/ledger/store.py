from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from kernel.engine.hashing import hash_data
from kernel.verify.hash import read_yaml, write_yaml


LEDGER_FIELDS = {"id", "timpo", "payload_hash", "payload_ref", "prev_hash", "entry_hash"}
PAYLOAD_FIELDS = {"from", "act", "type", "to"}
PAYLOAD_ACTS = {"add", "interpret", "declare", "generate", "validate"}
SEMANTIC_LEDGER_FORBIDDEN = {"from", "act", "type", "to", "profile", "domain", "value"}


class LedgerVerificationError(ValueError):
    pass


class PayloadValidationError(ValueError):
    pass


@dataclass(frozen=True)
class LedgerStore:
    root: Path

    @property
    def ledger_root(self) -> Path:
        return self.root / "ledger"

    @property
    def entries_root(self) -> Path:
        return self.ledger_root / "entries"

    @property
    def payloads_root(self) -> Path:
        return self.ledger_root / "payloads"

    def read_entries(self) -> list[dict[str, Any]]:
        entries = [read_yaml(path) for path in sorted(self.entries_root.glob("ledger.*.yaml"))]
        return sorted(entries, key=lambda item: item["id"])

    def read_payload(self, entry_or_hash: dict[str, Any] | str) -> dict[str, Any]:
        entry = self._entry_for(entry_or_hash)
        payload_path = self.root / str(entry["payload_ref"])
        if not payload_path.exists():
            raise LedgerVerificationError(f"payload_ref does not resolve: {entry['payload_ref']}")
        return read_yaml(payload_path)

    def write(self, payload: dict[str, Any], timpo: str | int) -> dict[str, Any]:
        validate_payload(payload)
        payload_hash = hash_data(payload)
        entries = self.read_entries() if self.entries_root.exists() else []
        next_number = len(entries) + 1
        payload_ref = f"ledger/payloads/payload.{next_number:04d}.yaml"
        payload_path = self.root / payload_ref
        write_yaml(payload_path, payload)

        entry_without_hash = {
            "id": f"ledger.{next_number:04d}",
            "timpo": str(timpo),
            "payload_hash": payload_hash,
            "payload_ref": payload_ref,
            "prev_hash": entries[-1]["entry_hash"] if entries else None,
        }
        entry = {**entry_without_hash, "entry_hash": hash_data(entry_without_hash)}
        write_yaml(self.entries_root / f"{entry['id']}.yaml", entry)
        return entry

    def verify_entry(self, entry: dict[str, Any]) -> dict[str, Any]:
        if set(entry) != LEDGER_FIELDS:
            extra = sorted(set(entry) - LEDGER_FIELDS)
            missing = sorted(LEDGER_FIELDS - set(entry))
            raise LedgerVerificationError(f"invalid ledger fields extra={extra} missing={missing}")
        forbidden = SEMANTIC_LEDGER_FORBIDDEN & set(entry)
        if forbidden:
            raise LedgerVerificationError(f"ledger entry contains semantic fields {sorted(forbidden)}")
        expected_entry_hash = hash_data({key: entry[key] for key in entry if key != "entry_hash"})
        if entry["entry_hash"] != expected_entry_hash:
            raise LedgerVerificationError(f"entry hash mismatch for {entry['id']}")

        payload = self.read_payload(entry)
        validate_payload(payload)
        expected_payload_hash = hash_data(payload)
        if entry["payload_hash"] != expected_payload_hash:
            raise LedgerVerificationError(f"payload hash mismatch for {entry['id']}")
        return {"entry": entry, "payload": payload}

    def verify_chain(self) -> dict[str, Any]:
        entries = self.read_entries()
        previous_hash = None
        verified = []
        for entry in entries:
            if entry["prev_hash"] != previous_hash:
                raise LedgerVerificationError(f"prev_hash mismatch for {entry['id']}")
            self.verify_entry(entry)
            previous_hash = entry["entry_hash"]
            verified.append(entry["id"])
        return {"valid": True, "entry_count": len(entries), "entries": verified}

    def _entry_for(self, entry_or_hash: dict[str, Any] | str) -> dict[str, Any]:
        if isinstance(entry_or_hash, dict):
            return entry_or_hash
        for entry in self.read_entries():
            if entry_or_hash in {entry["id"], entry["entry_hash"], entry["payload_hash"]}:
                return entry
        raise LedgerVerificationError(f"ledger entry not found: {entry_or_hash}")


def validate_payload(payload: dict[str, Any]) -> None:
    missing = PAYLOAD_FIELDS - set(payload)
    if missing:
        raise PayloadValidationError(f"payload missing required fields {sorted(missing)}")
    if payload["act"] not in PAYLOAD_ACTS:
        raise PayloadValidationError(f"unsupported payload act {payload['act']}")
    if "data" not in payload:
        raise PayloadValidationError("payload missing data")
