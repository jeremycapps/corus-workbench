from __future__ import annotations

import pytest


pytestmark = pytest.mark.xfail(reason="agent runtime not implemented: action initiation records are not exposed")


def test_action_includes_initiating_profile_id(agent_run) -> None:
    action = agent_run(action="recommend_productization_pattern")["action"]
    assert action["initiated_by"] == "neara.cody_yakimoff"


def test_action_includes_lens_id(agent_run) -> None:
    assert agent_run()["action"]["lens_id"]


def test_action_includes_graph_path(agent_run) -> None:
    assert agent_run()["action"]["graph_path"]


def test_action_includes_permission_check(agent_run) -> None:
    assert agent_run()["action"]["permission_check"]["status"]


def test_action_includes_reason_trace(agent_run) -> None:
    assert agent_run()["action"]["reason_trace"]["lineage"]


def test_action_creates_audit_event(agent_run) -> None:
    assert agent_run()["audit_event"]
