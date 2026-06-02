from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ValueSpec:
    id: str
    stakeholders: list[str]
    success_criteria: list[str]
    business_consequence: str
    risk_opportunity: str
    why_relation: str
    action_trigger: str
    required_metrics: list[str] = field(default_factory=list)
    narrative: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
