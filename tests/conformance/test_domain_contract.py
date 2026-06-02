from __future__ import annotations

import pytest

from tests.helpers import clone_yaml, contract_hash, write_contract
from kernel.domain.loader import load_domain
from kernel.domain.validate import DomainValidationError, validate_domain


def test_domain_nodes_have_stable_ids(paths: dict) -> None:
    domain = load_domain(paths["domain"])
    validate_domain(domain)
    assert {node.id for node in domain.nodes}
    assert len({node.id for node in domain.nodes}) == len(domain.nodes)


def test_domain_nodes_define_meaning(paths: dict) -> None:
    domain = load_domain(paths["domain"])
    assert all(node.type and node.label for node in domain.nodes)
    assert "model_delta" in domain.node_types


def test_domain_rejects_duplicate_node_ids(tmp_path, paths: dict) -> None:
    data = clone_yaml(paths["domain"])
    data["nodes"].append(dict(data["nodes"][0]))
    bad = write_contract(tmp_path, "duplicate.domain", data)
    with pytest.raises(DomainValidationError, match="duplicate"):
        validate_domain(load_domain(bad))


def test_domain_does_not_define_surface_edges(paths: dict) -> None:
    data = clone_yaml(paths["domain"])
    assert "edges" not in data
    assert "relationships" not in data


def test_domain_does_not_define_profile_attention(paths: dict) -> None:
    data = clone_yaml(paths["domain"])
    assert "core_question" not in data
    assert "lens_ref" not in data
    assert "action_authority" not in data


def test_domain_hash_changes_when_meaning_changes(tmp_path, paths: dict) -> None:
    data = clone_yaml(paths["domain"])
    changed = clone_yaml(paths["domain"])
    changed["nodes"][0]["label"] = "Changed model delta meaning"
    changed_path = write_contract(tmp_path, "changed.domain", changed)
    assert contract_hash(changed_path) != contract_hash(paths["domain"])


def test_domain_is_meaning_not_projection(paths: dict) -> None:
    data = clone_yaml(paths["domain"])
    forbidden = {"weighted_nodes", "first_order_context", "stakeholders", "value_resolution"}
    assert forbidden.isdisjoint(data)

