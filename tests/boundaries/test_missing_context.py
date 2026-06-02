from __future__ import annotations

from tests.helpers import cody_result, clone_yaml, write_contract


def test_engine_surfaces_context_gap_instead_of_fabricating(tmp_path, paths: dict) -> None:
    surface = clone_yaml(paths["surface"])
    surface["edges"] = []
    empty_surface = write_contract(tmp_path, "empty.surface", surface)
    result = cody_result(surface_path=empty_surface)
    assert "surface graph has no edges" in result["context_gap"]
    assert result["weighted_edge_list"] == []

