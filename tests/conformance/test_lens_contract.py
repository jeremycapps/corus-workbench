from __future__ import annotations

from copy import deepcopy

import pytest

from tests.helpers import cody_result, clone_yaml, write_contract
from kernel.domain.loader import domain_to_data, load_domain
from kernel.lens.loader import load_lens
from kernel.lens.validate import LensValidationError, validate_lens
from kernel.lens.weighting import apply_lens
from kernel.surface.loader import load_surface, surface_to_data


def test_lens_entrypoint_exists_in_surface(paths: dict) -> None:
    result = cody_result()
    assert result["weighted_node_list"][0]["id"] in result["domain_node_ids_used"]


def test_lens_weights_reference_existing_graph_elements(tmp_path, paths: dict) -> None:
    validate_lens(load_lens(paths["lens"]), load_domain(paths["domain"]))

    bad_data = clone_yaml(paths["lens"])
    bad_data["edge_weight_rules"][0]["match"] = "not_an_edge_type"
    bad = write_contract(tmp_path, "lens_bad_edge.lens", bad_data)
    with pytest.raises(LensValidationError, match="nonexistent edge type"):
        validate_lens(load_lens(bad), load_domain(paths["domain"]))


def test_lens_does_not_mutate_domain_or_surface(paths: dict) -> None:
    domain = load_domain(paths["domain"])
    surface = load_surface(paths["surface"])
    before_domain = deepcopy(domain_to_data(domain))
    before_surface = deepcopy(surface_to_data(surface))
    apply_lens(load_lens(paths["lens"]), surface, domain)
    assert domain_to_data(domain) == before_domain
    assert surface_to_data(surface) == before_surface


def test_lens_change_changes_projection_not_context(tmp_path, paths: dict) -> None:
    baseline = cody_result()
    data = clone_yaml(paths["lens"])
    data["node_weight_rules"][0]["weight"] = 9.0
    changed_lens = write_contract(tmp_path, "changed.lens", data)
    changed = cody_result(lens_paths=[changed_lens])
    assert changed["layer_hashes"]["context_hash"] == baseline["layer_hashes"]["context_hash"]
    assert changed["layer_hashes"]["projection_hash"] != baseline["layer_hashes"]["projection_hash"]


def test_two_lenses_create_distinct_projections_from_same_context(tmp_path, paths: dict) -> None:
    data = clone_yaml(paths["lens"])
    data["id"] = "customer_value_first"
    data["name"] = "customer_value_first"
    data["node_weight_rules"] = [{"match": "customer_value", "weight": 10.0}]
    alternate_lens = write_contract(tmp_path, "customer_value_first.lens", data)
    baseline = cody_result()
    alternate = cody_result(lens_paths=[alternate_lens], profile_path=_profile_for_lens(tmp_path, paths, "customer_value_first"))
    assert alternate["layer_hashes"]["context_hash"] == baseline["layer_hashes"]["context_hash"]
    assert alternate["layer_hashes"]["projection_hash"] != baseline["layer_hashes"]["projection_hash"]


def test_lens_warps_view_not_world(tmp_path, paths: dict) -> None:
    baseline_ids = set(cody_result()["domain_node_ids_used"])
    data = clone_yaml(paths["lens"])
    data["node_weight_rules"][0]["weight"] = 0.1
    changed_lens = write_contract(tmp_path, "view_only.lens", data)
    changed_ids = set(cody_result(lens_paths=[changed_lens])["domain_node_ids_used"])
    assert changed_ids == baseline_ids


def _profile_for_lens(tmp_path, paths: dict, lens_id: str):
    profile = clone_yaml(paths["profile"])
    profile["lens_ref"] = lens_id
    return write_contract(tmp_path, f"{lens_id}.profile", profile)
