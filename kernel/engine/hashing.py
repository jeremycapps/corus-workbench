from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Any

from kernel.engine.canonicalize import canonical_json
from kernel.verify.hash import read_yaml, sha256_file


ENGINE_VERSION = "corus-engine-0.1.0"


def hash_data(data: Any) -> str:
    return sha256(canonical_json(data).encode("utf-8")).hexdigest()


def checksum_map(paths: dict[str, Path | None]) -> dict[str, str | None]:
    checksums: dict[str, str | None] = {}
    for name, path in sorted(paths.items()):
        if path is None:
            checksums[name] = None
        elif path.suffix in {".domain", ".surface", ".lens", ".profile", ".value"}:
            checksums[name] = hash_data(read_yaml(path))
        else:
            checksums[name] = sha256_file(path)
    return checksums
