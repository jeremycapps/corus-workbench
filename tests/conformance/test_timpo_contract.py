from __future__ import annotations

from copy import deepcopy

import pytest

from tests.helpers import TIMPOS, contract_hash
from kernel.engine.hashing import hash_data
from kernel.verify.hash import read_yaml


FORBIDDEN_TIMPO_FIELDS = {"domain", "meaning", "context", "value", "customer_value"}


def _validate_timpo_record(record: dict) -> None:
    if "when" not in record or "time_ns" not in record["when"]:
        raise ValueError("timpo observation requires when.time_ns")
    if "where" not in record or not {"lat_deg", "lon_deg"} <= set(record["where"]):
        raise ValueError("timpo observation requires where.lat_deg and where.lon_deg")
    forbidden = FORBIDDEN_TIMPO_FIELDS & set(record)
    if forbidden:
        raise ValueError(f"timpo cannot store context fields: {sorted(forbidden)}")


def _canonical_records(records: list[dict]) -> list[dict]:
    return sorted(records, key=lambda item: int(item["timpo"]))


def test_timpo_requires_when_and_where() -> None:
    record = read_yaml(TIMPOS)["records"][0]
    _validate_timpo_record(record)

    missing_when = deepcopy(record)
    missing_when.pop("when")
    with pytest.raises(ValueError, match="when"):
        _validate_timpo_record(missing_when)

    missing_where = deepcopy(record)
    missing_where.pop("where")
    with pytest.raises(ValueError, match="where"):
        _validate_timpo_record(missing_where)


def test_timpo_cannot_store_context() -> None:
    record = deepcopy(read_yaml(TIMPOS)["records"][0])
    record["context"] = {"risk_tier": "watch"}
    with pytest.raises(ValueError, match="cannot store context"):
        _validate_timpo_record(record)


def test_timpo_rejects_domain_meaning_fields() -> None:
    record = deepcopy(read_yaml(TIMPOS)["records"][0])
    record["meaning"] = "vegetation_watch_point"
    with pytest.raises(ValueError, match="context fields"):
        _validate_timpo_record(record)


def test_timpo_observations_are_immutable_after_ingest() -> None:
    original = read_yaml(TIMPOS)["records"][0]
    before = hash_data(original)
    mutated = deepcopy(original)
    mutated["where"]["lat_deg"] = 41.0
    assert hash_data(mutated) != before


def test_timpo_canonical_order_is_stable() -> None:
    records = read_yaml(TIMPOS)["records"]
    assert hash_data(_canonical_records(records)) == hash_data(_canonical_records(list(reversed(records))))


def test_timpo_hash_is_stable_for_same_observations() -> None:
    assert contract_hash(TIMPOS) == contract_hash(TIMPOS)

