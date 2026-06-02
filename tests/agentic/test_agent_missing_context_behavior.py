from __future__ import annotations

import pytest


pytestmark = pytest.mark.xfail(reason="agent runtime not implemented: missing-context statuses are not exposed")


def test_missing_domain_node_returns_context_gap(agent_run) -> None:
    assert agent_run(missing="domain_node")["status"] == "context_gap"


def test_missing_surface_edge_returns_missing_relationship(agent_run) -> None:
    assert agent_run(missing="surface_edge")["status"] == "missing_relationship"


def test_missing_lens_entrypoint_returns_invalid_lens_entrypoint(agent_run) -> None:
    assert agent_run(missing="lens_entrypoint")["status"] == "invalid_lens_entrypoint"


def test_missing_profile_permission_returns_approval_required_or_denied(agent_run) -> None:
    assert agent_run(missing="profile_permission")["status"] in {"approval_required", "denied"}


def test_missing_value_metric_returns_value_gap(agent_run) -> None:
    assert agent_run(missing="value_metric")["status"] == "missing_metric"


def test_agent_proposes_intake_requirement_instead_of_fabricating(agent_run) -> None:
    run = agent_run(missing="source_evidence")
    assert run["status"] == "context_gap"
    assert run["proposed_action"] == "request_intake_requirement"
    assert not run["fabrications"]
