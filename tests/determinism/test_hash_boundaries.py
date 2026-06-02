from __future__ import annotations

import pytest

from tests.helpers import cody_result, clone_yaml, contract_hash, write_contract


def test_reordered_inputs_same_canonical_hash(tmp_path, paths: dict) -> None:
    surface = clone_yaml(paths["surface"])
    surface["nodes"] = list(reversed(surface["nodes"]))
    surface["edges"] = list(reversed(surface["edges"]))
    reordered = write_contract(tmp_path, "reordered.surface", surface)
    assert contract_hash(reordered) == contract_hash(paths["surface"])
    assert cody_result(surface_path=reordered)["replay_hash"] == cody_result()["replay_hash"]


def test_meaningful_domain_change_changes_context_hash(tmp_path, paths: dict) -> None:
    domain = clone_yaml(paths["domain"])
    domain["nodes"][0]["label"] = "Changed domain meaning"
    changed_domain = write_contract(tmp_path, "changed.domain", domain)
    changed = cody_result(domain_path=changed_domain)
    assert changed["layer_hashes"]["domain_hash"] != cody_result()["layer_hashes"]["domain_hash"]
    assert changed["layer_hashes"]["context_hash"] != cody_result()["layer_hashes"]["context_hash"]


def test_surface_change_changes_context_hash(tmp_path, paths: dict) -> None:
    surface = clone_yaml(paths["surface"])
    surface["edges"][0]["label"] = "Changed relationship semantics."
    changed_surface = write_contract(tmp_path, "changed.surface", surface)
    changed = cody_result(surface_path=changed_surface)
    baseline = cody_result()
    assert changed["layer_hashes"]["surface_hash"] != baseline["layer_hashes"]["surface_hash"]
    assert changed["layer_hashes"]["context_hash"] != baseline["layer_hashes"]["context_hash"]


def test_lens_change_changes_projection_hash_only(tmp_path, paths: dict) -> None:
    lens = clone_yaml(paths["lens"])
    lens["node_weight_rules"][0]["weight"] = 8.0
    changed_lens = write_contract(tmp_path, "changed.lens", lens)
    changed = cody_result(lens_paths=[changed_lens])
    baseline = cody_result()
    assert changed["layer_hashes"]["context_hash"] == baseline["layer_hashes"]["context_hash"]
    assert changed["layer_hashes"]["projection_hash"] != baseline["layer_hashes"]["projection_hash"]


def test_profile_change_changes_profiled_output_hash_only(tmp_path, paths: dict) -> None:
    profile = clone_yaml(paths["profile"])
    profile["core_question"] = "Can this delta become a customer success pattern?"
    changed_profile = write_contract(tmp_path, "changed.profile", profile)
    changed = cody_result(profile_path=changed_profile)
    baseline = cody_result()
    assert changed["layer_hashes"]["context_hash"] == baseline["layer_hashes"]["context_hash"]
    assert changed["layer_hashes"]["projection_hash"] == baseline["layer_hashes"]["projection_hash"]
    assert changed["layer_hashes"]["profiled_output_hash"] != baseline["layer_hashes"]["profiled_output_hash"]


def test_value_change_changes_value_hash_only(tmp_path, paths: dict) -> None:
    value = clone_yaml(paths["value"])
    value["success_criteria"].append("Additional success criterion.")
    changed_value = write_contract(tmp_path, "changed.value", value)
    changed = cody_result(value_path=changed_value)
    baseline = cody_result()
    assert changed["layer_hashes"]["context_hash"] == baseline["layer_hashes"]["context_hash"]
    assert changed["layer_hashes"]["projection_hash"] == baseline["layer_hashes"]["projection_hash"]
    assert changed["layer_hashes"]["value_output_hash"] != baseline["layer_hashes"]["value_output_hash"]


@pytest.mark.xfail(reason="context reconstruction does not yet ingest Timpo ledgers as runtime inputs")
def test_timpo_observation_change_changes_context_hash(tmp_path, paths: dict) -> None:
    baseline = cody_result()
    changed = cody_result(runtime_input={"timpo_observations": [{"timpo": 1, "when": 2, "where": 3}]})
    assert changed["layer_hashes"]["context_hash"] != baseline["layer_hashes"]["context_hash"]
