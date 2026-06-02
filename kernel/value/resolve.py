from __future__ import annotations

from typing import Any

from kernel.value.model import ValueSpec


def resolve_value(value: ValueSpec, runtime_context: dict[str, Any]) -> dict[str, Any]:
    return {
        "value_id": value.id,
        "stakeholders": sorted(value.stakeholders),
        "why_relation": value.why_relation,
        "success_criteria": sorted(value.success_criteria),
        "business_consequence": value.business_consequence,
        "risk_opportunity": value.risk_opportunity,
        "narrative": value.narrative,
        "action_trigger": value.action_trigger,
        "action_recommendation": value.action_trigger,
        "context_node_ids": list(runtime_context.get("first_order_context", {}).get("node_ids", [])),
    }

