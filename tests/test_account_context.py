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


def test_role_relations_produce_expected_artifacts() -> None:
    result = resolve_account_context(FIXTURE)
    relations = {relation["id"]: relation for relation in result["relations"]}

    assert relations["relation.cva.value_translation"]["produces"] == ["artifact.value_evidence"]
    assert relations["relation.fde.technical_implementation"]["produces"] == ["artifact.technical_evidence"]
    assert relations["relation.director.account_coherence"]["produces"] == ["artifact.delivery_alignment"]


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
    assert data["team"]["id"] == "team.neara_account_team"
    assert data["surface"]["id"] == "surface.account_context"
    assert data["layer_hashes"]["resolution_hash"]
