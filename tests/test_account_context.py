from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from kernel.account_context import AccountContextValidationError, load_account_context, resolve_account_context
from kernel.account_context.validate import validate_account_context
from kernel.verify.hash import read_yaml, write_yaml


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "neara_account_context"


def test_loads_account_context_fixture() -> None:
    bundle = load_account_context(FIXTURE)

    assert bundle.profile.id == "profile.neara_director_customer_implementation"
    assert bundle.context.id == "context.rvo_customer_implementation"
    assert bundle.team.id == "team.neara_account_team"
    assert bundle.surface.id == "surface.account_context"
    assert {relation.id for relation in bundle.relations} == {
        "relation.cva.value_translation",
        "relation.fde.technical_implementation",
        "relation.director.account_coherence",
    }
    assert {artifact.id for artifact in bundle.artifacts} == {
        "artifact.value_evidence",
        "artifact.technical_evidence",
        "artifact.delivery_alignment",
    }


def test_surface_is_director_owned() -> None:
    result = resolve_account_context(FIXTURE)

    assert result["surface"]["owner"] == "role.neara_director_customer_implementation"
    assert result["surface"] == {
        "id": "surface.account_context",
        "owner": "role.neara_director_customer_implementation",
        "context": "context.rvo_customer_implementation",
        "boundary": "team.neara_account_team",
    }


def test_resolution_state_marks_alignment_not_adoption() -> None:
    result = resolve_account_context(FIXTURE)

    assert "unblock an account-context graph" in result["answer"]
    assert "adoption-ready" not in result["answer"]
    assert result["state"] == {
        "account_context_model": "ready",
        "mandates": "unblocked",
        "neara_alignment": "unresolved",
        "customer_adoption": "unresolved",
        "reason": (
            "RVO context unblocks CVA, FDE, and Director mandates, but value evidence, technical evidence, "
            "and delivery alignment artifacts have not yet been contributed."
        ),
    }
    assert result["unresolved"] == [
        "missing.contributed_artifact.value_evidence",
        "missing.contributed_artifact.technical_evidence",
        "missing.contributed_artifact.delivery_alignment",
        "missing.customer_sponsor_acceptance",
        "missing.customer_technical_acceptance",
        "missing.customer_user_workflow",
    ]
    assert "state" not in result["surface"]
    assert "unresolved" not in result["surface"]
    assert "events" not in result["surface"]
    assert "state_transitions" not in result["surface"]


def test_loads_profile_initiator() -> None:
    result = resolve_account_context(FIXTURE)

    assert result["initiator"]["profile"] == "profile.neara_director_customer_implementation"
    assert result["initiator"]["role"] == "role.neara_director_customer_implementation"
    assert result["initiator"]["core_question"]
    assert result["initiator"]["lens"] == {
        "id": "lens.director_account_alignment",
        "prioritizes": [
            "semantic.account_coherence",
            "artifact.delivery_alignment",
            "state.neara_alignment",
            "unresolved.customer_adoption",
        ],
    }


def test_alignment_readiness_is_explained_by_events_and_transitions() -> None:
    result = resolve_account_context(FIXTURE)

    assert [event["claim"] for event in result["events"]] == [
        "Director initiates the account-context question.",
        "RVO context enters the Neara account team.",
        "CVA value-translation mandate is unblocked.",
        "FDE technical-implementation mandate is unblocked.",
        "Director account-coherence mandate is unblocked.",
        "Expected artifacts are identified.",
    ]
    assert result["events"][-1] == {
        "id": "event.expected_artifacts_identified",
        "claim": "Expected artifacts are identified.",
        "caused_by": [
            "contract.value_translation",
            "contract.technical_implementation",
            "contract.account_coherence",
        ],
        "produces_state": "account_context_model.ready",
        "lineage": [
            "artifact.value_evidence",
            "artifact.technical_evidence",
            "artifact.delivery_alignment",
        ],
    }
    assert result["state_transitions"][0]["from"] == "neara_alignment.unresolved"
    assert result["state_transitions"][0]["to"] == "alignment.question_initiated"
    assert result["state_transitions"][1]["from"] == "alignment.question_initiated"
    assert result["state_transitions"][1]["to"] == "alignment.context_available"
    assert result["state_transitions"][-1]["to"] == "account_context_model.ready"
    assert "event.delivery_alignment_resolved" not in {event["id"] for event in result["events"]}
    assert "neara_alignment.ready" not in {transition["to"] for transition in result["state_transitions"]}
    assert result["state"]["customer_adoption"] == "unresolved"


def test_answer_is_initiator_aware_without_claiming_customer_adoption() -> None:
    result = resolve_account_context(FIXTURE)

    assert "CVA is positioned to produce value evidence" in result["answer"]
    assert "Neara-side alignment remains unresolved" in result["answer"]
    assert "customer adoption is ready" not in result["answer"]
    assert "CVA contributes value evidence" not in result["answer"]


def test_events_include_initiation() -> None:
    result = resolve_account_context(FIXTURE)

    assert "event.director_initiates_account_context_question" in {event["id"] for event in result["events"]}


def test_missing_technical_evidence_keeps_alignment_unresolved(tmp_path: Path) -> None:
    broken = _copy_fixture(tmp_path)
    artifacts_path = broken / "neara_account.artifacts"
    artifacts = read_yaml(artifacts_path)
    artifacts["artifacts"] = [item for item in artifacts["artifacts"] if item["id"] != "artifact.technical_evidence"]
    write_yaml(artifacts_path, artifacts)

    result = resolve_account_context(broken)

    _assert_alignment_unresolved(result, "missing.artifact.technical_evidence")


def test_missing_cva_value_relation_keeps_alignment_unresolved(tmp_path: Path) -> None:
    broken = _copy_fixture(tmp_path)
    relations_path = broken / "neara_account.relations"
    relations = read_yaml(relations_path)
    relations["relations"] = [item for item in relations["relations"] if item["id"] != "relation.cva.value_translation"]
    write_yaml(relations_path, relations)

    result = resolve_account_context(broken)

    _assert_alignment_unresolved(result, "missing.relation.cva.value_translation")


def test_missing_surface_owner_keeps_alignment_unresolved(tmp_path: Path) -> None:
    broken = _copy_fixture(tmp_path)
    surface_path = broken / "neara_account.surface"
    surface = read_yaml(surface_path)
    surface.pop("owner")
    write_yaml(surface_path, surface)

    result = resolve_account_context(broken)

    assert result["surface"] == {
        "id": "surface.account_context",
        "owner": None,
        "context": "context.rvo_customer_implementation",
        "boundary": "team.neara_account_team",
    }
    _assert_alignment_unresolved(result, "missing.surface.owner")


def test_role_relations_produce_expected_artifacts() -> None:
    result = resolve_account_context(FIXTURE)
    relations = {relation["id"]: relation for relation in result["relations"]}

    assert relations["relation.cva.value_translation"]["produces"] == ["artifact.value_evidence"]
    assert relations["relation.fde.technical_implementation"]["produces"] == ["artifact.technical_evidence"]
    assert relations["relation.director.account_coherence"]["produces"] == ["artifact.delivery_alignment"]


def test_surface_contracts_unblock_expected_artifacts_without_contribution() -> None:
    result = resolve_account_context(FIXTURE)

    assert result["mandates"] == [
        {
            "id": "mandate.cva.value_translation",
            "role": "role.neara_cva",
            "semantic": "value_translation",
            "source_basis": ["source.neara_cva_job_description"],
        },
        {
            "id": "mandate.fde.technical_implementation",
            "role": "role.neara_fde",
            "semantic": "technical_implementation",
            "source_basis": ["source.neara_fde_job_description"],
        },
        {
            "id": "mandate.director.account_coherence",
            "role": "role.neara_director_customer_implementation",
            "semantic": "account_coherence",
            "source_basis": ["source.neara_director_customer_implementation_job_description"],
        },
    ]
    assert [contract["expected_artifact"] for contract in result["surface_contracts"]] == [
        "artifact.value_evidence",
        "artifact.technical_evidence",
        "artifact.delivery_alignment",
    ]
    assert {contract["state"] for contract in result["surface_contracts"]} == {"unblocked"}
    assert {contract["artifact_present"] for contract in result["surface_contracts"]} == {False}
    assert result["expected_artifacts"] == [
        {"id": "artifact.value_evidence", "produced_by": "relation.cva.value_translation"},
        {"id": "artifact.technical_evidence", "produced_by": "relation.fde.technical_implementation"},
        {"id": "artifact.delivery_alignment", "produced_by": "relation.director.account_coherence"},
    ]
    assert result["contributed_artifacts"] == []


def test_roles_do_not_carry_semantic_relation_bloat() -> None:
    bundle = load_account_context(FIXTURE)
    forbidden = {"translation", "implementation", "coherence", "evidence", "escalation"}

    for role in bundle.roles:
        assert forbidden.isdisjoint(role.__dict__)


def test_resolution_hashes_are_deterministic() -> None:
    first = resolve_account_context(FIXTURE)
    second = resolve_account_context(FIXTURE)

    assert first["layer_hashes"]["resolution_hash"] == second["layer_hashes"]["resolution_hash"]
    assert first["trace"]["hash"] == second["trace"]["hash"]


def test_trace_proves_only_account_context_claims() -> None:
    result = resolve_account_context(FIXTURE)

    assert [claim["claim"] for claim in result["trace"]["claims"]] == [
        "Director initiates the account-context question.",
        "RVO context enters the Neara account team.",
        "CVA value-translation mandate is unblocked.",
        "FDE technical-implementation mandate is unblocked.",
        "Director account-coherence mandate is unblocked.",
        "Expected artifacts are identified.",
    ]


def test_broken_relation_reference_raises_clear_error(tmp_path: Path) -> None:
    broken = tmp_path / "neara_account_context"
    shutil.copytree(FIXTURE, broken)
    relations_path = broken / "neara_account.relations"
    relations = read_yaml(relations_path)
    relations["relations"][0]["from_role"] = "role.missing"
    write_yaml(relations_path, relations)

    with pytest.raises(AccountContextValidationError, match="from_role role.missing does not exist"):
        validate_account_context(load_account_context(broken))


def test_account_context_cli_smoke() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "corus", "account-context", str(FIXTURE)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    data = json.loads(completed.stdout)
    assert data["context"]["id"] == "context.rvo_customer_implementation"
    assert data["initiator"]["profile"] == "profile.neara_director_customer_implementation"
    assert data["team"]["id"] == "team.neara_account_team"
    assert data["surface"]["id"] == "surface.account_context"
    assert data["layer_hashes"]["resolution_hash"]


def _copy_fixture(tmp_path: Path) -> Path:
    broken = tmp_path / "neara_account_context"
    shutil.copytree(FIXTURE, broken)
    return broken


def _assert_alignment_unresolved(result: dict[str, object], missing_item: str) -> None:
    assert result["state"]["neara_alignment"] == "unresolved"
    assert missing_item in result["unresolved"]
    assert "event.delivery_alignment_resolved" not in {event["id"] for event in result["events"]}
    assert "neara_alignment.ready" not in {transition["to"] for transition in result["state_transitions"]}
    assert "state" not in result["surface"]
    assert "unresolved" not in result["surface"]
