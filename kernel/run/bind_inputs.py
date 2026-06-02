from __future__ import annotations

from pathlib import Path
from typing import Any

from kernel.verify.hash import read_yaml


def load_bindings(root: Path, program: dict[str, Any]) -> dict[str, Any]:
    bindings: dict[str, Any] = {}
    for group_name, group in program.get("bindings", {}).items():
        bindings[group_name] = {}
        for key, value in group.items():
            path = root / value
            document = read_yaml(path)
            document["_path"] = value
            bindings[group_name][key] = document
    return bindings
