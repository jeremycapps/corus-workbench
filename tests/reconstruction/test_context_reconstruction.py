from __future__ import annotations

from tests.helpers import cody_result


def test_context_is_reconstructed_not_loaded_as_truth() -> None:
    result = cody_result()
    assert result["first_order_context"]
    assert "manual_context" not in result


def test_context_references_source_observations() -> None:
    assert "vegetation-observations.timpos" in cody_result()["evidence_summary"]["source_refs"]


def test_context_references_domain_rules() -> None:
    result = cody_result()
    assert "sce.clearance_policy" in result["domain_node_ids_used"]


def test_context_references_surface_edges() -> None:
    result = cody_result()
    assert result["weighted_edge_list"]
    assert "edge.policy.watch_points" in {edge["id"] for edge in result["weighted_edge_list"]}


def test_context_hash_is_stable_for_same_inputs() -> None:
    assert cody_result()["layer_hashes"]["context_hash"] == cody_result()["layer_hashes"]["context_hash"]


def test_timpo_plus_domain_plus_surface_equals_context() -> None:
    result = cody_result()
    assert result["because_trace"]["observations"]
    assert result["because_trace"]["domain_nodes"]
    assert result["because_trace"]["surface_edges"]

