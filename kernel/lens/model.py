from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class WeightRule:
    match: str
    weight: float


@dataclass(frozen=True)
class Lens:
    id: str
    name: str
    core_question_pattern: str
    node_weight_rules: list[WeightRule]
    edge_weight_rules: list[WeightRule]
    abstraction_preference: str = "balanced"
    evidence_preference: str = "source_grounded"
    first_order_scoring: dict[str, Any] = field(default_factory=dict)

