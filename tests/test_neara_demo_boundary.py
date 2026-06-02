from __future__ import annotations

from pathlib import Path

from kernel.verify.hash import read_yaml
from tests.test_playground_cli import SCE, run_corus


ROOT = Path(__file__).resolve().parents[1]
TRUST_MAP = SCE / "trust_map.yaml"
DOC = ROOT / "docs" / "demo" / "neara_value_translation_path.md"
WORK_PACKET_CONTRACT = ROOT / "docs" / "contracts" / "work_packet_output.md"


def _trust_map() -> dict:
    return read_yaml(TRUST_MAP)


def _file_entry(path: str) -> dict:
    entries = {entry["path"]: entry for entry in _trust_map()["files"]}
    return entries[path]


def _claim_entry(claim_id: str) -> dict:
    entries = {entry["id"]: entry for entry in _trust_map()["claims"]}
    return entries[claim_id]


def test_neara_model_output_is_central_to_value_translation_demo() -> None:
    entry = _file_entry("bundles/sce_vegetation/artifacts/demo_model_output.json")
    assert entry["classification"] == "central_demo_path"
    assert "demo_synthetic" in entry["trust_status"]
    assert "source_authority_missing" in entry["trust_status"]


def test_sce_translation_contracts_are_central_demo_path() -> None:
    central_files = [
        "tests/fixtures/sce_vegetation/sce.domain",
        "tests/fixtures/sce_vegetation/sce.surface",
        "tests/fixtures/sce_vegetation/vegetation_ops.lens",
        "tests/fixtures/sce_vegetation/sce_grid_ops.profile",
        "tests/fixtures/sce_vegetation/neara_value_architect.profile",
        "tests/fixtures/sce_vegetation/sce_customer.value",
        "tests/fixtures/sce_vegetation/sce.evidence",
    ]
    for path in central_files:
        assert _file_entry(path)["classification"] == "central_demo_path"


def test_raw_source_and_connector_surfaces_are_not_central_demo_path() -> None:
    non_central_files = [
        "kernel/connect/arcgis.py",
        "kernel/connect/geo.py",
        "kernel/connect/laz.py",
        "kernel/connect/pdf.py",
        "tests/fixtures/eaton_poc/sources/eaton_perimeter.geojson",
        "sources/eaton_fire/incident/eaton_perimeter_20250121.geojson",
    ]
    for path in non_central_files:
        assert _file_entry(path)["classification"] != "central_demo_path"


def test_value_and_evidence_assumptions_have_explicit_trust_status() -> None:
    for path in [
        "tests/fixtures/sce_vegetation/sce_customer.value",
        "tests/fixtures/sce_vegetation/sce.evidence",
    ]:
        statuses = set(_file_entry(path)["trust_status"])
        assert statuses & {"demo_synthetic", "source_labeled", "source_authority_missing"}

    for claim_id in [
        "claim.sce.watch_points_added",
        "claim.sce.unsupported_cost_assumption",
        "fact.cost.validation_exposure",
        "fact.cost.customer_value",
    ]:
        statuses = set(_claim_entry(claim_id)["trust_status"])
        assert statuses & {"demo_synthetic", "source_labeled", "source_authority_missing"}


def test_demo_docs_and_trust_map_name_value_translation_boundary() -> None:
    doc_text = DOC.read_text(encoding="utf-8").lower()
    trust_text = TRUST_MAP.read_text(encoding="utf-8").lower()
    assert "value translation" in doc_text
    assert "value translation" in trust_text
    assert "does not recreate neara" in doc_text


def test_existing_validate_cli_behavior_still_passes() -> None:
    result = run_corus("validate", str(SCE))
    assert result["timpo"]["valid"] is True
    assert result["domain"]["valid"] is True
    assert result["surface"]["valid"] is True
    assert result["value"]["valid"] is True
    assert result["evidence"]["valid"] is True


def test_current_work_packet_output_matches_minimal_contract_sections() -> None:
    contract_text = WORK_PACKET_CONTRACT.read_text(encoding="utf-8")
    assert "input model delta" in contract_text
    assert "customer value interpretation" in contract_text
    assert "profile permissions" in contract_text

    result = run_corus("agent-run", str(SCE), "--profile", "sce_grid_ops", "--lens", "vegetation_ops")
    agent_run = result["agent_run"]

    assert agent_run["path_summary"]["start"] == "fact.watch_points.added"
    assert agent_run["path_summary"]["domain_path"]
    assert agent_run["path_summary"]["surface_path"]
    assert agent_run["path_summary"]["value_metrics"]
    assert agent_run["because"]
    assert agent_run["source_hashes"]
    assert agent_run["audit_event_hash"]
    assert agent_run["audit_event"]
    assert agent_run["action_result"]["proposed_action"] == "generate_work_packet"
    assert agent_run["action_result"]["permission_result"] == "allowed"
    assert agent_run["action_result"]["restricted_actions"]
