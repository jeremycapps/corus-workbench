from __future__ import annotations

from pathlib import Path
from typing import Any

from kernel.verify.hash import read_yaml


def load_program(root: Path, program_name: str) -> dict[str, Any]:
    path = root / "fs" / "02_programs" / f"{program_name}.program"
    if not path.exists():
        raise FileNotFoundError(f"Unknown program: {program_name}")
    program = read_yaml(path)
    program["_path"] = str(path.relative_to(root))
    return program
