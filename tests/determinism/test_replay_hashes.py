from __future__ import annotations

from tests.helpers import GOLDEN_REPLAY_HASH, cody_result


def test_same_inputs_same_replay_hash() -> None:
    assert cody_result()["replay_hash"] == cody_result()["replay_hash"] == GOLDEN_REPLAY_HASH


def test_replay_metadata_contains_layer_hashes() -> None:
    result = cody_result()
    assert result["layer_hashes"]["context_hash"]
    assert result["layer_hashes"]["projection_hash"]
    assert result["layer_hashes"]["value_output_hash"]

