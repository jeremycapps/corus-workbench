from __future__ import annotations

from typing import Any

from kernel.engine.hashing import hash_data


def build_account_context_trace(events: list[dict[str, Any]]) -> dict[str, Any]:
    claims = [{"claim": event["claim"], "lineage": event["lineage"]} for event in events]
    trace = {"claims": claims}
    trace["hash"] = hash_data(trace)
    return trace
