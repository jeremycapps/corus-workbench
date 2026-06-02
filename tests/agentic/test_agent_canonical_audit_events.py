from __future__ import annotations

from tests.agentic.test_agent_profile_specific_actions import run_agent_json


def test_canonical_agent_run_contains_replayable_audit_event() -> None:
    agent_run = run_agent_json("sce_grid_ops")["agent_run"]
    audit_event = agent_run["audit_event"]

    assert audit_event["profile_id"] == "sce_grid_ops"
    assert audit_event["lens_id"] == "vegetation_ops"
    assert audit_event["source_hashes"] == agent_run["source_hashes"]
    assert audit_event["path_hash"] == agent_run["path_hash"]
    assert audit_event["action_result"] == agent_run["action_result"]
    assert audit_event["because_trace_hash"] == agent_run["because_trace_hash"]
    assert audit_event["hash"] == agent_run["audit_event_hash"]


def test_profile_specific_audit_events_share_path_but_not_action_hash() -> None:
    sce_run = run_agent_json("sce_grid_ops")["agent_run"]
    neara_run = run_agent_json("neara_value_architect")["agent_run"]

    assert sce_run["audit_event"]["path_hash"] == neara_run["audit_event"]["path_hash"]
    assert sce_run["audit_event"]["action_result"]["proposed_action"] == "generate_work_packet"
    assert neara_run["audit_event"]["action_result"]["proposed_action"] == "generate_value_story"
    assert sce_run["audit_event"]["hash"] != neara_run["audit_event"]["hash"]
