from __future__ import annotations

import pytest


pytestmark = pytest.mark.xfail(reason="agent runtime not implemented: replayable action records are not exposed")


def test_agent_action_is_replayable(agent_run) -> None:
    assert agent_run()["replay"]["replayable"] is True


def test_replayed_agent_action_has_same_hash(agent_run) -> None:
    run = agent_run()
    assert run["action_hash"] == run["replay"]["action_hash"]


def test_replayed_agent_action_has_same_because_trace(agent_run) -> None:
    run = agent_run()
    assert run["because_trace"]["hash"] == run["replay"]["because_trace_hash"]


def test_replayed_agent_action_has_same_permission_result(agent_run) -> None:
    run = agent_run()
    assert run["action"]["permission_check"] == run["replay"]["permission_check"]


def test_replay_fails_if_source_hashes_change(agent_run) -> None:
    run = agent_run(source_hash_changed=True)
    assert run["replay"]["status"] == "invalidated"
