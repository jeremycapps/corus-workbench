from __future__ import annotations

import pytest

from tests.helpers import cody_result, clone_yaml, write_contract
from kernel.domain.loader import domain_to_data, load_domain
from kernel.engine.runtime import resolve_context
from kernel.profile.initiate import InitiationError
from kernel.profile.loader import load_profile
from kernel.profile.validate import ProfileValidationError, validate_profile
from kernel.surface.loader import load_surface, surface_to_data


def test_profile_has_core_question(paths: dict) -> None:
    profile = load_profile(paths["profile"])
    assert profile.core_question
    validate_profile(profile)


def test_profile_declares_allowed_lenses(paths: dict) -> None:
    assert load_profile(paths["profile"]).lens_ref == "model_delta_to_product_pattern"


def test_profile_declares_action_permissions(paths: dict) -> None:
    assert load_profile(paths["profile"]).action_authority == "recommend_productization_pattern"


def test_only_profile_can_initiate_run(paths: dict) -> None:
    with pytest.raises(InitiationError, match="requires a profile"):
        resolve_context(
            profile_path=None,
            surface_path=paths["surface"],
            domain_path=paths["domain"],
            lens_paths=[paths["lens"]],
            value_path=paths["value"],
        )


def test_profile_initiation_creates_trace() -> None:
    result = cody_result()
    assert result["because_trace"]["profile"] == "neara.cody_yakimoff"
    assert result["core_question"] in result["replay_metadata"]["result"]["core_question"]


def test_profile_cannot_mutate_domain_or_surface(paths: dict) -> None:
    domain = load_domain(paths["domain"])
    surface = load_surface(paths["surface"])
    before_domain = domain_to_data(domain)
    before_surface = surface_to_data(surface)
    cody_result()
    assert domain_to_data(domain) == before_domain
    assert surface_to_data(surface) == before_surface


def test_profile_is_the_agency_boundary(tmp_path, paths: dict) -> None:
    data = clone_yaml(paths["profile"])
    data["action_authority"] = ""
    bad = write_contract(tmp_path, "no_authority.profile", data)
    profile = load_profile(bad)
    with pytest.raises(ProfileValidationError, match="action authority"):
        validate_profile(profile)

