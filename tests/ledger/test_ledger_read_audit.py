from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from kernel.audit import audit_target
from kernel.audit.admissibility import resolve_claim_admissibility
from kernel.audit.replay import projection_fingerprint
from kernel.ledger.read import read_active_context
from kernel.ledger.store import LEDGER_FIELDS, PAYLOAD_ACTS, LedgerStore, LedgerVerificationError
from kernel.verify.hash import read_yaml, write_yaml


ROOT = Path(__file__).resolve().parents[2]
SCE = ROOT / "tests" / "fixtures" / "sce_vegetation"


def run_corus(*args: str) -> dict:
    completed = subprocess.run(
        [sys.executable, "-m", "corus", *args, "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(completed.stdout)


def test_ledger_entries_are_dumb() -> None:
    store = LedgerStore(SCE)
    for entry in store.read_entries():
        assert set(entry) == LEDGER_FIELDS
        assert "from" not in entry
        assert "act" not in entry
        assert "type" not in entry
        assert "to" not in entry
        assert "profile" not in entry
        assert "domain" not in entry
        assert "value" not in entry


def test_payloads_contain_semantic_event_fields() -> None:
    store = LedgerStore(SCE)
    for entry in store.read_entries():
        payload = store.read_payload(entry)
        assert {"from", "act", "type", "to"} <= set(payload)
        assert payload["act"] in PAYLOAD_ACTS


def test_payload_hash_verification_fails_when_payload_changes(tmp_path: Path) -> None:
    fixture = _copy_fixture(tmp_path)
    payload_path = fixture / "ledger" / "payloads" / "payload.0002.yaml"
    payload = read_yaml(payload_path)
    payload["data"]["value"] = 73
    write_yaml(payload_path, payload)

    with pytest.raises(LedgerVerificationError, match="payload hash mismatch"):
        LedgerStore(fixture).verify_chain()


def test_prev_hash_chain_verification_fails_when_entry_changes(tmp_path: Path) -> None:
    fixture = _copy_fixture(tmp_path)
    entry_path = fixture / "ledger" / "entries" / "ledger.0002.yaml"
    entry = read_yaml(entry_path)
    entry["prev_hash"] = "broken"
    write_yaml(entry_path, entry)

    with pytest.raises(LedgerVerificationError, match="prev_hash mismatch"):
        LedgerStore(fixture).verify_chain()


def test_rejected_candidate_remains_in_ledger_but_is_excluded_from_read() -> None:
    read_result = read_active_context(LedgerStore(SCE))
    excluded = {item["id"]: item for item in read_result["excluded"]}

    assert _payload_exists("claim.sce.unsupported_cost_assumption")
    assert excluded["claim.sce.unsupported_cost_assumption"]["reason"] == "admissible false"


def test_interpreted_candidate_is_not_active_by_default(tmp_path: Path) -> None:
    fixture = _copy_fixture(tmp_path)
    store = LedgerStore(fixture)
    store.write(
        {
            "from": "corus.interpreter",
            "act": "interpret",
            "type": "candidate_claim",
            "to": "claim.sce.unvalidated_candidate",
            "inputs": ["source.demo_model_output"],
            "data": {
                "claim": "This candidate has not been admitted.",
                "status": "candidate",
            },
        },
        timpo="11612132757493222933514833726911676416",
    )

    read_result = read_active_context(store)
    excluded = {item["id"]: item for item in read_result["excluded"]}

    assert "claim.sce.unvalidated_candidate" not in {item["id"] for item in read_result["included"]}
    assert excluded["claim.sce.unvalidated_candidate"]["reason"] == "unvalidated"


def test_validated_candidate_enters_read_context() -> None:
    read_result = read_active_context(LedgerStore(SCE))
    included = {item["id"]: item for item in read_result["included"]}

    assert _payload_exists("claim.sce.watch_points_added")
    assert included["claim.sce.watch_points_added"]["reason"] == "admissible true"


def test_audit_target_resolver_finds_claim_interpretation_and_validation() -> None:
    proof = audit_target(LedgerStore(SCE), "claim.sce.watch_points_added")
    acts = {reference["payload_act"] for reference in proof["ledger_references"]}

    assert proof["checks"]["target_resolver"]["status"] == "pass"
    assert {"interpret", "validate"} <= acts
    assert proof["status"] == "included"
    assert proof["target_status"]["history"] == "found"
    assert proof["target_status"]["active_context"] == "included"
    assert proof["checks"]["admissibility"]["status"] == "pass"
    assert proof["valid"] is True


def test_audit_explains_included_and_excluded_claims() -> None:
    proof = audit_target(LedgerStore(SCE), "claim.sce.unsupported_cost_assumption")

    assert proof["status"] == "excluded"
    assert proof["reason"] == "admissible false"
    assert proof["target_status"]["history"] == "found"
    assert proof["target_status"]["active_context"] == "excluded"
    assert proof["target_status"]["reason"] == "admissible false"
    assert proof["checks"]["admissibility"]["status"] == "pass"
    assert any(item["id"] == "claim.sce.watch_points_added" for item in proof["included"])
    assert any(item["id"] == "claim.sce.unsupported_cost_assumption" for item in proof["excluded"])


def test_read_cli_includes_validated_claim_and_excludes_rejected_claim() -> None:
    result = run_corus("read", str(SCE), "--profile", "sce_grid_ops", "--lens", "vegetation_ops")

    assert result["architecture"]["invariant"] == "A claim can exist in the ledger without existing in active context."
    assert any(item["id"] == "claim.sce.watch_points_added" for item in result["included"])
    assert any(
        item["id"] == "claim.sce.unsupported_cost_assumption"
        and item["reason"] == "admissible false"
        for item in result["excluded"]
    )


def test_audit_cli_replays_read_but_surfaces_placeholder_gaps() -> None:
    proof = run_corus(
        "audit",
        str(SCE),
        "--target",
        "output.sce_grid_ops.work_packet",
        "--profile",
        "sce_grid_ops",
        "--lens",
        "vegetation_ops",
    )

    assert proof["valid"] is False
    assert proof["checks"]["target_resolver"]["status"] == "pass"
    assert proof["target"]["type"] == "output"
    assert proof["target_status"]["history"] == "found"
    assert proof["target_status"]["active_context"] == "not_applicable"
    assert any(ref["payload_act"] == "generate" for ref in proof["ledger_references"])
    assert proof["checks"]["ledger_chain"]["status"] == "pass"
    assert proof["checks"]["ledger_chain"]["verified"]
    assert proof["checks"]["payload_hashes"]["status"] == "pass"
    assert proof["checks"]["payload_hashes"]["verified"]
    assert proof["checks"]["read_replay"]["status"] == "fail"
    assert proof["checks"]["read_replay"]["matches"] is False
    assert proof["checks"]["diff_comparison"]["status"] == "not_implemented"
    assert proof["checks"]["profile_permissions"]["status"] == "pass"
    assert proof["replay"]["matches"] is False
    assert proof["replay"]["claimed_projection_hash"]
    assert proof["replay"]["replayed_projection_hash"]


def test_audit_missing_target_is_not_valid() -> None:
    proof = audit_target(LedgerStore(SCE), "claim.unknown")

    assert proof["valid"] is False
    assert proof["checks"]["target_resolver"]["status"] == "not_found"
    assert proof["target_status"]["history"] == "not_found"
    assert proof["target_status"]["active_context"] == "unknown"


def test_audit_output_target_without_records_does_not_auto_pass() -> None:
    proof = audit_target(LedgerStore(SCE), "output.fake")

    assert proof["valid"] is False
    assert proof["checks"]["target_resolver"]["status"] != "pass"
    assert proof["target_status"]["history"] == "not_found"


def test_audit_placeholder_checks_are_not_reported_as_pass() -> None:
    proof = audit_target(LedgerStore(SCE), "claim.sce.watch_points_added")

    assert proof["checks"]["read_replay"]["status"] == "not_applicable"
    assert proof["checks"]["diff_comparison"]["status"] == "not_applicable"


def test_audit_payload_hashes_are_explicitly_verified() -> None:
    proof = audit_target(LedgerStore(SCE), "claim.sce.watch_points_added")
    payload_check = proof["checks"]["payload_hashes"]

    assert payload_check["status"] == "pass"
    assert payload_check["reason"] == "All referenced payloads matched their recorded payload_hash."
    assert len(payload_check["verified"]) == len(LedgerStore(SCE).read_entries())
    assert {
        "entry_id",
        "payload_ref",
        "expected_hash",
        "actual_hash",
        "status",
    } <= set(payload_check["verified"][0])
    assert all(item["status"] == "pass" for item in payload_check["verified"])


def test_audit_ledger_chain_is_explicitly_verified() -> None:
    proof = audit_target(LedgerStore(SCE), "claim.sce.watch_points_added")
    ledger_check = proof["checks"]["ledger_chain"]

    assert ledger_check["status"] == "pass"
    assert ledger_check["reason"] == "All referenced ledger entries recomputed successfully and prev_hash continuity was intact."
    assert len(ledger_check["verified"]) == len(LedgerStore(SCE).read_entries())
    first = ledger_check["verified"][0]
    assert {
        "entry_id",
        "timpo",
        "prev_hash",
        "prev_hash_matches",
        "expected_entry_hash",
        "actual_entry_hash",
        "status",
    } <= set(first)
    assert first["entry_id"] == "ledger.0001"
    assert first["prev_hash"] is None
    assert first["prev_hash_matches"] is True
    assert all(item["status"] == "pass" for item in ledger_check["verified"])


def test_audit_included_claim_has_admissibility_proof() -> None:
    proof = audit_target(LedgerStore(SCE), "claim.sce.watch_points_added")
    admissibility = proof["checks"]["admissibility"]

    assert admissibility["status"] == "pass"
    assert admissibility["interpretation"]["status"] == "found"
    assert admissibility["validation"]["status"] == "found"
    assert admissibility["validation"]["admissible"] is True
    assert admissibility["history"] == "found"
    assert admissibility["active_context"] == "included"
    assert proof["target_status"]["active_context"] == "included"
    assert proof["valid"] is True


def test_audit_rejected_claim_has_admissibility_proof() -> None:
    proof = audit_target(LedgerStore(SCE), "claim.sce.unsupported_cost_assumption")
    admissibility = proof["checks"]["admissibility"]

    assert admissibility["status"] == "pass"
    assert admissibility["interpretation"]["status"] == "found"
    assert admissibility["validation"]["status"] == "found"
    assert admissibility["validation"]["admissible"] is False
    assert proof["target_status"]["active_context"] == "excluded"
    assert proof["reason"] == "admissible false"
    assert proof["valid"] is True


def test_audit_unvalidated_candidate_is_excluded_with_admissibility_proof(tmp_path: Path) -> None:
    fixture = _copy_fixture(tmp_path)
    store = LedgerStore(fixture)
    store.write(
        {
            "from": "corus.interpreter",
            "act": "interpret",
            "type": "candidate_claim",
            "to": "claim.sce.unvalidated_candidate",
            "inputs": ["source.demo_model_output"],
            "data": {
                "claim": "This candidate has not been admitted.",
                "status": "candidate",
            },
        },
        timpo="11612132757493222933514833726911676416",
    )

    proof = audit_target(store, "claim.sce.unvalidated_candidate")
    admissibility = proof["checks"]["admissibility"]

    assert admissibility["status"] == "pass"
    assert admissibility["interpretation"]["status"] == "found"
    assert admissibility["validation"]["status"] == "not_found"
    assert admissibility["validation"]["reason"] == "unvalidated"
    assert proof["target_status"]["active_context"] == "excluded"


def test_audit_unknown_claim_has_no_admissibility_proof() -> None:
    proof = audit_target(LedgerStore(SCE), "claim.unknown")

    assert proof["checks"]["target_resolver"]["status"] == "not_found"
    assert proof["checks"]["admissibility"]["status"] == "not_found"
    assert proof["valid"] is False


def test_admissibility_resolver_fails_inconsistent_read_state() -> None:
    store = LedgerStore(SCE)
    read_result = read_active_context(store)
    rejected = next(item for item in read_result["excluded"] if item["id"] == "claim.sce.unsupported_cost_assumption")
    read_result = {
        **read_result,
        "included": [*read_result["included"], rejected],
        "excluded": [item for item in read_result["excluded"] if item["id"] != "claim.sce.unsupported_cost_assumption"],
    }

    admissibility = resolve_claim_admissibility(store, "claim.sce.unsupported_cost_assumption", read_result)

    assert admissibility["status"] == "fail"
    assert "expected READ active_context=excluded" in admissibility["reason"]


def test_claim_audit_is_valid_without_claimed_projection() -> None:
    proof = audit_target(LedgerStore(SCE), "claim.sce.watch_points_added")

    assert proof["checks"]["read_replay"]["status"] == "not_applicable"
    assert proof["checks"]["diff_comparison"]["status"] == "not_applicable"
    assert proof["valid"] is True


def test_rejected_claim_audit_is_valid_without_claimed_projection() -> None:
    proof = audit_target(LedgerStore(SCE), "claim.sce.unsupported_cost_assumption")

    assert proof["checks"]["admissibility"]["status"] == "pass"
    assert proof["checks"]["read_replay"]["status"] == "not_applicable"
    assert proof["checks"]["diff_comparison"]["status"] == "not_applicable"
    assert proof["valid"] is True


def test_claimed_projection_matching_replay_passes_read_replay() -> None:
    store = LedgerStore(SCE)
    claimed_projection = projection_fingerprint(read_active_context(store))
    proof = audit_target(store, "claim.sce.watch_points_added", projection=claimed_projection)

    assert proof["checks"]["read_replay"]["status"] == "pass"
    assert proof["checks"]["read_replay"]["matches"] is True
    assert proof["checks"]["diff_comparison"]["status"] == "not_applicable"
    assert proof["valid"] is True


def test_claimed_projection_mismatch_fails_read_replay() -> None:
    store = LedgerStore(SCE)
    claimed_projection = projection_fingerprint(read_active_context(store))
    claimed_projection["included"] = []
    proof = audit_target(store, "claim.sce.watch_points_added", projection=claimed_projection)

    assert proof["checks"]["read_replay"]["status"] == "fail"
    assert proof["checks"]["read_replay"]["matches"] is False
    assert proof["checks"]["diff_comparison"]["status"] == "not_implemented"
    assert proof["valid"] is False


def test_read_projection_hash_ignores_external_projection() -> None:
    store = LedgerStore(SCE)
    read_a = read_active_context(store)
    read_b = read_active_context(store, projection={"included": []})

    assert read_a["projection_hash"] == read_b["projection_hash"]


def test_audit_claim_target_resolves() -> None:
    proof = audit_target(LedgerStore(SCE), "claim.sce.watch_points_added")

    assert proof["checks"]["target_resolver"]["status"] == "pass"
    assert proof["target"]["type"] == "claim"
    assert proof["target_status"]["history"] == "found"
    assert any(ref["payload_act"] == "interpret" for ref in proof["ledger_references"])
    assert any(ref["payload_act"] == "validate" for ref in proof["ledger_references"])


def test_audit_generated_output_target_resolves() -> None:
    proof = audit_target(LedgerStore(SCE), "output.sce_grid_ops.work_packet")

    assert proof["checks"]["target_resolver"]["status"] == "pass"
    assert proof["target"]["type"] == "output"
    assert proof["target_status"]["history"] == "found"
    assert proof["target_status"]["active_context"] == "not_applicable"
    assert any(ref["payload_act"] == "generate" for ref in proof["ledger_references"])
    assert proof["checks"]["profile_permissions"]["status"] == "pass"
    assert proof["valid"] is True


def test_audit_output_target_has_profile_permission_proof() -> None:
    proof = audit_target(LedgerStore(SCE), "output.sce_grid_ops.work_packet")
    permissions = proof["checks"]["profile_permissions"]

    assert proof["checks"]["target_resolver"]["status"] == "pass"
    assert proof["target"]["type"] == "output"
    assert permissions["status"] == "pass"
    assert permissions["proposed_action"] == "generate_work_packet"
    assert permissions["permission_result"] == "allowed"
    assert permissions["profile"]["id"] == "profile.sce_grid_ops"
    assert "generate_work_packet" in permissions["allowed_actions"]


def test_audit_output_target_surfaces_restricted_actions() -> None:
    proof = audit_target(LedgerStore(SCE), "output.sce_grid_ops.work_packet")
    restricted = proof["checks"]["profile_permissions"]["restricted_actions"]

    assert {"action": "dispatch_crew", "permission_result": "approval_required"} in restricted


def test_audit_fake_output_still_fails_target_resolver() -> None:
    proof = audit_target(LedgerStore(SCE), "output.fake")

    assert proof["checks"]["target_resolver"]["status"] == "not_found"
    assert proof["checks"]["profile_permissions"]["status"] in {"not_found", "not_applicable"}
    assert proof["valid"] is False


def test_audit_generated_output_without_profile_input_fails_permissions(tmp_path: Path) -> None:
    fixture = _copy_fixture(tmp_path)
    store = LedgerStore(fixture)
    store.write(
        {
            "from": "corus.agent_run",
            "act": "generate",
            "type": "output",
            "to": "output.test.no_profile",
            "inputs": ["claim.sce.watch_points_added"],
            "data": {
                "proposed_action": "generate_work_packet",
                "permission_result": "allowed",
            },
        },
        timpo="11612132757493222933514833726911676417",
    )

    proof = audit_target(store, "output.test.no_profile")

    assert proof["checks"]["profile_permissions"]["status"] == "fail"
    assert "does not reference a profile input" in proof["checks"]["profile_permissions"]["reason"]
    assert proof["valid"] is False


def test_audit_generated_output_with_restricted_action_fails_permissions(tmp_path: Path) -> None:
    fixture = _copy_fixture(tmp_path)
    store = LedgerStore(fixture)
    store.write(
        {
            "from": "corus.agent_run",
            "act": "generate",
            "type": "output",
            "to": "output.test.dispatch",
            "inputs": ["claim.sce.watch_points_added", "profile.sce_grid_ops"],
            "data": {
                "proposed_action": "dispatch_crew",
                "permission_result": "approval_required",
            },
        },
        timpo="11612132757493222933514833726911676417",
    )

    proof = audit_target(store, "output.test.dispatch")

    assert proof["checks"]["profile_permissions"]["status"] == "fail"
    assert proof["checks"]["profile_permissions"]["proposed_action"] == "dispatch_crew"
    assert proof["valid"] is False


def test_audit_ledger_entry_id_target_resolves() -> None:
    store = LedgerStore(SCE)
    entry = store.read_entries()[0]
    proof = audit_target(store, entry["id"])

    assert proof["checks"]["target_resolver"]["status"] == "pass"
    assert proof["target"]["type"] == "ledger_entry"
    assert proof["target_status"]["history"] == "found"
    assert proof["target_status"]["active_context"] == "not_applicable"


def test_audit_entry_hash_target_resolves() -> None:
    store = LedgerStore(SCE)
    entry = store.read_entries()[0]
    proof = audit_target(store, entry["entry_hash"])

    assert proof["checks"]["target_resolver"]["status"] == "pass"
    assert proof["target"]["type"] == "ledger_entry"
    assert proof["target_status"]["history"] == "found"


def test_audit_payload_hash_target_resolves() -> None:
    store = LedgerStore(SCE)
    entry = store.read_entries()[0]
    proof = audit_target(store, entry["payload_hash"])

    assert proof["checks"]["target_resolver"]["status"] == "pass"
    assert proof["target"]["type"] == "payload"
    assert proof["target_status"]["history"] == "found"


def test_audit_object_target_returns_placeholder() -> None:
    proof = audit_target(LedgerStore(SCE), "edge.watch_points.risk")

    assert proof["checks"]["target_resolver"]["status"] == "not_implemented"
    assert proof["target"]["type"] == "object"
    assert proof["target_status"]["history"] == "unknown"
    assert proof["valid"] is False


def _payload_exists(target: str) -> bool:
    store = LedgerStore(SCE)
    return any(store.read_payload(entry).get("to") == target for entry in store.read_entries())


def _copy_fixture(tmp_path: Path) -> Path:
    fixture = tmp_path / "sce_vegetation"
    shutil.copytree(SCE, fixture)
    return fixture
