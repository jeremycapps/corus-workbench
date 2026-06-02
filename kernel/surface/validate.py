from __future__ import annotations

from kernel.domain.model import Domain
from kernel.surface.edges import EDGE_TYPES
from kernel.surface.graph import SurfaceGraph


class SurfaceValidationError(ValueError):
    pass


def validate_surface(surface: SurfaceGraph, domain: Domain) -> None:
    if not surface.id:
        raise SurfaceValidationError("surface graph must have an id")
    if surface.domain_id != domain.id:
        raise SurfaceValidationError(f"surface {surface.id} references unknown domain {surface.domain_id}")
    if not surface.boundary:
        raise SurfaceValidationError(f"surface {surface.id} must define a boundary")

    domain_nodes = domain.node_ids()
    for node_id in surface.nodes:
        if node_id not in domain_nodes:
            raise SurfaceValidationError(f"surface node {node_id} is missing from domain {domain.id}")

    seen: set[str] = set()
    for edge in surface.edges:
        if not edge.id:
            raise SurfaceValidationError("every surface edge must have an id")
        if edge.id in seen:
            raise SurfaceValidationError(f"duplicate surface edge id: {edge.id}")
        seen.add(edge.id)
        if edge.from_node not in domain_nodes:
            raise SurfaceValidationError(f"edge {edge.id} references missing from_node {edge.from_node}")
        if edge.to_node not in domain_nodes:
            raise SurfaceValidationError(f"edge {edge.id} references missing to_node {edge.to_node}")
        if edge.type not in EDGE_TYPES:
            raise SurfaceValidationError(f"edge {edge.id} has unregistered type {edge.type}")

