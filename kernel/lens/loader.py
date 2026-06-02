from __future__ import annotations

from pathlib import Path
from typing import Any

from kernel.lens.model import Lens, WeightRule
from kernel.verify.hash import read_yaml


def _rules(items: list[dict[str, Any]]) -> list[WeightRule]:
    return [WeightRule(match=str(item.get("match", "")), weight=float(item.get("weight", 0.0))) for item in items]


def load_lens(path: Path) -> Lens:
    data = read_yaml(path)
    return Lens(
        id=str(data.get("id") or data.get("lens", "")),
        name=str(data.get("name") or data.get("id") or data.get("lens", "")),
        core_question_pattern=str(data.get("core_question_pattern", "")),
        node_weight_rules=_rules(list(data.get("node_weight_rules", []))),
        edge_weight_rules=_rules(list(data.get("edge_weight_rules", []))),
        abstraction_preference=str(data.get("abstraction_preference", "balanced")),
        evidence_preference=str(data.get("evidence_preference", "source_grounded")),
        first_order_scoring=dict(data.get("first_order_scoring", {})),
    )


def lens_to_data(lens: Lens) -> dict[str, Any]:
    return {
        "id": lens.id,
        "name": lens.name,
        "core_question_pattern": lens.core_question_pattern,
        "node_weight_rules": [
            {"match": rule.match, "weight": rule.weight}
            for rule in sorted(lens.node_weight_rules, key=lambda item: item.match)
        ],
        "edge_weight_rules": [
            {"match": rule.match, "weight": rule.weight}
            for rule in sorted(lens.edge_weight_rules, key=lambda item: item.match)
        ],
        "abstraction_preference": lens.abstraction_preference,
        "evidence_preference": lens.evidence_preference,
        "first_order_scoring": lens.first_order_scoring,
    }

