from __future__ import annotations

import pytest


pytestmark = pytest.mark.xfail(reason="agent runtime not implemented: permission boundary decisions are not exposed")


def test_agent_can_read_permitted_graph_region(agent_run) -> None:
    assert agent_run()["permissions"]["read_context"] == "allowed"


def test_agent_cannot_read_blocked_graph_region(agent_run) -> None:
    assert agent_run(blocked_region=True)["permissions"]["read_blocked_region"] == "denied"


def test_agent_can_propose_allowed_action(agent_run) -> None:
    assert agent_run(action="recommend_productization_pattern")["action"]["status"] in {"proposed", "executed"}


def test_agent_requires_approval_for_restricted_action(agent_run) -> None:
    assert agent_run(action="dispatch_crews")["action"]["status"] == "approval_required"


def test_agent_cannot_execute_denied_action(agent_run) -> None:
    assert agent_run(action="mutate_domain")["action"]["status"] == "denied"


def test_agent_cannot_mutate_domain(agent_run) -> None:
    run = agent_run(action="read_context")
    assert run["before_hashes"]["domain_hash"] == run["after_hashes"]["domain_hash"]


def test_agent_cannot_mutate_surface(agent_run) -> None:
    run = agent_run(action="read_context")
    assert run["before_hashes"]["surface_hash"] == run["after_hashes"]["surface_hash"]


def test_agent_cannot_silently_change_profile(agent_run) -> None:
    run = agent_run(action="read_context")
    assert run["before_hashes"]["profile_hash"] == run["after_hashes"]["profile_hash"]
