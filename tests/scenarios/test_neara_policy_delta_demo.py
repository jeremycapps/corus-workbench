from __future__ import annotations

from tests.helpers import cody_result


def test_neara_policy_delta_demo_resolves_cody_question() -> None:
    result = cody_result()
    assert result["core_question"] == "Can this Neara model delta become a reusable product/value pattern?"
    assert result["lens_id"] == "model_delta_to_product_pattern"


def test_neara_policy_delta_demo_has_customer_facing_action() -> None:
    result = cody_result()
    assert result["action_recommendation"] == "Recommend productizing the model-delta-to-customer-value translation pattern."

