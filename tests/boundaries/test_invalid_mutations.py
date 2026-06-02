from __future__ import annotations

import pytest

from tests.helpers import clone_yaml, write_contract
from kernel.domain.loader import load_domain
from kernel.lens.loader import load_lens
from kernel.lens.validate import LensValidationError, validate_lens
from kernel.surface.loader import load_surface
from kernel.surface.validate import SurfaceValidationError, validate_surface


def test_surface_edge_addition_does_not_create_domain_node(tmp_path, paths: dict) -> None:
    surface = clone_yaml(paths["surface"])
    surface["edges"].append(
        {
            "id": "edge.to.invented",
            "from_node": "neara.model_delta",
            "to_node": "invented.meaning",
            "type": "connects",
            "label": "Cannot create meaning",
        }
    )
    bad = write_contract(tmp_path, "invented.surface", surface)
    with pytest.raises(SurfaceValidationError, match="missing"):
        validate_surface(load_surface(bad), load_domain(paths["domain"]))


def test_lens_cannot_reference_unknown_node_type(tmp_path, paths: dict) -> None:
    lens = clone_yaml(paths["lens"])
    lens["node_weight_rules"].append({"match": "invented_type", "weight": 4})
    bad = write_contract(tmp_path, "invented.lens", lens)
    with pytest.raises(LensValidationError, match="nonexistent node type"):
        validate_lens(load_lens(bad), load_domain(paths["domain"]))

