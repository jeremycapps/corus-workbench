from __future__ import annotations

from pathlib import Path
from typing import Any

from kernel.surface.graph import SurfaceEdge, SurfaceGraph
from kernel.verify.hash import read_yaml


def load_surface(path: Path) -> SurfaceGraph:
    data = read_yaml(path)
    edges = [
        SurfaceEdge(
            id=str(item.get("id", "")),
            from_node=str(item.get("from_node", "")),
            to_node=str(item.get("to_node", "")),
            type=str(item.get("type", "")),
            label=str(item.get("label", "")),
            weight_base=float(item.get("weight_base", 1.0)),
            properties=dict(item.get("properties", {})),
            source_refs=list(item.get("source_refs", [])),
        )
        for item in data.get("edges", [])
    ]
    return SurfaceGraph(
        id=str(data.get("id") or data.get("surface", "")),
        domain_id=str(data.get("domain_id", "")),
        nodes=list(data.get("nodes", [])),
        edges=edges,
        boundary=dict(data.get("boundary", {})),
        version=str(data.get("version", "")),
    )


def surface_to_data(surface: SurfaceGraph) -> dict[str, Any]:
    return {
        "id": surface.id,
        "domain_id": surface.domain_id,
        "nodes": sorted(surface.nodes),
        "edges": [
            {
                "id": edge.id,
                "from_node": edge.from_node,
                "to_node": edge.to_node,
                "type": edge.type,
                "label": edge.label,
                "weight_base": edge.weight_base,
                "properties": edge.properties,
                "source_refs": sorted(edge.source_refs),
            }
            for edge in sorted(surface.edges, key=lambda item: item.id)
        ],
        "boundary": surface.boundary,
        "version": surface.version,
    }

