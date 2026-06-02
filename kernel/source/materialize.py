from __future__ import annotations

from typing import Any


def materialize_source(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "from": data["from"],
        "act": "add",
        "type": "source",
        "to": data["name"],
        "inputs": [],
        "data": dict(data["data"]),
    }


def materialize_extent(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "from": data["from"],
        "act": "interpret",
        "type": "extent",
        "to": data["name"],
        "inputs": [data["source"]],
        "data": dict(data.get("data", {})),
    }


def materialize_validation(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "from": data["from"],
        "act": "validate",
        "type": "extent",
        "to": data["target"],
        "inputs": [data["target"]],
        "data": dict(data["data"]),
    }


def materialize_object_file(data: dict[str, Any]) -> dict[str, Any]:
    name = str(data.get("name", ""))
    if name.endswith(".source"):
        return materialize_source(data)
    if name.endswith(".extent"):
        return materialize_extent(data)
    if str(data.get("target", "")).endswith(".extent"):
        return materialize_validation(data)
    raise ValueError(f"unsupported source object file: {name or data.get('target')}")
