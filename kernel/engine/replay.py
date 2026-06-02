from __future__ import annotations

from pathlib import Path
from typing import Any

from kernel.engine.hashing import ENGINE_VERSION, checksum_map, hash_data


def replay_payload(
    *,
    checksums: dict[str, str | None],
    runtime_input: dict[str, Any] | None,
    canonical_weighted_graph: dict[str, Any],
    result_without_hash: dict[str, Any],
) -> dict[str, Any]:
    return {
        "engine_version": ENGINE_VERSION,
        "checksums": checksums,
        "runtime_input": runtime_input or {},
        "canonical_weighted_graph": canonical_weighted_graph,
        "result": result_without_hash,
    }


def build_replay_hash(
    *,
    paths: dict[str, Path | None],
    runtime_input: dict[str, Any] | None,
    canonical_weighted_graph: dict[str, Any],
    result_without_hash: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    checksums = checksum_map(paths)
    payload = replay_payload(
        checksums=checksums,
        runtime_input=runtime_input,
        canonical_weighted_graph=canonical_weighted_graph,
        result_without_hash=result_without_hash,
    )
    return hash_data(payload), payload

