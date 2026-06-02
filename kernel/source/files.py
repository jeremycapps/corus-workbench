from __future__ import annotations

from pathlib import Path
from typing import Any

from kernel.verify.hash import write_yaml


def write_source_file(run_dir: Path, name: str, ref: str, artifact_hash: str, geometry_hash: str | None) -> dict[str, Any]:
    data = {
        "from": "user",
        "act": "add",
        "name": f"{name}.source",
        "data": {
            "ref": ref,
            "artifact_hash": artifact_hash,
            "geometry_hash": geometry_hash,
        },
    }
    write_yaml(run_dir / f"{name}.source", data)
    return data


def write_extent_file(run_dir: Path, name: str) -> dict[str, Any]:
    data = {
        "from": "ingest",
        "act": "interpret",
        "source": f"{name}.source",
        "name": f"{name}.extent",
        "data": {},
    }
    write_yaml(run_dir / f"{name}.extent", data)
    return data


def write_validation_file(run_dir: Path, name: str) -> dict[str, Any]:
    data = {
        "from": "user",
        "act": "validate",
        "target": f"{name}.extent",
        "data": {
            "admissible": True,
        },
    }
    write_yaml(run_dir / f"{name}.validation", data)
    return data
