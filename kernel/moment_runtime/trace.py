from __future__ import annotations

from typing import Any

from kernel.engine.hashing import hash_data


def build_moment_trace(resolution: dict[str, Any]) -> dict[str, Any]:
    artifacts = {artifact["id"]: artifact for artifact in resolution["artifacts"]}
    claims = []
    for context in resolution["derived_contexts"]:
        claims.append(
            {
                "claim": "Director-orchestrated account context begins when RVO enters the moment chain.",
                "lineage": context["moments"][:1],
            }
        )
    for contract in resolution["contracts"]:
        artifact = artifacts[contract["artifact"]]
        if artifact["current_state"] == "expected_missing":
            claims.append(
                {
                    "claim": f"{_contract_label(contract['id'])} is expected by contract but missing.",
                    "lineage": [contract["id"], contract["artifact"]],
                }
            )
    if resolution["state"].get("state.neara_alignment") == "ready":
        claims.append(
            {
                "claim": "Neara alignment is ready because required Neara-side artifacts are present.",
                "lineage": [
                    "artifact.value_evidence",
                    "artifact.roi_case",
                    "artifact.technical_evidence",
                    "artifact.integration_path",
                ],
            }
        )
    if resolution["state"].get("state.neara_alignment") == "unresolved":
        claims.append(
            {
                "claim": "Neara alignment remains unresolved because required artifacts are missing.",
                "lineage": ["state.neara_alignment"],
            }
        )
    if resolution["state"].get("state.customer_adoption") == "unresolved":
        claims.append(
            {
                "claim": "Customer adoption remains unresolved because customer acceptance artifacts are missing.",
                "lineage": ["state.customer_adoption"],
            }
        )
    trace = {"claims": claims}
    trace["hash"] = hash_data(trace)
    return trace


def _contract_label(contract_id: str) -> str:
    labels = {
        "contract.cva.value_evidence": "CVA value evidence",
        "contract.cva.roi_case": "CVA ROI case",
        "contract.fde.technical_evidence": "FDE technical evidence",
        "contract.fde.integration_path": "FDE integration path",
    }
    return labels.get(contract_id, contract_id)
