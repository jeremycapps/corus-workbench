from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from kernel.engine.hashing import hash_data
from kernel.engine.runtime import resolve_context
from kernel.verify.hash import read_yaml, write_yaml


ROOT = Path(__file__).resolve().parents[1]
ENGINE_FIXTURE = ROOT / "kernel" / "fixtures" / "neara_sce"
DOMAIN = ENGINE_FIXTURE / "sce.domain"
SURFACE = ENGINE_FIXTURE / "sce_value_translation.surface"
LENS = ENGINE_FIXTURE / "model_delta_to_product_pattern.lens"
PROFILE = ENGINE_FIXTURE / "cody_yakimoff.profile"
VALUE = ENGINE_FIXTURE / "sce_customer_value.value"
TIMPOS = ROOT / "fs" / "04_evidence" / "inputs" / "sce" / "vegetation-observations.timpos"

GOLDEN_REPLAY_HASH = "d136703f54f216c09384d215b28074b9c4225dc504241f2ffeb8d69636c757b1"


def cody_result(**overrides: Any) -> dict[str, Any]:
    params = {
        "profile_path": PROFILE,
        "surface_path": SURFACE,
        "domain_path": DOMAIN,
        "lens_paths": [LENS],
        "value_path": VALUE,
    }
    params.update(overrides)
    return resolve_context(**params)


def clone_yaml(path: Path) -> dict[str, Any]:
    return deepcopy(read_yaml(path))


def write_contract(tmp_path: Path, name: str, data: dict[str, Any]) -> Path:
    path = tmp_path / name
    write_yaml(path, data)
    return path


def contract_hash(path: Path) -> str:
    return hash_data(read_yaml(path))

