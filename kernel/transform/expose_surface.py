from __future__ import annotations

from typing import Any


def expose_surface(clearance_context: dict[str, Any], surface: dict[str, Any]) -> dict[str, Any]:
    return {
        "context": "surface_context",
        "surface": surface["surface"],
        "props": {
            key: clearance_context["policy_diff"].get(key)
            for key in surface.get("props", {})
            if key in clearance_context["policy_diff"]
        },
        "relationships": surface.get("relationships", {}),
    }
