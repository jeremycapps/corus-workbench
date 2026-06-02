from __future__ import annotations

from tests.helpers import cody_result


def test_context_contains_lineage() -> None:
    trace = cody_result()["because_trace"]
    assert trace["observations"]
    assert trace["domain_nodes"]
    assert trace["surface_edges"]


def test_context_contains_source_hashes() -> None:
    hashes = cody_result()["layer_hashes"]
    assert hashes["domain_hash"]
    assert hashes["surface_hash"]


def test_context_cannot_reference_unknown_domain_nodes() -> None:
    result = cody_result()
    assert set(result["first_order_context"]["node_ids"]) <= set(result["domain_node_ids_used"])

