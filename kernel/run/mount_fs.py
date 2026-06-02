from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    current = Path.cwd().resolve()
    if (current / "kernel").exists() and (current / "fs").exists():
        return current
    for parent in current.parents:
        if (parent / "kernel").exists() and (parent / "fs").exists():
            return parent
    return current


def mount_fs(root: Path | None = None) -> Path:
    root = root or project_root()
    required = [
        "timpo/src",
        "timpo/tests",
        "kernel/transform",
        "kernel/engine",
        "kernel/domain",
        "kernel/surface",
        "kernel/lens",
        "kernel/profile",
        "kernel/value",
        "kernel/fixtures/neara_sce",
        "kernel/run",
        "kernel/connect",
        "kernel/verify",
        "kernel/command",
        "fs/01_protocols",
        "fs/02_programs",
        "fs/03_processes/runs",
        "fs/04_evidence",
        "fs/04_evidence/ledgers",
    ]
    for item in required:
        (root / item).mkdir(parents=True, exist_ok=True)
    return root / "fs"
