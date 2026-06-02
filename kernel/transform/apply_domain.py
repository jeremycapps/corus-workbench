from __future__ import annotations

from typing import Any


def apply_domain(model_output: dict[str, Any], domain: dict[str, Any], timpos: dict[str, Any] | None = None) -> dict[str, Any]:
    data = model_output["data"]
    return {
        "context": "clearance_context",
        "domain": domain["domain"],
        "timpos": {
            "ref": timpos.get("_path") if timpos else None,
            "count": len(timpos.get("records", [])) if timpos else 0,
        },
        "policy_diff": {
            "from_policy_version": data["policy_before"],
            "to_policy_version": data["policy_after"],
            "added_watch_items": data["added_watch_items"],
            "removed_items": data["removed_items"],
            "escalated_items": data["escalated_items"],
            "because": data["because"],
        },
        "domain_outputs": domain.get("outputs", []),
    }
