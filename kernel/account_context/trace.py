from __future__ import annotations

from typing import Any

from kernel.account_context.model import AccountContextBundle
from kernel.engine.hashing import hash_data


def build_account_context_trace(bundle: AccountContextBundle) -> dict[str, Any]:
    claims = [
        {
            "claim": "RVO context enters the Neara account team.",
            "lineage": ["context", "team", "sources"],
        },
        {
            "claim": "CVA contributes value translation into the account surface.",
            "lineage": ["role.neara_cva", "relation.cva.value_translation", "artifact.value_evidence"],
        },
        {
            "claim": "FDE contributes technical implementation into the account surface.",
            "lineage": ["role.neara_fde", "relation.fde.technical_implementation", "artifact.technical_evidence"],
        },
        {
            "claim": "Director owns the account surface and resolves delivery alignment.",
            "lineage": [
                "role.neara_director_customer_implementation",
                "surface.account_context",
                "artifact.delivery_alignment",
            ],
        },
    ]
    trace = {"claims": claims}
    trace["hash"] = hash_data(trace)
    return trace
