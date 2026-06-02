from __future__ import annotations

from typing import Any

from kernel.ledger.store import LedgerStore
from kernel.verify.hash import read_yaml


def verify_profile_permissions(
    store: LedgerStore,
    target: str,
    target_resolution: dict[str, Any],
) -> dict[str, Any]:
    if target_resolution["target"]["type"] != "output":
        return {
            "status": "not_applicable",
            "reason": "Profile permissions apply to output/action targets, not claim targets.",
        }

    output = _generated_output_payload(store, target_resolution)
    if output is None:
        return {
            "status": "not_found",
            "reason": "No generated output payload resolved for output target.",
        }

    output_entry, output_payload = output
    proposed_action = output_payload.get("data", {}).get("proposed_action")
    if not proposed_action:
        return {
            "status": "fail",
            "reason": "Generated output does not include proposed_action.",
            "output": _output_reference(target, output_entry),
        }

    profile_id = _profile_input(output_payload)
    if profile_id is None:
        return {
            "status": "fail",
            "reason": "Generated output does not reference a profile input.",
            "output": _output_reference(target, output_entry),
            "proposed_action": proposed_action,
        }

    profile = _resolve_profile_contract(store, profile_id)
    if profile is None:
        return {
            "status": "fail",
            "reason": "Referenced profile input did not resolve to a declared profile contract.",
            "output": _output_reference(target, output_entry),
            "profile": {"id": profile_id},
            "proposed_action": proposed_action,
        }

    profile_entry, profile_payload, profile_data = profile
    allowed_actions = _action_names(profile_data.get("allowed_actions", []))
    restricted_actions = _restricted_actions(profile_data.get("restricted_actions", []))
    restricted_by_action = {item["action"]: item for item in restricted_actions}
    permission_result = str(output_payload.get("data", {}).get("permission_result") or "")

    result = {
        "output": _output_reference(target, output_entry),
        "profile": {
            "id": profile_id,
            "contract_ref": profile_payload.get("data", {}).get("ref"),
            "entry_id": profile_entry["id"],
            "payload_hash": profile_entry["payload_hash"],
        },
        "proposed_action": proposed_action,
        "permission_result": permission_result,
        "allowed_actions": allowed_actions,
        "restricted_actions": restricted_actions,
    }

    if proposed_action in restricted_by_action and restricted_by_action[proposed_action]["permission_result"] == "approval_required":
        return {
            "status": "fail",
            "reason": "Generated output proposed_action requires approval by referenced profile.",
            **result,
        }
    if proposed_action not in allowed_actions:
        return {
            "status": "fail",
            "reason": "Generated output proposed_action is not allowed by referenced profile.",
            **result,
        }
    return {
        "status": "pass",
        "reason": "Generated output proposed_action is allowed by referenced profile.",
        **result,
    }


def _generated_output_payload(
    store: LedgerStore,
    target_resolution: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]] | None:
    for record in target_resolution["records"]:
        if record["payload_act"] != "generate" or record["payload_type"] != "output":
            continue
        entry = next(item for item in store.read_entries() if item["id"] == record["entry_id"])
        payload = store.read_payload(entry)
        return entry, payload
    return None


def _profile_input(payload: dict[str, Any]) -> str | None:
    return next((item for item in payload.get("inputs", []) if str(item).startswith("profile.")), None)


def _resolve_profile_contract(
    store: LedgerStore,
    profile_id: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]] | None:
    for entry in store.read_entries():
        payload = store.read_payload(entry)
        data = payload.get("data", {})
        if (
            payload.get("act") == "declare"
            and payload.get("type") == "contract"
            and payload.get("to") == profile_id
            and data.get("contract_kind") == "profile"
        ):
            return entry, payload, _profile_data(store, data)
    return None


def _profile_data(store: LedgerStore, declaration_data: dict[str, Any]) -> dict[str, Any]:
    if "allowed_actions" in declaration_data or "restricted_actions" in declaration_data:
        return declaration_data
    ref = declaration_data.get("ref")
    if ref:
        return read_yaml(store.root / str(ref))
    return declaration_data


def _action_names(actions: list[Any]) -> list[str]:
    names = []
    for action in actions:
        if isinstance(action, dict):
            names.append(str(action.get("action")))
        else:
            names.append(str(action))
    return names


def _restricted_actions(actions: list[Any]) -> list[dict[str, str]]:
    restricted = []
    for action in actions:
        if isinstance(action, dict):
            restricted.append(
                {
                    "action": str(action.get("action")),
                    "permission_result": str(action.get("permission_result", "approval_required")),
                }
            )
        else:
            restricted.append({"action": str(action), "permission_result": "approval_required"})
    return restricted


def _output_reference(target: str, entry: dict[str, Any]) -> dict[str, str]:
    return {
        "id": target,
        "entry_id": entry["id"],
        "payload_hash": entry["payload_hash"],
    }
