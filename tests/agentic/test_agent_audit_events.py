from __future__ import annotations

import pytest


pytestmark = pytest.mark.xfail(reason="agent runtime not implemented: audit event records are not emitted")


def test_agent_run_creates_audit_event(agent_run) -> None:
    assert agent_run()["audit_event"]["id"]


def test_audit_event_contains_input_hashes(agent_run) -> None:
    event = agent_run()["audit_event"]
    assert event["input_hashes"]["domain_hash"]
    assert event["input_hashes"]["surface_hash"]


def test_audit_event_contains_profile_id(agent_run) -> None:
    assert agent_run()["audit_event"]["profile_id"] == "neara.cody_yakimoff"


def test_audit_event_contains_lens_id(agent_run) -> None:
    assert agent_run()["audit_event"]["lens_id"]


def test_audit_event_contains_action_result(agent_run) -> None:
    assert agent_run()["audit_event"]["action_result"]["status"]


def test_audit_event_contains_because_trace_hash(agent_run) -> None:
    assert agent_run()["audit_event"]["because_trace_hash"]
