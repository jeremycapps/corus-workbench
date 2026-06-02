from __future__ import annotations

from pathlib import Path
from typing import Any

from kernel.ledger.store import LedgerStore
from kernel.source.files import write_extent_file
from kernel.source.files import write_source_file
from kernel.source.files import write_validation_file
from kernel.source.hash import hash_artifact
from kernel.source.hash import hash_geojson_geometry
from kernel.source.materialize import materialize_extent
from kernel.source.materialize import materialize_source
from kernel.source.materialize import materialize_validation


def add_source(
    name: str,
    ref: str,
    kind: str,
    out: Path,
    admit: bool,
) -> dict[str, Any]:
    if kind != "extent":
        raise ValueError("source add PoC currently supports only --kind extent")
    out.mkdir(parents=True, exist_ok=True)
    (out / "ledger" / "entries").mkdir(parents=True, exist_ok=True)
    (out / "ledger" / "payloads").mkdir(parents=True, exist_ok=True)

    ref_path = Path(ref)
    if not ref_path.is_absolute():
        ref_path = Path.cwd() / ref_path
    artifact_hash = hash_artifact(ref_path)
    geometry_hash = hash_geojson_geometry(ref_path)

    source = write_source_file(out, name, ref, artifact_hash, geometry_hash)
    extent = write_extent_file(out, name)
    objects = [source, extent]
    if admit:
        objects.append(write_validation_file(out, name))

    store = LedgerStore(out)
    written = []
    for data in objects:
        payload = _materialize(data)
        entry = store.write(payload, timpo="0")
        written.append({"name": _object_name(data), "entry_id": entry["id"], "payload_hash": entry["payload_hash"]})

    ledger = store.verify_chain()
    return {
        "command": "source add",
        "name": name,
        "kind": kind,
        "created": [_object_name(data) for data in objects],
        "ledger": ledger,
        "written_payloads": written,
        "artifact_hash": artifact_hash,
        "geometry_hash": geometry_hash,
    }


def _materialize(data: dict[str, Any]) -> dict[str, Any]:
    if str(data.get("name", "")).endswith(".source"):
        return materialize_source(data)
    if str(data.get("name", "")).endswith(".extent"):
        return materialize_extent(data)
    return materialize_validation(data)


def _object_name(data: dict[str, Any]) -> str:
    return str(data.get("name") or f"{str(data['target']).rsplit('.', 1)[0]}.validation")
