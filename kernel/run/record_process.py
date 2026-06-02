from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from kernel.verify.hash import sha256_file, write_yaml


def now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def record_process(
    root: Path,
    program: dict[str, Any],
    inputs: dict[str, Any],
    outputs: dict[str, Any],
    process_contracts: list[dict[str, Any]],
) -> Path:
    run_dir = root / "fs" / "03_processes" / "runs" / f"{now_stamp()}-{program['program']}.process"
    run_dir.mkdir(parents=True, exist_ok=False)

    write_yaml(
        run_dir / "inputs.input",
        {"input": "program-run-inputs", "version": "1.0.0", "type": "program_run_inputs", "data": inputs},
    )
    write_yaml(run_dir / "outputs.output", {"output": "program-run-outputs", "version": "1.0.0", "data": outputs})
    manifest = {
        "process": "program-run",
        "version": "1.0.0",
        "program": program["program"],
        "started_at": run_dir.name.split("-", 1)[0],
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "processes": [contract["process"] for contract in process_contracts],
        "status": "success",
    }
    write_yaml(run_dir / "manifest.process", manifest)

    hashes = {
        path.name: sha256_file(path)
        for path in [
            run_dir / "manifest.process",
            run_dir / "inputs.input",
            run_dir / "outputs.output",
        ]
    }
    write_yaml(run_dir / "hashes.hash", {"hash": "program-run-hashes", "version": "1.0.0", "sha256": hashes})
    (run_dir / "logs.txt").write_text("Program run completed successfully.\n", encoding="utf-8")
    return run_dir
