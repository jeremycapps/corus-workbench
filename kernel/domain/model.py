from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DomainNode:
    id: str
    type: str
    label: str
    properties: dict[str, Any] = field(default_factory=dict)
    source_refs: list[str] = field(default_factory=list)
    version: str = "1.0.0"


@dataclass(frozen=True)
class Domain:
    id: str
    version: str
    node_types: list[str]
    nodes: list[DomainNode]

    def node_ids(self) -> set[str]:
        return {node.id for node in self.nodes}

    def node_by_id(self) -> dict[str, DomainNode]:
        return {node.id: node for node in self.nodes}

