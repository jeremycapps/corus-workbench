from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from kernel.audit import audit_target
from kernel.ledger.store import LedgerStore
from kernel.source.hash import hash_geojson_geometry
from kernel.source.materialize import materialize_extent
from kernel.source.materialize import materialize_source
from kernel.source.materialize import materialize_validation
from kernel.verify.hash import read_yaml


ROOT = Path(__file__).resolve().parents[1]
GEOJSON = ROOT / "tests" / "fixtures" / "eaton_poc" / "sources" / "eaton_perimeter.geojson"


def test_source_add_creates_object_files(tmp_path: Path) -> None:
    run_dir = _source_add(tmp_path)

    source = read_yaml(run_dir / "eaton_perimeter.source")
    extent = read_yaml(run_dir / "eaton_perimeter.extent")
    validation = read_yaml(run_dir / "eaton_perimeter.validation")

    assert source["from"] == "user"
    assert source["act"] == "add"
    assert source["name"] == "eaton_perimeter.source"
    assert source["data"]["ref"] == str(GEOJSON)
    assert source["data"]["artifact_hash"]
    assert source["data"]["geometry_hash"]

    assert extent == {
        "from": "ingest",
        "act": "interpret",
        "source": "eaton_perimeter.source",
        "name": "eaton_perimeter.extent",
        "data": {},
    }

    assert validation["from"] == "user"
    assert validation["act"] == "validate"
    assert validation["target"] == "eaton_perimeter.extent"
    assert validation["data"]["admissible"] is True


def test_source_file_materializes_to_source_payload(tmp_path: Path) -> None:
    run_dir = _source_add(tmp_path)
    payload = materialize_source(read_yaml(run_dir / "eaton_perimeter.source"))

    assert payload["act"] == "add"
    assert payload["type"] == "source"
    assert payload["to"] == "eaton_perimeter.source"
    assert payload["inputs"] == []
    assert payload["data"]["ref"]
    assert payload["data"]["artifact_hash"]
    assert payload["data"]["geometry_hash"]


def test_extent_file_materializes_to_extent_payload(tmp_path: Path) -> None:
    run_dir = _source_add(tmp_path)
    payload = materialize_extent(read_yaml(run_dir / "eaton_perimeter.extent"))

    assert payload == {
        "from": "ingest",
        "act": "interpret",
        "type": "extent",
        "to": "eaton_perimeter.extent",
        "inputs": ["eaton_perimeter.source"],
        "data": {},
    }


def test_validation_file_materializes_to_extent_validation_payload(tmp_path: Path) -> None:
    run_dir = _source_add(tmp_path)
    payload = materialize_validation(read_yaml(run_dir / "eaton_perimeter.validation"))

    assert payload["from"] == "user"
    assert payload["act"] == "validate"
    assert payload["type"] == "extent"
    assert payload["to"] == "eaton_perimeter.extent"
    assert payload["inputs"] == ["eaton_perimeter.extent"]
    assert payload["data"]["admissible"] is True


def test_source_add_writes_valid_ledger(tmp_path: Path) -> None:
    run_dir = _source_add(tmp_path)
    store = LedgerStore(run_dir)

    assert store.verify_chain()["valid"] is True
    assert len(store.read_entries()) == 3


def test_geometry_hash_is_stable_for_equivalent_geojson(tmp_path: Path) -> None:
    a = tmp_path / "a.geojson"
    b = tmp_path / "b.geojson"
    geometry = {
        "type": "Polygon",
        "coordinates": [
            [
                [-118.123, 34.191],
                [-118.12, 34.191],
                [-118.12, 34.194],
                [-118.123, 34.194],
                [-118.123, 34.191],
            ]
        ],
    }
    a.write_text(json.dumps({"type": "Feature", "properties": {"a": 1}, "geometry": geometry}, indent=2), encoding="utf-8")
    b.write_text(json.dumps({"geometry": geometry, "properties": {"b": 2}, "type": "Feature"}, separators=(",", ":")), encoding="utf-8")

    assert hash_geojson_geometry(a) == hash_geojson_geometry(b)


def test_source_extent_target_resolves_for_poc(tmp_path: Path) -> None:
    run_dir = _source_add(tmp_path)
    proof = audit_target(LedgerStore(run_dir), "eaton_perimeter.extent")

    assert proof["checks"]["target_resolver"]["status"] == "pass"
    assert proof["target"]["type"] == "extent"
    assert any(ref["payload_act"] == "interpret" for ref in proof["ledger_references"])


def _source_add(tmp_path: Path) -> Path:
    run_dir = tmp_path / "eaton_poc"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "corus",
            "source",
            "add",
            "--name",
            "eaton_perimeter",
            "--ref",
            str(GEOJSON),
            "--kind",
            "extent",
            "--out",
            str(run_dir),
            "--admit",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return run_dir
