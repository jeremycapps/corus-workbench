from __future__ import annotations

from typing import Any


def apply_profile(surface_context: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    return {
        "context": "profiled_context",
        "surface_context": surface_context,
        "profile": profile["profile"],
        "audience": profile.get("audience", {}),
        "information_hierarchy": profile.get("information_hierarchy", {}),
        "actions": profile.get("actions", {}),
    }
