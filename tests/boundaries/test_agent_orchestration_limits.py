from __future__ import annotations

from tests.helpers import cody_result


def test_sce_agent_cannot_dispatch_without_permission() -> None:
    result = cody_result()
    assert result["action_recommendation"].startswith("Recommend")
    assert "dispatch" not in result["action_recommendation"].lower()

