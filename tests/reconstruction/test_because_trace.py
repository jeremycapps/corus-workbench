from __future__ import annotations

from tests.helpers import cody_result
from kernel.engine.hashing import hash_data


def test_because_trace_exists_for_context_output() -> None:
    assert cody_result()["because_trace"]


def test_because_trace_references_observations() -> None:
    assert "vegetation-observations.timpos" in cody_result()["because_trace"]["observations"]


def test_because_trace_references_domain_rules() -> None:
    assert "sce.clearance_policy" in cody_result()["because_trace"]["domain_nodes"]


def test_because_trace_references_surface_edges() -> None:
    assert cody_result()["because_trace"]["surface_edges"]


def test_because_trace_references_profile_for_profiled_output() -> None:
    assert cody_result()["because_trace"]["profile"] == "neara.cody_yakimoff"


def test_because_trace_references_value_metrics_for_value_output() -> None:
    assert cody_result()["because_trace"]["value_metrics"]


def test_every_because_claim_has_lineage() -> None:
    for claim in cody_result()["because_trace"]["claims"]:
        assert claim["lineage"]


def test_because_trace_rejects_unsupported_claims() -> None:
    supported = {
        "observations",
        "domain_nodes",
        "surface_edges",
        "profile",
        "lens",
        "value",
        "value_metrics",
        "first_order_context",
        "weighted_node_list",
        "weighted_edge_list",
    }
    for claim in cody_result()["because_trace"]["claims"]:
        assert set(claim["lineage"]) <= supported


def test_because_trace_hash_is_deterministic() -> None:
    first = cody_result()["because_trace"]
    second = cody_result()["because_trace"]
    assert first["hash"] == second["hash"]
    assert hash_data(first["claims"]) == hash_data(second["claims"])
