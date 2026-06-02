from __future__ import annotations

from pathlib import Path
from typing import Any

from kernel.domain.model import Domain, DomainNode
from kernel.verify.hash import read_yaml


def load_domain(path: Path) -> Domain:
    data = read_yaml(path)
    node_types = list(data.get("node_types", []))
    nodes: list[DomainNode] = []
    for item in data.get("nodes", []):
        nodes.append(
            DomainNode(
                id=str(item.get("id", "")),
                type=str(item.get("type", "")),
                label=str(item.get("label", "")),
                properties=dict(item.get("properties", {})),
                source_refs=list(item.get("source_refs", [])),
                version=str(item.get("version", data.get("version", "1.0.0"))),
            )
        )
    return Domain(
        id=str(data.get("id") or data.get("domain", "")),
        version=str(data.get("version", "")),
        node_types=node_types,
        nodes=nodes,
    )


def domain_to_data(domain: Domain) -> dict[str, Any]:
    return {
        "id": domain.id,
        "version": domain.version,
        "node_types": sorted(domain.node_types),
        "nodes": [
            {
                "id": node.id,
                "type": node.type,
                "label": node.label,
                "properties": node.properties,
                "source_refs": sorted(node.source_refs),
                "version": node.version,
            }
            for node in sorted(domain.nodes, key=lambda item: item.id)
        ],
    }

