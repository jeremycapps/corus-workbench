from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from kernel.audit import audit_target
from kernel.ledger.read import read_active_context
from kernel.ledger.store import LedgerStore


ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "bundles" / "sce_vegetation"


def test_ingest_creates_ledger(tmp_path: Path) -> None:
    run_dir = _ingest(tmp_path)
    store = LedgerStore(run_dir)

    assert (run_dir / "ledger" / "entries").exists()
    assert (run_dir / "ledger" / "payloads").exists()
    assert len(store.read_entries()) == 12
    assert store.verify_chain()["valid"] is True


def test_ingested_run_supports_read(tmp_path: Path) -> None:
    run_dir = _ingest(tmp_path)
    result = read_active_context(LedgerStore(run_dir))

    assert "claim.sce.watch_points_added" in {item["id"] for item in result["included"]}
    assert "claim.sce.unsupported_cost_assumption" in {item["id"] for item in result["excluded"]}


def test_ingested_run_supports_audit(tmp_path: Path) -> None:
    run_dir = _ingest(tmp_path)
    store = LedgerStore(run_dir)

    assert audit_target(store, "claim.sce.watch_points_added")["valid"] is True
    assert audit_target(store, "claim.sce.unsupported_cost_assumption")["valid"] is True
    assert audit_target(store, "output.sce_grid_ops.work_packet")["valid"] is True


def test_cli_ingest_summary(tmp_path: Path) -> None:
    run_dir = tmp_path / "sce_vegetation"
    completed = subprocess.run(
        [sys.executable, "-m", "corus", "ingest", str(BUNDLE), "--out", str(run_dir)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    output = completed.stdout

    assert "Intake Bundle" in output
    assert "Ledger" in output
    assert "valid: true" in output
    assert "source.demo_model_output was added" in output
    assert "claim.sce.watch_points_added was interpreted" in output
    assert "claim.sce.watch_points_added was validated" in output
    assert "claim.sce.unsupported_cost_assumption was rejected" in output
    assert "output.sce_grid_ops.work_packet was generated" in output


def test_cli_ingest_json_summary(tmp_path: Path) -> None:
    run_dir = tmp_path / "sce_vegetation"
    completed = subprocess.run(
        [sys.executable, "-m", "corus", "ingest", str(BUNDLE), "--out", str(run_dir), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    result = json.loads(completed.stdout)

    assert result["bundle_id"] == "bundle.sce_vegetation"
    assert result["ledger"]["valid"] is True
    assert result["entries_written"] == 12
    assert result["written_payloads"]


def _ingest(tmp_path: Path) -> Path:
    run_dir = tmp_path / "sce_vegetation"
    subprocess.run(
        [sys.executable, "-m", "corus", "ingest", str(BUNDLE), "--out", str(run_dir), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return run_dir
