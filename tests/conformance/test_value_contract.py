from __future__ import annotations

import pytest

from tests.helpers import cody_result
from kernel.value.loader import load_value
from kernel.value.resolve import resolve_value
from kernel.value.validate import ValueValidationError, validate_value


def test_value_maps_projection_to_customer_metrics(paths: dict) -> None:
    value = load_value(paths["value"])
    output = resolve_value(value, {"first_order_context": {"node_ids": ["sce.customer_value"]}})
    assert "SCE operations" in output["stakeholders"]
    assert output["success_criteria"]


def test_value_output_contains_because() -> None:
    result = cody_result()
    assert result["because_trace"]["value"] == "neara.sce.customer_value"
    assert result["value_resolution"]["narrative"]


def test_value_cannot_override_profile_permissions() -> None:
    result = cody_result()
    assert result["value_resolution"]["action_trigger"] == result["action_recommendation"]
    assert result["value_resolution"]["action_trigger"] != result["profile_id"]


def test_value_does_not_mutate_context() -> None:
    result = cody_result()
    assert result["layer_hashes"]["context_hash"]
    assert result["layer_hashes"]["value_output_hash"] != result["layer_hashes"]["context_hash"]


def test_value_interpretation_hash_is_stable() -> None:
    assert cody_result()["layer_hashes"]["value_output_hash"] == cody_result()["layer_hashes"]["value_output_hash"]


def test_value_explains_significance_not_authority(paths: dict) -> None:
    value = load_value(paths["value"])
    assert "action_authority" not in value.metadata
    assert "authority" not in value_to_plain_dict(value)

    bad_value = value.__class__(
        id="bad.value",
        stakeholders=[],
        success_criteria=["success"],
        business_consequence="none",
        risk_opportunity="none",
        why_relation="person_to_person",
        action_trigger="act",
    )
    with pytest.raises(ValueValidationError, match="stakeholders"):
        validate_value(bad_value)


def value_to_plain_dict(value) -> str:
    return " ".join(str(part) for part in value.__dict__.values()).lower()

