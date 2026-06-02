from __future__ import annotations

import pytest

from tests.helpers import clone_yaml, contract_hash, write_contract
from kernel.domain.loader import load_domain
from kernel.surface.loader import load_surface
from kernel.surface.validate import SurfaceValidationError, validate_surface


def test_surface_edges_reference_domain_nodes(paths: dict) -> None:
    domain = load_domain(paths["domain"])
    surface = load_surface(paths["surface"])
    validate_surface(surface, domain)
    domain_ids = domain.node_ids()
    assert all(edge.from_node in domain_ids and edge.to_node in domain_ids for edge in surface.edges)


def test_surface_rejects_dangling_edges(tmp_path, paths: dict) -> None:
    data = clone_yaml(paths["surface"])
    data["edges"][0]["to_node"] = "missing.node"
    bad = write_contract(tmp_path, "dangling.surface", data)
    with pytest.raises(SurfaceValidationError, match="missing"):
        validate_surface(load_surface(bad), load_domain(paths["domain"]))


def test_surface_cannot_invent_nodes(tmp_path, paths: dict) -> None:
    data = clone_yaml(paths["surface"])
    data["nodes"].append("invented.node")
    bad = write_contract(tmp_path, "invented.surface", data)
    with pytest.raises(SurfaceValidationError, match="missing from domain"):
        validate_surface(load_surface(bad), load_domain(paths["domain"]))


def test_surface_canonical_graph_hash_is_stable(tmp_path, paths: dict) -> None:
    data = clone_yaml(paths["surface"])
    data["nodes"] = list(reversed(data["nodes"]))
    data["edges"] = list(reversed(data["edges"]))
    reordered = write_contract(tmp_path, "reordered.surface", data)
    assert contract_hash(reordered) == contract_hash(paths["surface"])


def test_surface_change_changes_context_relationships(tmp_path, paths: dict) -> None:
    data = clone_yaml(paths["surface"])
    data["edges"][0]["label"] = "Changed relationship."
    changed = write_contract(tmp_path, "changed.surface", data)
    assert contract_hash(changed) != contract_hash(paths["surface"])


def test_surface_is_graph_not_meaning_source(paths: dict) -> None:
    data = clone_yaml(paths["surface"])
    assert "node_types" not in data
    assert all("meaning" not in edge for edge in data["edges"])

