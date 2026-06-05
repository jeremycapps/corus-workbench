from __future__ import annotations

from pathlib import Path

from tests.helpers import cody_result
from kernel.verify.hash import read_yaml


SCE_FIXTURE = Path("tests/fixtures/sce_vegetation")


def test_sce_reconstructs_vegetation_context() -> None:
    result = cody_result()
    assert "sce.vegetation_watch_points" in result["domain_node_ids_used"]
    assert "sce.clearance_policy" in result["domain_node_ids_used"]


def test_sce_policy_delta_adds_watch_points() -> None:
    result = cody_result()
    assert "edge.policy.watch_points" in {edge["id"] for edge in result["weighted_edge_list"]}


def test_sce_output_contains_operational_context() -> None:
    result = cody_result()
    assert "sce.operational_priority" in result["first_order_context"]["node_ids"]


def test_sce_value_output_contains_budget_or_crew_significance() -> None:
    value = cody_result()["value_resolution"]
    text = " ".join([value["business_consequence"], value["narrative"], *value["success_criteria"]]).lower()
    assert "sce" in text
    assert "value" in text


def test_sce_because_trace_is_grounded() -> None:
    trace = cody_result()["because_trace"]
    assert trace["observations"]
    assert trace["domain_nodes"]
    assert trace["surface_edges"]


def test_sce_demo_proves_model_delta_to_customer_value() -> None:
    result = cody_result()
    ids = set(result["domain_node_ids_used"])
    assert {"neara.model_delta", "sce.customer_value", "neara.repeatable_product_pattern"} <= ids
    assert "Neara product value" in result["value_resolution"]["narrative"]


def test_sce_operational_facts_are_source_grounded_not_domain_embedded() -> None:
    domain = read_yaml(SCE_FIXTURE / "sce.domain")
    evidence = read_yaml(SCE_FIXTURE / "sce.evidence")

    forbidden_domain_fields = {
        "count",
        "total_validation_exposure",
        "watch_points_added",
        "clearance_delta",
        "delta",
    }
    for node in domain["nodes"]:
        node_keys = set(node)
        property_keys = set(node.get("properties", {}))
        assert not forbidden_domain_fields.intersection(node_keys)
        assert not forbidden_domain_fields.intersection(property_keys)

    fact_ids = {fact["id"] for fact in evidence["facts"]}
    assert "fact.watch_points.added" in fact_ids
    assert "fact.clearance_policy.delta" in fact_ids
    assert "fact.cost.validation_exposure" in fact_ids


def test_explain_uses_source_derived_operational_facts_for_sce_fixture() -> None:
    from tests.test_playground_cli import run_corus

    result = run_corus("explain", str(SCE_FIXTURE))
    assert "architectural_trace" in result
    assert "operational_trace" in result

    claims = result["operational_trace"]["claims"]
    assert any(
        claim.get("value") == 72
        and "sce.vegetation_watch_points" in claim.get("domain_nodes", [])
        for claim in claims
    )
    assert any(
        claim.get("value") == 25164
        and "sce.cost_exposure" in claim.get("domain_nodes", [])
        for claim in claims
    )
    assert any(
        claim.get("value_metric") == "SCE can translate watch points into workforce and budget planning."
        for claim in claims
    )
    for claim in claims:
        assert claim["id"]
        assert claim["claim"]
        assert claim["source_observation"]
        assert claim["domain_nodes"]
        assert "surface_edges" in claim


def test_operational_trace_connects_fact_to_customer_value_path() -> None:
    from tests.test_playground_cli import run_corus

    result = run_corus("explain", str(SCE_FIXTURE))
    assert "operational_trace" in result
    claims = result["operational_trace"]["claims"]

    watch_claim = next(claim for claim in claims if claim["id"] == "fact.watch_points.added")
    assert watch_claim["source_observation"] == "demo_model_output"
    assert "source.demo_model_output" in watch_claim["source_context_ids"]
    assert "source.sce_2025_wmp_update" in watch_claim["source_context_ids"]
    assert "demo_synthetic" in watch_claim["trust_status"]
    assert watch_claim["trust_note"]
    assert "sce.vegetation_watch_points" in watch_claim["domain_nodes"]
    assert "edge.policy.watch_points" in watch_claim["surface_edges"]
    assert "edge.watch_points.risk" in watch_claim["surface_edges"]

    cost_claim = next(claim for claim in claims if claim["id"] == "fact.cost.validation_exposure")
    assert cost_claim["value"] == 25164
    assert cost_claim["unit"] == "dollars"
    assert "sce.cost_exposure" in cost_claim["domain_nodes"]
    assert "edge.crew_hours.cost" in cost_claim["surface_edges"]
    assert "edge.cost.customer_value" in cost_claim["surface_edges"]

    value_claim = next(claim for claim in claims if claim["id"] == "fact.cost.customer_value")
    assert value_claim["value_metric"] == "SCE can translate watch points into workforce and budget planning."
    assert "sce.customer_value" in value_claim["domain_nodes"]


def test_operational_trace_contains_surface_path_to_customer_value() -> None:
    from tests.test_playground_cli import run_corus

    result = run_corus("explain", str(SCE_FIXTURE))
    path_summary = result["operational_trace"]["path_summary"]
    assert path_summary["start"] == "fact.watch_points.added"
    assert path_summary["end"] == "fact.cost.customer_value"
    assert "demo_model_output" in path_summary["source_observations"]
    assert "demo_customer_input" in path_summary["source_observations"]
    assert path_summary["domain_path"] == [
        "neara.model_delta",
        "sce.clearance_policy",
        "sce.vegetation_watch_points",
        "sce.wildfire_risk",
        "sce.operational_priority",
        "sce.crew_hours",
        "sce.cost_exposure",
        "sce.customer_value",
    ]
    assert path_summary["surface_path"] == [
        "edge.model_delta.policy",
        "edge.policy.watch_points",
        "edge.watch_points.risk",
        "edge.risk.priority",
        "edge.priority.crew_hours",
        "edge.crew_hours.cost",
        "edge.cost.customer_value",
    ]
    assert "SCE can translate watch points into workforce and budget planning." in path_summary["value_metrics"]
