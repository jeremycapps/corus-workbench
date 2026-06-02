from __future__ import annotations

import pytest


pytestmark = pytest.mark.xfail(reason="agent runtime not implemented: graph traversal API and selected path are not exposed")


def test_agent_starts_from_profile_selected_lens(agent_run) -> None:
    run = agent_run()
    assert run["profile_id"]
    assert run["lens_id"]
    assert run["lens_id"] in run["profile"]["allowed_lenses"]


def test_agent_enters_graph_through_valid_lens_entrypoint(agent_run) -> None:
    run = agent_run()
    assert run["entrypoint"] in run["surface_node_ids"]


def test_agent_traverses_only_valid_surface_edges(agent_run) -> None:
    run = agent_run()
    assert set(step["edge_id"] for step in run["traversal_path"]) <= set(run["surface_edge_ids"])


def test_agent_cannot_jump_to_unrelated_nodes(agent_run) -> None:
    run = agent_run()
    assert set(run["selected_node_ids"]) <= set(run["surface_node_ids"])


def test_agent_returns_selected_path(agent_run) -> None:
    run = agent_run()
    assert run["traversal_path"]


def test_agent_returns_reason_trace_for_path(agent_run) -> None:
    run = agent_run()
    assert run["reason_trace"]["path"]
    assert run["reason_trace"]["lineage"]
