from __future__ import annotations

from tests.test_playground_cli import SCE, run_corus


def run_agent_json(profile: str, lens: str = "vegetation_ops") -> dict:
    return run_corus("agent-run", str(SCE), "--profile", profile, "--lens", lens)


def test_sce_grid_ops_profile_generates_work_packet() -> None:
    result = run_agent_json("sce_grid_ops")
    agent_run = result.get("agent_run", result)
    assert agent_run["profile_id"] == "sce_grid_ops"
    assert agent_run["core_question"] == "What work needs to happen, where, and with what operational impact?"
    action_result = agent_run["action_result"]
    assert action_result["proposed_action"] == "generate_work_packet"
    assert action_result["permission_result"] == "allowed"
    assert {"action": "dispatch_crew", "permission_result": "approval_required"} in action_result["restricted_actions"]


def test_neara_value_architect_profile_generates_value_story() -> None:
    result = run_agent_json("neara_value_architect")
    agent_run = result.get("agent_run", result)
    assert agent_run["profile_id"] == "neara_value_architect"
    assert agent_run["core_question"] == "Can this model delta become a reusable customer value pattern?"
    action_result = agent_run["action_result"]
    assert action_result["proposed_action"] == "generate_value_story"
    assert action_result["permission_result"] == "allowed"
    assert "Neara can reuse the model-delta-to-value pattern for other utility customers." in agent_run["path_summary"]["value_metrics"]


def test_profiles_produce_different_actions_from_same_context() -> None:
    sce_run = run_agent_json("sce_grid_ops")["agent_run"]
    neara_run = run_agent_json("neara_value_architect")["agent_run"]
    assert sce_run["path_hash"] == neara_run["path_hash"]
    assert sce_run["action_result"]["proposed_action"] != neara_run["action_result"]["proposed_action"]
    assert sce_run["profile_id"] != neara_run["profile_id"]
    assert sce_run["audit_event"]["hash"] != neara_run["audit_event"]["hash"]


def test_neara_value_architect_cannot_dispatch_crews() -> None:
    agent_run = run_agent_json("neara_value_architect")["agent_run"]
    restricted = agent_run["action_result"]["restricted_actions"]
    assert any(
        item["action"] == "dispatch_crew"
        and item["permission_result"] in {"approval_required", "denied"}
        for item in restricted
    )
    assert {"action": "change_customer_policy", "permission_result": "approval_required"} in restricted
    assert {"action": "commit_customer_budget", "permission_result": "approval_required"} in restricted

