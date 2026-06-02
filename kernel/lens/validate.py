from __future__ import annotations

from kernel.domain.model import Domain
from kernel.lens.model import Lens
from kernel.surface.edges import EDGE_TYPES


class LensValidationError(ValueError):
    pass


def validate_lens(lens: Lens, domain: Domain | None = None) -> None:
    if not lens.id:
        raise LensValidationError("lens must have an id")
    if not lens.core_question_pattern:
        raise LensValidationError(f"lens {lens.id} must define a core_question_pattern")
    if not lens.node_weight_rules:
        raise LensValidationError(f"lens {lens.id} must define node_weight_rules")
    if not lens.edge_weight_rules:
        raise LensValidationError(f"lens {lens.id} must define edge_weight_rules")

    domain_types = set(domain.node_types) if domain else None
    for rule in lens.node_weight_rules:
        if not rule.match:
            raise LensValidationError(f"lens {lens.id} has an empty node weight rule")
        if domain_types is not None and rule.match not in domain_types:
            raise LensValidationError(f"lens {lens.id} references nonexistent node type {rule.match}")

    for rule in lens.edge_weight_rules:
        if rule.match not in EDGE_TYPES:
            raise LensValidationError(f"lens {lens.id} references nonexistent edge type {rule.match}")

