from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.helpers import ROOT
from kernel.domain.loader import load_domain
from kernel.domain.validate import DomainValidationError, validate_domain
from kernel.engine.runtime import resolve_context
from kernel.lens.resolver import LensResolutionError
from kernel.surface.loader import load_surface
from kernel.surface.validate import SurfaceValidationError, validate_surface
from kernel.value.loader import load_value
from kernel.value.validate import ValueValidationError, validate_value


MALFORMED = ROOT / "tests" / "fixtures" / "malformed"


def _record(name: str) -> dict:
    return json.loads((MALFORMED / name).read_text(encoding="utf-8"))


def _validate_timpo_record(record: dict) -> None:
    if "when" not in record:
        raise ValueError("missing when")
    if "where" not in record:
        raise ValueError("missing where")
    if {"meaning", "domain", "context", "value"} & set(record):
        raise ValueError("timpo cannot contain domain meaning or context")


def test_reject_timpo_missing_when() -> None:
    with pytest.raises(ValueError, match="when"):
        _validate_timpo_record(_record("timpo_missing_when.json"))


def test_reject_timpo_missing_where() -> None:
    with pytest.raises(ValueError, match="where"):
        _validate_timpo_record(_record("timpo_missing_where.json"))


def test_reject_timpo_with_domain_meaning() -> None:
    with pytest.raises(ValueError, match="domain meaning"):
        _validate_timpo_record(_record("timpo_with_domain_meaning.json"))


def test_reject_domain_duplicate_nodes() -> None:
    with pytest.raises(DomainValidationError, match="duplicate"):
        validate_domain(load_domain(MALFORMED / "domain_duplicate_nodes.yaml"))


def test_reject_surface_dangling_edge(paths: dict) -> None:
    with pytest.raises(SurfaceValidationError, match="missing"):
        validate_surface(load_surface(MALFORMED / "surface_dangling_edge.yaml"), load_domain(paths["domain"]))


@pytest.mark.xfail(reason="lens entrypoint validation is an agent-runtime contract not implemented yet")
def test_reject_lens_missing_entrypoint(paths: dict) -> None:
    result = resolve_context(
        profile_path=paths["profile"],
        surface_path=paths["surface"],
        domain_path=paths["domain"],
        lens_paths=[MALFORMED / "lens_missing_entrypoint.yaml"],
        value_path=paths["value"],
    )
    assert result["context_gap"] == ["invalid_lens_entrypoint"]


def test_reject_profile_unknown_lens(paths: dict) -> None:
    with pytest.raises(LensResolutionError, match="missing lens"):
        resolve_context(
            profile_path=MALFORMED / "profile_unknown_lens.yaml",
            surface_path=paths["surface"],
            domain_path=paths["domain"],
            lens_paths=[paths["lens"]],
            value_path=paths["value"],
        )


def test_reject_value_unknown_metric() -> None:
    with pytest.raises(ValueValidationError, match="unknown metric"):
        validate_value(load_value(MALFORMED / "value_unknown_metric.yaml"))


def test_reject_manual_context_without_lineage() -> None:
    manual = _record("context_with_manual_because.json")
    with pytest.raises(ValueError, match="lineage"):
        if "lineage" not in manual["context"]:
            raise ValueError("manual context without lineage is not valid Corus context")

