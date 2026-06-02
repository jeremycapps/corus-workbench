from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from kernel.verify.hash import sha256_file


def hash_artifact(path: Path) -> str:
    return sha256_file(path)


def hash_geojson_geometry(path: Path) -> str | None:
    if path.suffix.lower() not in {".geojson", ".json"}:
        return None
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    geometry = _geometry_content(data)
    serialized = json.dumps(geometry, sort_keys=True, separators=(",", ":"))
    return sha256(serialized.encode("utf-8")).hexdigest()


def _geometry_content(data: dict[str, Any]) -> Any:
    kind = data.get("type")
    if kind == "FeatureCollection":
        return [feature.get("geometry") for feature in data.get("features", [])]
    if kind == "Feature":
        return data.get("geometry")
    return data
