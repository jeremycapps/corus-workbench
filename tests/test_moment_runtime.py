from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from kernel.moment_runtime import MomentRuntimeValidationError, load_moment_runtime, resolve_moment_runtime
from kernel.moment_runtime.model import MOMENT_KEYS
from kernel.moment_runtime.validate import validate_moment_runtime
from kernel.verify.hash import read_yaml, write_yaml


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "neara_moment_v0"


def test_moment_atom_is_minimal() -> None:
    bundle = load_moment_runtime(FIXTURE)

    for moment in bundle.moments:
        assert set(moment.__dict__) == MOMENT_KEYS


def test_profile_types_are_enforced(tmp_path: Path) -> None:
    broken = _copy_fixture(tmp_path)
    profiles_path = broken / "profiles.yaml"
    profiles = read_yaml(profiles_path)
    profiles["profiles"][0]["type"] = "person"
    write_yaml(profiles_path, profiles)

    with pytest.raises(MomentRuntimeValidationError, match="invalid type person"):
        validate_moment_runtime(load_moment_runtime(broken))


def test_contract_has_exactly_one_artifact(tmp_path: Path) -> None:
    broken = _copy_fixture(tmp_path)
    contracts_path = broken / "contracts.yaml"
    contracts = read_yaml(contracts_path)
    contracts["contracts"][0]["artifact"] = ["artifact.value_evidence", "artifact.roi_case"]
    write_yaml(contracts_path, contracts)

    with pytest.raises(ValueError, match="must reference exactly one artifact"):
        load_moment_runtime(broken)


@pytest.mark.parametrize(
    ("path_name", "mutate", "message"),
    [
        ("moments.yaml", lambda data: data["moments"][0].update({"initiator": "profile.missing"}), "missing initiator"),
        ("contracts.yaml", lambda data: data["contracts"][0].update({"artifact": "artifact.missing"}), "missing artifact"),
        ("moments.yaml", lambda data: data["moments"][1].update({"orientation": "contract.missing"}), "missing contract"),
        ("moments.yaml", lambda data: data["moments"][1].update({"previous": "moment.missing"}), "missing previous moment"),
        ("contracts.yaml", lambda data: data["contracts"][0].update({"derived_from": ["source.missing"]}), "missing source"),
    ],
)
def test_references_validate(tmp_path: Path, path_name: str, mutate: object, message: str) -> None:
    broken = _copy_fixture(tmp_path)
    path = broken / path_name
    data = read_yaml(path)
    mutate(data)
    write_yaml(path, data)

    with pytest.raises(MomentRuntimeValidationError, match=message):
        validate_moment_runtime(load_moment_runtime(broken))


def test_context_is_derived_without_authored_context_file() -> None:
    assert not (FIXTURE / "context.yaml").exists()

    result = resolve_moment_runtime(FIXTURE)

    assert result["derived_contexts"][0]["id"] == "context.neara.rvo.account_context"
    assert result["derived_contexts"][0]["orchestrator"] == "profile.neara_director_customer_implementation"
    assert result["derived_contexts"][0]["subject"] == "source.neara_rvo"
    assert result["derived_contexts"][0]["moments"] == [
        "moment.001",
        "moment.002",
        "moment.003",
        "moment.004",
        "moment.005",
        "moment.006",
    ]


def test_default_neara_state_is_unresolved() -> None:
    result = resolve_moment_runtime(FIXTURE)

    assert result["state"]["state.neara_alignment"] == "unresolved"
    assert result["state"]["state.customer_adoption"] == "unresolved"
    assert "Neara-side alignment remains unresolved" in result["answer"]
    assert "CVA contributed value evidence" not in result["answer"]
    assert "FDE contributed technical evidence" not in result["answer"]


def test_positive_path_with_neara_alignment_commits(tmp_path: Path) -> None:
    fixture = _copy_fixture(tmp_path)
    commits = [
        ("commit.001", "artifact.value_evidence", "profile.neara_cva"),
        ("commit.002", "artifact.roi_case", "profile.neara_cva"),
        ("commit.003", "artifact.technical_evidence", "profile.neara_fde"),
        ("commit.004", "artifact.integration_path", "profile.neara_fde"),
    ]
    _add_commits(fixture, commits)
    _add_commit_moments(fixture, commits)

    result = resolve_moment_runtime(fixture)

    assert {contract["state"] for contract in result["contracts"]} == {"present"}
    assert result["state"]["state.neara_alignment"] == "ready"
    assert result["state"]["state.customer_adoption"] == "unresolved"
    assert "moment.commit.001" in result["derived_contexts"][0]["moments"]
    assert "moment.commit.004" in result["derived_contexts"][0]["moments"]
    assert "Neara alignment is ready because required Neara-side artifacts are present." in {
        claim["claim"] for claim in result["trace"]["claims"]
    }
    assert "Customer adoption remains unresolved because customer acceptance artifacts are missing." in {
        claim["claim"] for claim in result["trace"]["claims"]
    }


def test_customer_adoption_positive_path(tmp_path: Path) -> None:
    fixture = _copy_fixture(tmp_path)
    commits = [
        ("commit.001", "artifact.value_evidence", "profile.neara_cva"),
        ("commit.002", "artifact.roi_case", "profile.neara_cva"),
        ("commit.003", "artifact.technical_evidence", "profile.neara_fde"),
        ("commit.004", "artifact.integration_path", "profile.neara_fde"),
        ("commit.005", "artifact.customer_sponsor_acceptance", "profile.neara_director_customer_implementation"),
        ("commit.006", "artifact.customer_technical_acceptance", "profile.neara_director_customer_implementation"),
    ]
    _add_commits(fixture, commits)
    _add_commit_moments(fixture, commits)

    result = resolve_moment_runtime(fixture)

    assert result["state"]["state.customer_adoption"] == "ready"


def test_hashes_are_deterministic() -> None:
    first = resolve_moment_runtime(FIXTURE)
    second = resolve_moment_runtime(FIXTURE)

    assert first["trace"]["hash"] == second["trace"]["hash"]
    assert first["layer_hashes"]["resolution_hash"] == second["layer_hashes"]["resolution_hash"]


def test_moment_cli_smoke() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "corus", "moment", str(FIXTURE)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    data = json.loads(completed.stdout)
    assert data["derived_contexts"][0]["id"] == "context.neara.rvo.account_context"
    assert data["state"]["state.neara_alignment"] == "unresolved"
    assert data["layer_hashes"]["resolution_hash"]


def _copy_fixture(tmp_path: Path) -> Path:
    target = tmp_path / "neara_moment_v0"
    shutil.copytree(FIXTURE, target)
    return target


def _add_commits(fixture: Path, commits: list[tuple[str, str, str]]) -> None:
    path = fixture / "commits.yaml"
    payload = {"commits": []}
    previous = None
    for commit_id, artifact_id, author in commits:
        payload["commits"].append(
            {
                "id": commit_id,
                "target": artifact_id,
                "from_state": "expected_missing",
                "to_state": "present",
                "author": author,
                "timpo": f"timpo.demo.{commit_id.replace('.', '_')}",
                "previous": previous,
            }
        )
        previous = commit_id
    write_yaml(path, payload)


def _add_commit_moments(fixture: Path, commits: list[tuple[str, str, str]]) -> None:
    path = fixture / "moments.yaml"
    payload = read_yaml(path)
    previous_moment = "moment.006"
    for commit_id, _artifact_id, author in commits:
        moment_id = f"moment.{commit_id}"
        payload["moments"].append(
            {
                "id": moment_id,
                "timpo": f"timpo.demo.{commit_id.replace('.', '_')}_enters_context",
                "initiator": author,
                "orientation": "commit.artifact_update",
                "subject": commit_id,
                "previous": previous_moment,
            }
        )
        previous_moment = moment_id
    write_yaml(path, payload)
