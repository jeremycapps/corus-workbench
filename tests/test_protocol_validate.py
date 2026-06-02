from pathlib import Path

from kernel.verify.hash import read_yaml
from kernel.verify.validate import validate_document


def test_seed_semantic_documents_validate() -> None:
    root = Path(__file__).resolve().parents[1]
    errors = []
    for path in (root / "fs").rglob("*"):
        if path.is_file() and path.suffix in {
            ".domain",
            ".surface",
            ".profile",
            ".value",
            ".program",
            ".process",
            ".input",
            ".protocol",
            ".timpos",
            ".ledger",
        }:
            errors.extend(validate_document(path, read_yaml(path)))
    assert errors == []
