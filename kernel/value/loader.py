from __future__ import annotations

from pathlib import Path

from kernel.value.model import ValueSpec
from kernel.verify.hash import read_yaml


def load_value(path: Path) -> ValueSpec:
    data = read_yaml(path)
    return ValueSpec(
        id=str(data.get("id") or data.get("value", "")),
        stakeholders=list(data.get("stakeholders", [])),
        success_criteria=list(data.get("success_criteria", [])),
        business_consequence=str(data.get("business_consequence", "")),
        risk_opportunity=str(data.get("risk_opportunity", "")),
        why_relation=str(data.get("why_relation", "")),
        action_trigger=str(data.get("action_trigger", "")),
        required_metrics=list(data.get("required_metrics", [])),
        narrative=str(data.get("narrative", "")),
        metadata=dict(data.get("metadata", {})),
    )


def value_to_data(value: ValueSpec) -> dict:
    data = {
        "id": value.id,
        "stakeholders": sorted(value.stakeholders),
        "success_criteria": sorted(value.success_criteria),
        "business_consequence": value.business_consequence,
        "risk_opportunity": value.risk_opportunity,
        "why_relation": value.why_relation,
        "action_trigger": value.action_trigger,
        "narrative": value.narrative,
        "metadata": value.metadata,
    }
    if value.required_metrics:
        data["required_metrics"] = sorted(value.required_metrics)
    return data
