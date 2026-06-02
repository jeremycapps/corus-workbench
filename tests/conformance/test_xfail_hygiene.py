from __future__ import annotations

import ast
from pathlib import Path


def test_all_xfail_markers_have_explicit_reasons() -> None:
    root = Path(__file__).resolve().parents[1]
    offenders = []
    for path in sorted(root.rglob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and _is_xfail_call(node):
                if not any(keyword.arg == "reason" and _has_text(keyword.value) for keyword in node.keywords):
                    offenders.append(f"{path}:{node.lineno}")
    assert offenders == []


def _is_xfail_call(node: ast.Call) -> bool:
    func = node.func
    return (
        isinstance(func, ast.Attribute)
        and func.attr == "xfail"
        and isinstance(func.value, ast.Attribute)
        and func.value.attr == "mark"
    )


def _has_text(node: ast.AST) -> bool:
    return isinstance(node, ast.Constant) and isinstance(node.value, str) and bool(node.value.strip())

