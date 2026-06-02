from __future__ import annotations

from pathlib import Path

REQUIRED_KEYS = {
    ".domain": ["domain", "version", "purpose", "entities", "policies", "outputs"],
    ".surface": ["surface", "type", "version", "purpose", "props", "relationships"],
    ".lens": ["id", "name", "core_question_pattern", "node_weight_rules", "edge_weight_rules"],
    ".profile": ["profile", "version", "purpose", "audience", "information_hierarchy", "actions"],
    ".value": [
        "value",
        "version",
        "customer",
        "source_context",
        "value_question",
        "customer_constraints",
        "context_input",
        "value_calculations",
        "value_outputs",
        "value_claims",
    ],
    ".program": ["program", "version", "purpose", "bindings", "workflow", "outputs"],
    ".process": ["process", "version", "purpose", "signature", "purity", "implementation"],
    ".input": ["input", "version", "type"],
    ".source": [],
    ".protocol": ["protocol", "version", "purpose"],
    ".timpos": ["timpos", "version", "records"],
    ".ledger": ["ledger", "version", "entries"],
}

RUN_MANIFEST_REQUIRED_KEYS = ["process", "version", "program", "status"]


def validate_document(path: Path, data: dict) -> list[str]:
    errors: list[str] = []
    required = REQUIRED_KEYS.get(path.suffix, [])
    if path.name == "manifest.process" and "fs/03_processes/runs" in path.as_posix():
        required = RUN_MANIFEST_REQUIRED_KEYS
    for key in required:
        if key not in data:
            errors.append(f"{path}: missing required key {key}")
    return errors
