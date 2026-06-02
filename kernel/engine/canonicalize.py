from __future__ import annotations

import json
from typing import Any


def canonicalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: canonicalize(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        items = [canonicalize(item) for item in value]
        if all(isinstance(item, dict) and "id" in item for item in items):
            return sorted(items, key=lambda item: str(item["id"]))
        if all(not isinstance(item, (dict, list)) for item in items):
            return sorted(items, key=lambda item: str(item))
        return items
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(canonicalize(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
