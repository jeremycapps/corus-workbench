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
    assert len(store.read_entries()) == 26
    assert store.verify_chain()["valid"] is True


def test_ingest_preserves_source_and_claim_metadata(tmp_path: Path) -> None:
    run_dir = _ingest(tmp_path)
    payloads = _payloads_by_target(run_dir)

    source = payloads["source.sce_2025_wmp_update"]
    assert source["data"]["authority"] == "public_sce_regulatory_filing"
    assert source["data"]["source_status"] == "public_pdf"
    assert "public_source" in source["data"]["trust_status"]
    assert source["data"]["url"].startswith("https://")

    neara_source = payloads["source.neara_risk_impact_scoring"]
    assert neara_source["data"]["authority"] == "public_neara_marketing"
    assert "public_source" in neara_source["data"]["trust_status"]

    source_context = payloads["bundle.sce_significance_translation.source_context"]
    assert source_context["type"] == "source_context"
    assert "source.sce_2025_wmp_update" in source_context["inputs"]
    assert source_context["data"]["primary_source_ids"]

    claim = _payload_for(run_dir, target="claim.sce.watch_points_added", act="interpret")
    assert claim["data"]["source"] == "source.demo_model_output"
    assert "source.sce_2025_wmp_update" in claim["data"]["context_sources"]
    assert "demo_synthetic" in claim["data"]["trust_status"]
    assert claim["data"]["trust_note"]

    rejected = _payload_for(run_dir, target="claim.sce.unsupported_cost_assumption", act="interpret")
    assert "source.neara_pole_replacement_case_study" in rejected["data"]["context_sources"]
    assert "source_authority_missing" in rejected["data"]["trust_status"]


def test_ingested_run_supports_read(tmp_path: Path) -> None:
    run_dir = _ingest(tmp_path)
    result = read_active_context(LedgerStore(run_dir))

    assert "claim.sce.watch_points_added" in {item["id"] for item in result["included"]}
    assert "claim.sce.unsupported_cost_assumption" in {item["id"] for item in result["excluded"]}
    assert "claim.customer.needs_significance" in {item["id"] for item in result["included"]}
    assert "claim.customer.unsupported_specific_cost" in {item["id"] for item in result["excluded"]}
    assert "profile.neara_implementation" in {item["id"] for item in result["declared_contracts"]}


def test_ingested_run_supports_audit(tmp_path: Path) -> None:
    run_dir = _ingest(tmp_path)
    store = LedgerStore(run_dir)

    assert audit_target(store, "claim.sce.watch_points_added")["valid"] is True
    assert audit_target(store, "claim.sce.unsupported_cost_assumption")["valid"] is True
    assert audit_target(store, "claim.customer.needs_significance")["valid"] is True
    assert audit_target(store, "claim.customer.unsupported_specific_cost")["valid"] is True
    assert audit_target(store, "output.implementation_context_trace")["valid"] is True
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
    assert "source.sce_2025_wmp_update was added" in output
    assert "source.neara_risk_impact_scoring was added" in output
    assert "claim.customer.needs_significance was interpreted" in output
    assert "claim.customer.unsupported_specific_cost was rejected" in output
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

    assert result["bundle_id"] == "bundle.sce_significance_translation"
    assert result["ledger"]["valid"] is True
    assert result["entries_written"] == 26
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


def _payloads_by_target(run_dir: Path) -> dict[str, dict]:
    store = LedgerStore(run_dir)
    return {
        payload["to"]: payload
        for entry in store.read_entries()
        for payload in [store.read_payload(entry)]
    }


def _payload_for(run_dir: Path, target: str, act: str) -> dict:
    store = LedgerStore(run_dir)
    for entry in store.read_entries():
        payload = store.read_payload(entry)
        if payload["to"] == target and payload["act"] == act:
            return payload
    raise AssertionError(f"missing payload target={target} act={act}")
