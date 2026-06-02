from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SurfaceEdge:
    id: str
    from_node: str
    to_node: str
    type: str
    label: str
    weight_base: float = 1.0
    properties: dict[str, Any] = field(default_factory=dict)
    source_refs: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SurfaceGraph:
    id: str
    domain_id: str
    nodes: list[str]
    edges: list[SurfaceEdge]
    boundary: dict[str, Any]
    version: str

