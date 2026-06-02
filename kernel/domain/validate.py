from __future__ import annotations

from kernel.domain.model import Domain


class DomainValidationError(ValueError):
    pass


def validate_domain(domain: Domain) -> None:
    if not domain.id:
        raise DomainValidationError("domain must have an id")
    if not domain.version:
        raise DomainValidationError("domain must have a version")
    if not domain.node_types:
        raise DomainValidationError("domain must define node_types")

    seen: set[str] = set()
    for node in domain.nodes:
        if not node.id:
            raise DomainValidationError("every domain node must have an id")
        if node.id in seen:
            raise DomainValidationError(f"duplicate domain node id: {node.id}")
        seen.add(node.id)
        if not node.type:
            raise DomainValidationError(f"domain node {node.id} must have a type")
        if node.type not in domain.node_types:
            raise DomainValidationError(f"domain node {node.id} has invalid type {node.type}")
        if not node.label:
            raise DomainValidationError(f"domain node {node.id} must have a label")

