from __future__ import annotations

import pytest


pytestmark = pytest.mark.xfail(reason="agent runtime not implemented: fabrication reports are not exposed")


def test_agent_cannot_reference_unknown_domain_node(agent_run) -> None:
    run = agent_run()
    assert set(run["referenced_node_ids"]) <= set(run["domain_node_ids"])


def test_agent_cannot_reference_unknown_surface_edge(agent_run) -> None:
    run = agent_run()
    assert set(run["referenced_edge_ids"]) <= set(run["surface_edge_ids"])


def test_agent_cannot_create_value_metric(agent_run) -> None:
    run = agent_run()
    assert set(run["referenced_metrics"]) <= set(run["value_metrics"])


def test_agent_cannot_invent_permission(agent_run) -> None:
    run = agent_run()
    assert set(run["permission_checks"]) <= set(run["profile_permissions"])


def test_agent_cannot_emit_unsupported_because_claim(agent_run) -> None:
    for claim in agent_run()["because_trace"]["claims"]:
        assert claim["lineage"]


def test_agent_outputs_empty_fabrication_lists(agent_run) -> None:
    assert agent_run()["fabrications"] == {"nodes": [], "edges": [], "metrics": [], "permissions": []}
