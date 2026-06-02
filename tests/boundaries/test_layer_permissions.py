from __future__ import annotations

from tests.helpers import cody_result, clone_yaml


def test_domain_surface_lens_profile_value_stay_separate(paths: dict) -> None:
    assert "edges" not in clone_yaml(paths["domain"])
    assert "node_types" not in clone_yaml(paths["surface"])
    assert "nodes" not in clone_yaml(paths["lens"])
    assert "edges" not in clone_yaml(paths["profile"])
    assert "action_authority" not in clone_yaml(paths["value"])


def test_context_hash_does_not_depend_on_profile_or_value() -> None:
    result = cody_result()
    assert result["layer_hashes"]["context_hash"] != result["layer_hashes"]["profiled_output_hash"]
    assert result["layer_hashes"]["context_hash"] != result["layer_hashes"]["value_output_hash"]

