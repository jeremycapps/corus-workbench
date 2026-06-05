from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Any

import yaml


SEMANTIC_SUFFIXES = {
    ".domain",
    ".surface",
    ".profile",
    ".lens",
    ".value",
    ".evidence",
    ".program",
    ".process",
    ".protocol",
    ".source",
    ".extent",
    ".validation",
    ".input",
    ".output",
    ".schema",
    ".hash",
    ".timpos",
    ".ledger",
    ".sources",
    ".context",
    ".team",
    ".roles",
    ".relations",
    ".artifacts",
}


def sha256_text(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_yaml(path: Path) -> Any:
    if path.suffix not in SEMANTIC_SUFFIXES and path.suffix not in {".yaml", ".yml"}:
        raise ValueError(f"Unsupported semantic extension: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def write_yaml(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False, allow_unicode=False)
