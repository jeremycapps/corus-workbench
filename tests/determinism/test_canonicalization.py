from __future__ import annotations

from kernel.engine.canonicalize import canonical_json


def test_input_canonicalization_is_key_order_stable() -> None:
    assert canonical_json({"b": 2, "a": 1}) == canonical_json({"a": 1, "b": 2})


def test_scalar_lists_are_order_insensitive_for_contract_hashing() -> None:
    assert canonical_json(["b", "a"]) == canonical_json(["a", "b"])


def test_id_dict_lists_are_ordered_by_id() -> None:
    assert canonical_json([{"id": "b"}, {"id": "a"}]) == canonical_json([{"id": "a"}, {"id": "b"}])

