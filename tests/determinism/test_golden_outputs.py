from __future__ import annotations

from tests.helpers import cody_result


def _golden(name: str) -> str:
    from pathlib import Path

    return (Path(__file__).resolve().parents[1] / "golden" / name).read_text(encoding="utf-8").strip()


def test_sce_context_matches_golden() -> None:
    assert cody_result()["layer_hashes"]["context_hash"] == _golden("sce_vegetation.context.hash")


def test_sce_projection_matches_golden() -> None:
    assert cody_result()["layer_hashes"]["projection_hash"] == _golden("sce_vegetation.projection.hash")


def test_sce_value_output_matches_golden() -> None:
    assert cody_result()["layer_hashes"]["value_output_hash"] == _golden("sce_vegetation.value.hash")


def test_sce_replay_matches_golden() -> None:
    assert cody_result()["replay_hash"] == _golden("sce_vegetation.replay.hash")

