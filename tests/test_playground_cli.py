from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCE = ROOT / "tests" / "fixtures" / "sce_vegetation"
DELTA = ROOT / "tests" / "fixtures" / "neara_policy_delta"


def run_corus(*args: str) -> dict:
    completed = subprocess.run(
        [sys.executable, "-m", "corus", *args, "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(completed.stdout)


def test_playground_validate_json() -> None:
    result = run_corus("validate", str(SCE))
    assert result["timpo"]["valid"] is True
    assert result["domain"]["valid"] is True
    assert result["surface"]["valid"] is True
    assert result["lens"][0]["valid"] is True
    assert all(profile["valid"] for profile in result["profile"])
    assert {profile["id"] for profile in result["profile"]} == {"neara_value_architect", "sce_grid_ops"}
    assert result["value"]["valid"] is True
    assert result["evidence"]["valid"] is True


def test_playground_project_json() -> None:
    result = run_corus("project", str(SCE), "--profile", "sce_grid_ops", "--lens", "vegetation_ops")
    assert result["profile_id"] == "sce_grid_ops"
    assert result["lens_id"] == "vegetation_ops"
    assert result["selected_nodes"]
    assert result["projection_hash"]


def test_playground_diff_json() -> None:
    result = run_corus("diff", str(DELTA))
    assert result["before_hash"] != result["after_hash"]
    assert result["changed_layer"] == "domain"
    assert "sce.operational_priority" in result["added_context_elements"]


def test_playground_explain_has_architectural_and_operational_traces() -> None:
    result = run_corus("explain", str(SCE))
    assert "architectural_trace" in result
    assert "operational_trace" in result
    assert result["architectural_trace"]["because_trace"]
    assert result["operational_trace"]["claims"]


def test_playground_explain_operational_trace_uses_specific_lineage() -> None:
    result = run_corus("explain", str(SCE))
    operational = result["operational_trace"]
    assert operational["path"] == [
        "sce.source_evidence",
        "neara.model_delta",
        "sce.clearance_policy",
        "sce.vegetation_watch_points",
        "sce.wildfire_risk",
        "sce.operational_priority",
        "sce.crew_hours",
        "sce.cost_exposure",
        "sce.customer_value",
        "neara.repeatable_product_pattern",
    ]
    for claim in operational["claims"]:
        assert claim["id"]
        assert claim["claim"]
        assert claim["specific_observation_ids"] == ["vegetation-point-001", "vegetation-point-002"]
        assert claim["domain_node_ids"]
        assert claim["surface_edge_ids"]
        assert claim["lineage_hash"]
        assert "observations" not in claim["domain_node_ids"]
        assert "domain_nodes" not in claim["surface_edge_ids"]


def test_playground_explain_operational_trace_reaches_customer_value_and_product_pattern() -> None:
    result = run_corus("explain", str(SCE))
    claims = result["operational_trace"]["claims"]
    edge_ids = {edge_id for claim in claims for edge_id in claim["surface_edge_ids"]}
    assert "edge.cost.customer_value" in edge_ids
    assert "edge.customer_value.product_pattern" in edge_ids
    value_claims = [claim for claim in claims if "sce.customer_value" in claim["domain_node_ids"]]
    assert any(claim["value_metric"] == "SCE can translate watch points into workforce and budget planning." for claim in value_claims)


def test_playground_explain_human_output_has_operational_sections() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "corus", "explain", str(SCE)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    output = completed.stdout
    assert "Architectural Trace" in output
    assert "Operational Trace" in output
    assert "Operational Path" in output
    assert "Because" in output
    assert "The model delta produced 72 vegetation watch points." in output
    assert "Value: 25164 dollars" in output


def test_playground_agent_run_uses_operational_path_and_profile_permissions() -> None:
    result = run_corus("agent-run", str(SCE), "--profile", "sce_grid_ops", "--lens", "vegetation_ops")
    agent_run = result["agent_run"]
    assert agent_run["initiated_by"] == "sce_grid_ops"
    assert agent_run["lens_id"] == "vegetation_ops"
    assert agent_run["core_question"]
    assert agent_run["action_result"]["proposed_action"] == "generate_work_packet"
    assert agent_run["action_result"]["permission_result"] == "allowed"
    assert {"action": "dispatch_crew", "permission_result": "approval_required"} in agent_run["action_result"]["restricted_actions"]
    assert agent_run["path_summary"]["start"] == "fact.watch_points.added"
    assert agent_run["path_summary"]["end"] == "fact.cost.customer_value"
    assert agent_run["path_hash"]
    assert agent_run["because_trace_hash"]
    assert agent_run["audit_event"]["profile_id"] == "sce_grid_ops"
    assert agent_run["audit_event"]["lens_id"] == "vegetation_ops"
    assert agent_run["audit_event"]["source_hashes"]["evidence_hash"]
    assert agent_run["audit_event"]["action_result"]["permission_result"] == "allowed"
    assert agent_run["audit_event"]["hash"] == agent_run["audit_event_hash"]


def test_playground_agent_run_human_output_has_profile_action_and_audit() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "corus", "agent-run", str(SCE), "--profile", "sce_grid_ops", "--lens", "vegetation_ops"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    output = completed.stdout
    assert "Profile: sce_grid_ops" in output
    assert "Core Question: What work needs to happen, where, and with what operational impact?" in output
    assert "- generate_work_packet: allowed" in output
    assert "- dispatch_crew: approval_required" in output
    assert "Audit Event:" in output


def test_playground_read_human_output_has_demo_sections() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "corus", "read", str(SCE), "--profile", "sce_grid_ops", "--lens", "vegetation_ops"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    output = completed.stdout

    assert "Architecture" in output
    assert "Read Context" in output
    assert "profile: profile.sce_grid_ops" in output
    assert "lens: lens.vegetation_ops" in output
    assert "core_question:" in output
    assert "Ledger" in output
    assert "Admission Trail" in output
    assert "source.demo_model_output was added" in output
    assert "claim.sce.watch_points_added was interpreted" in output
    assert "claim.sce.watch_points_added was validated" in output
    assert "claim.sce.unsupported_cost_assumption was interpreted" in output
    assert "claim.sce.unsupported_cost_assumption was rejected" in output
    assert "Included Claims" in output
    assert "Excluded Claims" in output
    assert "Declared Contracts" in output
    assert "Outputs" in output
    assert "Invariant" in output
    assert "claim.sce.watch_points_added" in output
    assert "claim.sce.unsupported_cost_assumption" in output
    assert "A claim can exist in the ledger without existing in active context." in output
    assert "Projection hash:" not in output
    assert "Read projection hash:" in output


def test_playground_audit_included_claim_human_output() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "corus", "audit", str(SCE), "--target", "claim.sce.watch_points_added"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    output = completed.stdout

    assert "claim.sce.watch_points_added" in output
    assert "valid: true" in output
    assert "active_context: included" in output
    assert "admissibility: pass" in output


def test_playground_audit_rejected_claim_human_output() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "corus", "audit", str(SCE), "--target", "claim.sce.unsupported_cost_assumption"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    output = completed.stdout

    assert "claim.sce.unsupported_cost_assumption" in output
    assert "valid: true" in output
    assert "active_context: excluded" in output
    assert "admissible false" in output


def test_playground_audit_output_human_output() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "corus", "audit", str(SCE), "--target", "output.sce_grid_ops.work_packet"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    output = completed.stdout

    assert "output.sce_grid_ops.work_packet" in output
    assert "valid: true" in output
    assert "profile.sce_grid_ops" in output
    assert "generate_work_packet" in output
    assert "dispatch_crew" in output
    assert "approval_required" in output
    assert "profile_permissions: pass" in output


def test_playground_audit_json_still_exposes_proof_fields() -> None:
    for target in [
        "claim.sce.watch_points_added",
        "claim.sce.unsupported_cost_assumption",
        "output.sce_grid_ops.work_packet",
    ]:
        proof = run_corus("audit", str(SCE), "--target", target)
        assert proof["target"]
        assert "valid" in proof
        assert proof["checks"]
        assert proof["checks"]["ledger_chain"]
        assert proof["checks"]["payload_hashes"]
        assert proof["checks"]["profile_permissions"]


def test_playground_agent_run_requires_profile_when_fixture_has_multiple_profiles() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "corus", "agent-run", str(SCE), "--lens", "vegetation_ops"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert completed.returncode != 0
    assert "Multiple profiles found. Please pass --profile." in completed.stderr
