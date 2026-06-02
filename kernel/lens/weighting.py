from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from kernel.domain.model import Domain
from kernel.lens.model import Lens
from kernel.surface.graph import SurfaceGraph


@dataclass(frozen=True)
class WeightedNode:
    id: str
    type: str
    label: str
    weight: float


@dataclass(frozen=True)
class WeightedEdge:
    id: str
    from_node: str
    to_node: str
    type: str
    label: str
    weight: float


@dataclass(frozen=True)
class WeightedGraph:
    nodes: list[WeightedNode]
    edges: list[WeightedEdge]
    first_order_context: dict[str, Any]
    gaps: list[str]


def _node_weight(node_type: str, lens: Lens) -> float:
    return 1.0 + sum(rule.weight for rule in lens.node_weight_rules if rule.match == node_type)


def _edge_weight(edge_type: str, base: float, lens: Lens) -> float:
    return base + sum(rule.weight for rule in lens.edge_weight_rules if rule.match == edge_type)


def apply_lens(lens: Lens, surface: SurfaceGraph, domain: Domain) -> WeightedGraph:
    nodes_by_id = domain.node_by_id()
    weighted_nodes = [
        WeightedNode(
            id=node_id,
            type=nodes_by_id[node_id].type,
            label=nodes_by_id[node_id].label,
            weight=_node_weight(nodes_by_id[node_id].type, lens),
        )
        for node_id in surface.nodes
    ]
    weighted_edges = [
        WeightedEdge(
            id=edge.id,
            from_node=edge.from_node,
            to_node=edge.to_node,
            type=edge.type,
            label=edge.label,
            weight=_edge_weight(edge.type, edge.weight_base, lens),
        )
        for edge in surface.edges
    ]
    weighted_nodes = sorted(weighted_nodes, key=lambda item: (-item.weight, item.id))
    weighted_edges = sorted(weighted_edges, key=lambda item: (-item.weight, item.id))
    first_order_ids = [node.id for node in weighted_nodes[: int(lens.first_order_scoring.get("limit", 5))]]
    gaps = []
    if not weighted_edges:
        gaps.append("surface graph has no edges")
    return WeightedGraph(
        nodes=weighted_nodes,
        edges=weighted_edges,
        first_order_context={
            "surface_id": surface.id,
            "node_ids": first_order_ids,
            "edge_ids": [edge.id for edge in weighted_edges[:5]],
        },
        gaps=gaps,
    )


def weighted_graph_to_data(graph: WeightedGraph) -> dict[str, Any]:
    return {
        "weighted_nodes": [node.__dict__ for node in graph.nodes],
        "weighted_edges": [edge.__dict__ for edge in graph.edges],
        "first_order_context": graph.first_order_context,
        "gaps": graph.gaps,
    }

