from __future__ import annotations

from tests.helpers import cody_result, clone_yaml, write_contract


def test_policy_delta_changes_context_hash(tmp_path, paths: dict) -> None:
    domain = clone_yaml(paths["domain"])
    for node in domain["nodes"]:
        if node["id"] == "sce.clearance_policy":
            node["properties"]["delta"] = "5m_to_7m"
    changed_domain = write_contract(tmp_path, "policy_delta.domain", domain)
    assert cody_result(domain_path=changed_domain)["layer_hashes"]["context_hash"] != cody_result()["layer_hashes"]["context_hash"]


def test_policy_delta_remains_explainable() -> None:
    result = cody_result()
    assert "sce.clearance_policy" in result["because_trace"]["domain_nodes"]
    assert any("policy" in edge for edge in result["because_trace"]["surface_edges"])

