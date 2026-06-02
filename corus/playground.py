from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from kernel.audit import audit_target
from kernel.domain.loader import load_domain
from kernel.domain.validate import validate_domain
from kernel.engine.hashing import hash_data
from kernel.engine.runtime import resolve_context
from kernel.ledger.read import read_active_context
from kernel.ledger.store import LedgerStore, validate_payload
from kernel.lens.loader import load_lens
from kernel.lens.validate import validate_lens
from kernel.profile.loader import load_profile
from kernel.profile.validate import validate_profile
from kernel.source import add_source
from kernel.surface.loader import load_surface
from kernel.surface.validate import validate_surface
from kernel.value.loader import load_value
from kernel.value.validate import validate_value
from kernel.verify.hash import read_yaml


@dataclass(frozen=True)
class FixtureBundle:
    root: Path
    timpo_path: Path | None
    domain_path: Path
    surface_path: Path
    lens_paths: list[Path]
    profile_paths: list[Path]
    value_path: Path | None
    evidence_path: Path | None


def _find_one(root: Path, pattern: str, required: bool = True) -> Path | None:
    matches = sorted(root.glob(pattern))
    if matches:
        return matches[0]
    if required:
        raise FileNotFoundError(f"{root} does not contain {pattern}")
    return None


def load_bundle(root: Path) -> FixtureBundle:
    root = root.resolve()
    return FixtureBundle(
        root=root,
        timpo_path=_find_one(root, "*.timpos", required=False),
        domain_path=_find_one(root, "*.domain"),
        surface_path=_find_one(root, "*.surface"),
        lens_paths=sorted(root.glob("*.lens")),
        profile_paths=sorted(root.glob("*.profile")),
        value_path=_find_one(root, "*.value", required=False),
        evidence_path=_find_one(root, "*.evidence", required=False),
    )


def _id_from(path: Path) -> str:
    data = read_yaml(path)
    return str(data.get("id") or data.get(path.suffix.lstrip(".")) or path.stem)


def _select(paths: list[Path], requested: str | None, label: str) -> Path:
    if not paths:
        raise FileNotFoundError(f"fixture has no {label} files")
    if requested is None:
        return paths[0]
    for path in paths:
        if requested in {path.stem, _id_from(path)}:
            return path
    raise FileNotFoundError(f"fixture has no {label} named {requested}")


def validate_timpos(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {"valid": False, "path": None, "error": "missing timpo file"}
    data = read_yaml(path)
    records = list(data.get("records", []))
    for index, record in enumerate(records):
        if "when" not in record or "time_ns" not in record["when"]:
            return {"valid": False, "path": str(path), "error": f"record {index} missing when.time_ns"}
        if "where" not in record or not {"lat_deg", "lon_deg"} <= set(record["where"]):
            return {"valid": False, "path": str(path), "error": f"record {index} missing where lat/lon"}
        forbidden = {"domain", "meaning", "context", "value", "customer_value"} & set(record)
        if forbidden:
            return {"valid": False, "path": str(path), "error": f"record {index} has forbidden fields {sorted(forbidden)}"}
    return {"valid": True, "path": str(path), "record_count": len(records), "hash": hash_data(data)}


def validate_bundle(bundle: FixtureBundle) -> dict[str, Any]:
    result: dict[str, Any] = {"fixture": str(bundle.root)}
    result["timpo"] = validate_timpos(bundle.timpo_path)

    try:
        domain = load_domain(bundle.domain_path)
        validate_domain(domain)
        result["domain"] = {"valid": True, "path": str(bundle.domain_path), "node_count": len(domain.nodes)}
    except Exception as exc:
        result["domain"] = {"valid": False, "path": str(bundle.domain_path), "error": str(exc)}
        domain = None

    try:
        surface = load_surface(bundle.surface_path)
        if domain is None:
            raise ValueError("domain must validate before surface")
        validate_surface(surface, domain)
        result["surface"] = {"valid": True, "path": str(bundle.surface_path), "edge_count": len(surface.edges)}
    except Exception as exc:
        result["surface"] = {"valid": False, "path": str(bundle.surface_path), "error": str(exc)}

    result["lens"] = []
    for path in bundle.lens_paths:
        try:
            lens = load_lens(path)
            validate_lens(lens, domain)
            result["lens"].append({"valid": True, "id": lens.id, "path": str(path)})
        except Exception as exc:
            result["lens"].append({"valid": False, "path": str(path), "error": str(exc)})

    result["profile"] = []
    for path in bundle.profile_paths:
        try:
            profile = load_profile(path)
            validate_profile(profile)
            result["profile"].append({"valid": True, "id": profile.id, "path": str(path)})
        except Exception as exc:
            result["profile"].append({"valid": False, "path": str(path), "error": str(exc)})

    if bundle.value_path:
        try:
            value = load_value(bundle.value_path)
            validate_value(value)
            result["value"] = {"valid": True, "id": value.id, "path": str(bundle.value_path)}
        except Exception as exc:
            result["value"] = {"valid": False, "path": str(bundle.value_path), "error": str(exc)}
    else:
        result["value"] = {"valid": False, "path": None, "error": "missing value file"}

    if bundle.evidence_path:
        evidence = read_yaml(bundle.evidence_path)
        facts = list(evidence.get("facts", []))
        result["evidence"] = {
            "valid": all(fact.get("id") and fact.get("claim") and fact.get("supports_domain_node") for fact in facts),
            "id": evidence.get("id"),
            "path": str(bundle.evidence_path),
            "fact_count": len(facts),
        }
    else:
        result["evidence"] = {"valid": False, "path": None, "error": "missing evidence file"}
    return result


def runtime_result(bundle: FixtureBundle, profile: str | None = None, lens: str | None = None) -> dict[str, Any]:
    profile_path = _select(bundle.profile_paths, profile, "profile")
    lens_paths = [_select(bundle.lens_paths, lens, "lens")] if lens else bundle.lens_paths
    return resolve_context(
        profile_path=profile_path,
        surface_path=bundle.surface_path,
        domain_path=bundle.domain_path,
        lens_paths=lens_paths,
        value_path=bundle.value_path,
    )


def selected_profile_path(bundle: FixtureBundle, profile: str | None = None) -> Path:
    return _select(bundle.profile_paths, profile, "profile")


def selected_lens_path(bundle: FixtureBundle, lens: str | None = None) -> Path:
    return _select(bundle.lens_paths, lens, "lens")


def command_reconstruct(bundle: FixtureBundle) -> dict[str, Any]:
    result = runtime_result(bundle)
    domain = load_domain(bundle.domain_path)
    surface = load_surface(bundle.surface_path)
    timpo = validate_timpos(bundle.timpo_path)
    return {
        "observation_count": timpo.get("record_count", 0),
        "domain_node_count": len(domain.nodes),
        "surface_edge_count": len(surface.edges),
        "context_hash": result["layer_hashes"]["context_hash"],
        "context_summary": result["first_order_context"],
    }


def command_project(bundle: FixtureBundle, profile: str | None, lens: str | None) -> dict[str, Any]:
    result = runtime_result(bundle, profile=profile, lens=lens)
    return {
        "profile_id": result["profile_id"],
        "core_question": result["core_question"],
        "lens_id": result["lens_id"],
        "entrypoint": result["weighted_node_list"][0]["id"] if result["weighted_node_list"] else None,
        "selected_nodes": result["first_order_context"]["node_ids"],
        "traversal_path": result["first_order_context"]["edge_ids"],
        "projection_hash": result["layer_hashes"]["projection_hash"],
    }


def command_read(bundle: FixtureBundle, profile: str | None, lens: str | None) -> dict[str, Any]:
    projection = command_project(bundle, profile, lens) if profile or lens else None
    store = LedgerStore(bundle.root)
    read_result = read_active_context(store, projection=projection)
    return {
        "architecture": {
            "phrase": "Timpos anchors. Ledger preserves. Admission writes. Corus reads. Audit proves.",
            "invariant": "A claim can exist in the ledger without existing in active context.",
        },
        "read_context": _read_context(projection),
        "admission_trail": _admission_trail(store),
        **read_result,
    }


def command_audit(bundle: FixtureBundle, target: str, profile: str | None, lens: str | None) -> dict[str, Any]:
    projection = command_project(bundle, profile, lens) if profile or lens else None
    return audit_target(LedgerStore(bundle.root), target=target, projection=projection)


def command_write(payload_path: Path, timpo: str | None) -> dict[str, Any]:
    payload_path = payload_path.resolve()
    payload = read_yaml(payload_path)
    validate_payload(payload)
    if payload_path.parent.name == "payloads" and payload_path.parent.parent.name == "ledger":
        store = LedgerStore(payload_path.parent.parent.parent)
    else:
        store = LedgerStore(payload_path.parent)
    if timpo:
        entry = store.write(payload, timpo)
        return {"written": True, "payload_hash": entry["payload_hash"], "entry": entry}

    payload_hash = hash_data(payload)
    matches = [
        entry
        for entry in store.read_entries()
        if entry["payload_hash"] == payload_hash
    ] if store.entries_root.exists() else []
    return {
        "written": False,
        "payload_valid": True,
        "payload_hash": payload_hash,
        "matching_entries": matches,
    }


def command_ingest(bundle_root: Path, out_root: Path) -> dict[str, Any]:
    bundle_root = bundle_root.resolve()
    out_root = out_root.resolve()
    manifest = read_yaml(bundle_root / "corus.bundle.yaml")
    if (out_root / "ledger" / "entries").exists() and list((out_root / "ledger" / "entries").glob("ledger.*.yaml")):
        raise ValueError(f"output run already has ledger entries: {out_root}")

    (out_root / "ledger" / "entries").mkdir(parents=True, exist_ok=True)
    (out_root / "ledger" / "payloads").mkdir(parents=True, exist_ok=True)
    _copy_bundle_files(bundle_root, out_root, manifest)

    store = LedgerStore(out_root)
    timpos = list(manifest.get("timpo_sequence", []))
    written = []

    def write_payload(payload: dict[str, Any]) -> None:
        entry = store.write(payload, timpos[len(written) % len(timpos)] if timpos else "0")
        written.append(
            {
                "id": payload["to"],
                "event": _admission_event(payload),
                "entry_id": entry["id"],
                "payload_hash": entry["payload_hash"],
            }
        )

    for source in manifest.get("sources", []):
        write_payload(
            {
                "from": "user",
                "act": "add",
                "type": "artifact",
                "to": source["id"],
                "inputs": [],
                "data": {
                    "kind": source.get("kind"),
                    "file": source["file"],
                },
            }
        )

    validations = {item["target"]: item for item in manifest.get("validations", [])}
    for claim in manifest.get("claims", []):
        claim_data = {
            "claim": claim["claim"],
            "status": "candidate",
        }
        for optional in ["value", "unit", "candidate_for"]:
            if optional in claim:
                claim_data[optional] = claim[optional]
        write_payload(
            {
                "from": "corus.interpreter",
                "act": "interpret",
                "type": "candidate_claim",
                "to": claim["id"],
                "inputs": [claim["source"]],
                "data": claim_data,
            }
        )
        validation = validations.get(claim["id"])
        if validation:
            write_payload(
                {
                    "from": "user",
                    "act": "validate",
                    "type": "candidate_claim",
                    "to": validation["target"],
                    "inputs": [validation["target"]],
                    "data": {
                        "admissible": bool(validation["admissible"]),
                        "reason": validation.get("reason"),
                    },
                }
            )

    for contract in manifest.get("contracts", []):
        write_payload(
            {
                "from": "user",
                "act": "declare",
                "type": "contract",
                "to": contract["id"],
                "inputs": [],
                "data": {
                    "contract_kind": contract["kind"],
                    "ref": Path(contract["ref"]).name,
                },
            }
        )

    for output in manifest.get("outputs", []):
        write_payload(
            {
                "from": output.get("from", "corus.agent_run"),
                "act": "generate",
                "type": "output",
                "to": output["id"],
                "inputs": list(output.get("inputs", [])),
                "data": dict(output.get("data", {})),
            }
        )

    ledger = store.verify_chain()
    return {
        "bundle_id": manifest["id"],
        "bundle_name": manifest.get("name"),
        "run_dir": str(out_root),
        "ledger": ledger,
        "entries_written": len(written),
        "written_payloads": written,
    }


def _copy_bundle_files(bundle_root: Path, out_root: Path, manifest: dict[str, Any]) -> None:
    for source in manifest.get("sources", []):
        source_path = bundle_root / source["file"]
        dest_path = out_root / source["file"]
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, dest_path)
    for contract in manifest.get("contracts", []):
        source_path = bundle_root / contract["ref"]
        root_dest = out_root / source_path.name
        shutil.copy2(source_path, root_dest)


def _read_context(projection: dict[str, Any] | None) -> dict[str, str]:
    if projection is None:
        return {
            "profile": "not selected",
            "lens": "not selected",
            "core_question": "unresolved",
        }
    return {
        "profile": f"profile.{projection['profile_id']}" if projection.get("profile_id") else "not selected",
        "lens": f"lens.{projection['lens_id']}" if projection.get("lens_id") else "not selected",
        "core_question": projection.get("core_question") or "unresolved",
    }


def _admission_trail(store: LedgerStore) -> list[dict[str, str]]:
    trail = []
    for entry in store.read_entries():
        payload = store.read_payload(entry)
        if payload.get("act") == "add" or payload.get("type") == "candidate_claim":
            trail.append(
                {
                    "id": payload["to"],
                    "event": _admission_event(payload),
                    "entry_id": entry["id"],
                }
            )
    return trail


def _admission_event(payload: dict[str, Any]) -> str:
    if payload.get("act") == "add":
        return "was added"
    if payload.get("act") == "interpret":
        return "was interpreted"
    if payload.get("act") == "validate":
        return "was validated" if payload.get("data", {}).get("admissible") else "was rejected"
    if payload.get("act") == "declare":
        return "was declared"
    if payload.get("act") == "generate":
        return "was generated"
    return f"was {payload.get('act')}"


OPERATIONAL_NODE_PATH = [
    "sce.source_evidence",
    "neara.model_delta",
    "sce.clearance_policy",
    "sce.vegetation_watch_points",
    "sce.wildfire_risk",
    "sce.operational_priority",
    "sce.crew_hours",
    "sce.cost_exposure",
    "sce.customer_value",
    "neara.repeatable_product_pattern",
]


def _timpo_observation_ids(path: Path | None) -> list[str]:
    if path is None:
        return []
    data = read_yaml(path)
    ids = []
    for record in data.get("records", []):
        payload = record.get("payload", {})
        ids.append(str(payload.get("ref") or record.get("timpo")))
    return ids


def _surface_edges_touching(edges: list[Any], node_id: str) -> list[str]:
    return sorted(edge.id for edge in edges if edge.from_node == node_id or edge.to_node == node_id)


def _directed_surface_path(edges: list[Any], start: str, end: str) -> tuple[list[str], list[str]]:
    by_from: dict[str, list[Any]] = {}
    for edge in edges:
        by_from.setdefault(edge.from_node, []).append(edge)
    for edge_list in by_from.values():
        edge_list.sort(key=lambda item: item.id)

    queue: list[tuple[str, list[str], list[str]]] = [(start, [start], [])]
    visited = {start}
    while queue:
        node_id, node_path, edge_path = queue.pop(0)
        if node_id == end:
            return node_path, edge_path
        for edge in by_from.get(node_id, []):
            if edge.to_node in visited:
                continue
            visited.add(edge.to_node)
            queue.append((edge.to_node, [*node_path, edge.to_node], [*edge_path, edge.id]))
    return [], []


def _value_metrics(bundle: FixtureBundle) -> list[str]:
    if bundle.value_path is None:
        return []
    return list(read_yaml(bundle.value_path).get("success_criteria", []))


def _operational_path_summary(evidence: dict[str, Any], surface: Any, bundle: FixtureBundle) -> dict[str, Any]:
    facts = list(evidence.get("facts", []))
    fact_by_id = {fact.get("id"): fact for fact in facts}
    domain_path, surface_path = _directed_surface_path(surface.edges, "neara.model_delta", "sce.customer_value")
    source_observations = sorted({str(fact.get("source_observation")) for fact in facts if fact.get("source_observation")})
    return {
        "start": "fact.watch_points.added" if "fact.watch_points.added" in fact_by_id else (facts[0]["id"] if facts else None),
        "end": "fact.cost.customer_value" if "fact.cost.customer_value" in fact_by_id else (facts[-1]["id"] if facts else None),
        "source_observations": source_observations,
        "domain_path": domain_path,
        "surface_path": surface_path,
        "value_metrics": _value_metrics(bundle),
    }


def _operational_trace(bundle: FixtureBundle) -> dict[str, Any]:
    domain = load_domain(bundle.domain_path)
    surface = load_surface(bundle.surface_path)
    domain_node_ids = {node.id for node in domain.nodes}
    evidence = read_yaml(bundle.evidence_path) if bundle.evidence_path else {"facts": []}
    claims = []
    observation_ids = _timpo_observation_ids(bundle.timpo_path)

    for fact in evidence.get("facts", []):
        node_id = str(fact.get("supports_domain_node", ""))
        surface_edges = _surface_edges_touching(surface.edges, node_id) if node_id in domain_node_ids else []
        source_ids = list(fact.get("source_observation_ids", [])) or observation_ids
        claim = {
            "id": fact.get("id"),
            "claim": fact.get("claim"),
            "source_observation": fact.get("source_observation"),
            "source_observation_ids": source_ids,
            "specific_observation_ids": source_ids,
            "domain_nodes": [node_id] if node_id else [],
            "domain_node_ids": [node_id] if node_id else [],
            "surface_edges": surface_edges,
            "surface_edge_ids": surface_edges,
            "value": fact.get("value"),
            "unit": fact.get("unit"),
            "value_metric": fact.get("value_metric"),
            "value_metric_ids_or_strings": [fact["value_metric"]] if fact.get("value_metric") else [],
            "derived_fields": {
                key: fact[key]
                for key in ["value", "unit", "value_metric"]
                if key in fact
            },
        }
        claim["lineage_hash"] = hash_data(claim)
        claims.append(claim)

    trace = {
        "path": [node_id for node_id in OPERATIONAL_NODE_PATH if node_id in domain_node_ids],
        "path_summary": _operational_path_summary(evidence, surface, bundle),
        "claims": claims,
    }
    trace["hash"] = hash_data(trace)
    return trace


def command_explain(bundle: FixtureBundle) -> dict[str, Any]:
    result = runtime_result(bundle)
    trace = result["because_trace"]
    return {
        "architectural_trace": {
            "because_trace": trace,
            "source_observations": trace["observations"],
            "domain_rules_used": trace["domain_nodes"],
            "surface_relationships_used": trace["surface_edges"],
            "profile": trace["profile"],
            "lens": trace["lens"],
            "value": trace["value"],
            "value_metrics": trace["value_metrics"],
        },
        "operational_trace": _operational_trace(bundle),
        "source_observations": trace["observations"],
        "domain_rules_used": trace["domain_nodes"],
        "surface_relationships_used": trace["surface_edges"],
        "profile": trace["profile"],
        "lens": trace["lens"],
        "value": trace["value"],
        "value_metrics": trace["value_metrics"],
    }


def command_diff(root: Path) -> dict[str, Any]:
    root = root.resolve()
    before = _find_one(root, "before.*")
    after = _find_one(root, "after.*")
    before_data = read_yaml(before)
    after_data = read_yaml(after)
    before_hash = hash_data(before_data)
    after_hash = hash_data(after_data)
    before_ids = {item["id"] for item in before_data.get("nodes", []) if "id" in item}
    after_ids = {item["id"] for item in after_data.get("nodes", []) if "id" in item}
    changed = []
    before_by_id = {item["id"]: item for item in before_data.get("nodes", []) if "id" in item}
    after_by_id = {item["id"]: item for item in after_data.get("nodes", []) if "id" in item}
    for node_id in sorted(before_ids & after_ids):
        if before_by_id[node_id] != after_by_id[node_id]:
            changed.append(node_id)
    return {
        "before_hash": before_hash,
        "after_hash": after_hash,
        "changed_layer": before.suffix.lstrip("."),
        "added_context_elements": sorted(after_ids - before_ids),
        "removed_context_elements": sorted(before_ids - after_ids),
        "changed_context_elements": changed,
        "policy_delta_explanation": "Policy/domain changes alter reconstructed context when affected meaning nodes change.",
    }


def command_agent_run(bundle: FixtureBundle, profile: str | None, lens: str | None) -> dict[str, Any]:
    if profile is None and len(bundle.profile_paths) > 1:
        raise ValueError("Multiple profiles found. Please pass --profile.")
    result = runtime_result(bundle, profile=profile, lens=lens)
    profile_path = selected_profile_path(bundle, profile)
    lens_path = selected_lens_path(bundle, lens)
    profile_data = read_yaml(profile_path)
    operational_trace = _operational_trace(bundle)
    path_summary = operational_trace["path_summary"]

    allowed_actions = list(profile_data.get("allowed_actions", []))
    restricted_action_names = list(profile_data.get("restricted_actions", []))
    proposed_action = allowed_actions[0] if allowed_actions else result["action_recommendation"]
    permission_result = "allowed" if proposed_action in allowed_actions else "approval_required"
    restricted_actions = [
        {"action": action, "permission_result": "approval_required"}
        for action in restricted_action_names
    ]
    source_hashes = {
        "timpo_hash": validate_timpos(bundle.timpo_path).get("hash"),
        "domain_hash": hash_data(read_yaml(bundle.domain_path)),
        "surface_hash": hash_data(read_yaml(bundle.surface_path)),
        "profile_hash": hash_data(profile_data),
        "lens_hash": hash_data(read_yaml(lens_path)),
        "value_hash": hash_data(read_yaml(bundle.value_path)) if bundle.value_path else None,
        "evidence_hash": hash_data(read_yaml(bundle.evidence_path)) if bundle.evidence_path else None,
    }
    action_result = {
        "proposed_action": proposed_action,
        "permission_result": permission_result,
        "restricted_actions": restricted_actions,
    }
    audit_event = {
        "initiated_by": result["profile_id"],
        "profile_id": result["profile_id"],
        "lens_id": result["lens_id"],
        "core_question": result["core_question"],
        "source_hashes": source_hashes,
        "path_hash": hash_data(path_summary),
        "action_result": action_result,
        "because_trace_hash": result["because_trace"]["hash"],
    }
    audit_event["hash"] = hash_data(audit_event)
    because = (
        "The same model delta path can be translated into a repeatable customer value story."
        if result["profile_id"] == "neara_value_architect"
        else "The model delta produced watch points that travel through clearance policy, wildfire risk, operational priority, crew hours, and cost exposure into SCE customer value."
    )
    agent_run = {
        "initiated_by": result["profile_id"],
        "profile_id": result["profile_id"],
        "lens_id": result["lens_id"],
        "core_question": result["core_question"],
        "path_summary": path_summary,
        "because": because,
        "action_result": action_result,
        "source_hashes": source_hashes,
        "path_hash": hash_data(path_summary),
        "because_trace_hash": result["because_trace"]["hash"],
        "audit_event": audit_event,
        "audit_event_hash": audit_event["hash"],
    }
    return {
        "agent_run": agent_run,
        "initiated_by": agent_run["initiated_by"],
        "profile_id": agent_run["profile_id"],
        "lens": agent_run["lens_id"],
        "lens_id": agent_run["lens_id"],
        "core_question": agent_run["core_question"],
        "proposed_action": action_result["proposed_action"],
        "permission_result": action_result["permission_result"],
        "restricted_actions": action_result["restricted_actions"],
        "path_summary": agent_run["path_summary"],
        "because": agent_run["because"],
        "source_hashes": agent_run["source_hashes"],
        "path_hash": agent_run["path_hash"],
        "action_result": agent_run["action_result"],
        "because_trace_hash": agent_run["because_trace_hash"],
        "audit_event": audit_event,
        "audit_event_hash": audit_event["hash"],
    }


def print_output(data: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(data, indent=2, sort_keys=True))
        return
    if "architectural_trace" in data and "operational_trace" in data:
        print_explain_output(data)
        return
    if "agent_run" in data:
        print_agent_run_output(data["agent_run"])
        return
    if "bundle_id" in data and "written_payloads" in data:
        print_ingest_output(data)
        return
    if data.get("command") == "source add":
        print_source_add_output(data)
        return
    if "architecture" in data and "included" in data and "excluded" in data:
        print_read_output(data)
        return
    if "proof_hash" in data and "checks" in data:
        print_audit_output(data)
        return
    for key, value in data.items():
        if isinstance(value, (dict, list)):
            print(f"{key}:")
            print(json.dumps(value, indent=2, sort_keys=True))
        else:
            print(f"{key}: {value}")


def _join_path(items: list[str]) -> str:
    return " -> ".join(items)


def print_explain_output(data: dict[str, Any]) -> None:
    architectural = data["architectural_trace"]
    operational = data["operational_trace"]
    print("Architectural Trace")
    print(f"Profile: {architectural['profile']}")
    print(f"Lens: {architectural['lens']}")
    print(f"Value: {architectural['value']}")
    print(f"Because trace hash: {architectural['because_trace']['hash']}")
    print()

    print("Operational Trace")
    for index, claim in enumerate(operational["claims"], start=1):
        print(f"{index}. {claim['claim']}")
        print(f"   Source: {claim['source_observation']}")
        print(f"   Meaning: {', '.join(claim['domain_nodes'])}")
        print(f"   Path: {_join_path(claim['surface_edges'])}")
        if claim.get("value") is not None:
            unit = f" {claim['unit']}" if claim.get("unit") else ""
            print(f"   Value: {claim['value']}{unit}")
        if claim.get("value_metric"):
            print(f"   Value metric: {claim['value_metric']}")
        print(f"   Lineage hash: {claim['lineage_hash']}")
    print()

    print("Operational Path")
    summary = operational["path_summary"]
    print(f"Start: {summary['start']}")
    print(f"End: {summary['end']}")
    print(f"Domain: {_join_path(summary['domain_path'])}")
    print(f"Surface: {_join_path(summary['surface_path'])}")
    print()

    print("Because")
    for metric in summary["value_metrics"]:
        print(f"- {metric}")


def print_agent_run_output(agent_run: dict[str, Any]) -> None:
    print(f"Profile: {agent_run['profile_id']}")
    print(f"Core Question: {agent_run['core_question']}")
    print(f"Lens: {agent_run['lens_id']}")
    print()
    print("Operational Path")
    print(f"Domain: {_join_path(agent_run['path_summary']['domain_path'])}")
    print(f"Surface: {_join_path(agent_run['path_summary']['surface_path'])}")
    print()
    print("Proposed Action:")
    action = agent_run["action_result"]
    print(f"- {action['proposed_action']}: {action['permission_result']}")
    print()
    print("Restricted Actions:")
    for item in action["restricted_actions"]:
        print(f"- {item['action']}: {item['permission_result']}")
    print()
    print("Because:")
    print(agent_run["because"])
    print()
    print("Audit Event:")
    print(agent_run["audit_event"]["hash"])


def print_ingest_output(data: dict[str, Any]) -> None:
    print("Intake Bundle")
    print(f"id: {data['bundle_id']}")
    print()

    print("Ledger")
    print(f"valid: {_json_scalar(data['ledger']['valid'])}")
    print(f"entries: {data['ledger']['entry_count']}")
    print()

    print("Written Payloads")
    for item in data["written_payloads"]:
        print(f"- {item['id']} {item['event']}: {item['entry_id']}")


def print_source_add_output(data: dict[str, Any]) -> None:
    print("Source Add")
    print(f"name: {data['name']}")
    print(f"kind: {data['kind']}")
    print()

    print("Created")
    for item in data["created"]:
        print(f"- {item}")
    print()

    print("Ledger")
    print(f"valid: {_json_scalar(data['ledger']['valid'])}")
    print(f"entries: {data['ledger']['entry_count']}")


def print_read_output(data: dict[str, Any]) -> None:
    print("Architecture")
    print(data["architecture"]["phrase"])
    print()

    print("Read Context")
    read_context = data["read_context"]
    print(f"profile: {read_context['profile']}")
    print(f"lens: {read_context['lens']}")
    print(f"core_question: {read_context['core_question']}")
    print()

    print("Ledger")
    ledger = data["ledger_chain"]
    print(f"valid: {_json_scalar(ledger['valid'])}")
    print(f"entries: {ledger['entry_count']}")
    print()

    print("Admission Trail")
    for item in data["admission_trail"]:
        print(f"- {item['id']} {item['event']}: {item['entry_id']}")
    print()

    print("Included Claims")
    for item in data["included"]:
        print(f"- {item['id']}")
        print(f"  reason: {item['reason']}")
        print(f"  validation: {item.get('validation_entry_id')}")
    print()

    print("Excluded Claims")
    for item in data["excluded"]:
        print(f"- {item['id']}")
        print(f"  reason: {item['reason']}")
        print(f"  validation: {item.get('validation_entry_id')}")
    print()

    print("Declared Contracts")
    for item in data["declared_contracts"]:
        print(f"- {item['id']} ({item['data']['contract_kind']}): {item['entry_id']}")
    print()

    print("Outputs")
    for item in data["outputs"]:
        output_data = item.get("data", {})
        print(f"- {item['id']}")
        print(f"  proposed_action: {output_data.get('proposed_action')}")
        print(f"  permission_result: {output_data.get('permission_result')}")
    print()

    print("Invariant")
    print(data["architecture"]["invariant"])
    print()
    print(f"Read projection hash: {data['projection_hash']}")


def print_audit_output(data: dict[str, Any]) -> None:
    print("Target")
    print(data["target"]["id"])
    print()

    print("Status")
    print(f"valid: {_json_scalar(data['valid'])}")
    print(f"active_context: {data['target_status']['active_context']}")
    if data["target_status"].get("reason"):
        print(f"reason: {data['target_status']['reason']}")
    print()

    permissions = data["checks"].get("profile_permissions", {})
    if data["target"]["type"] == "output" and permissions.get("status") != "not_applicable":
        print("Generated Output")
        print(f"proposed_action: {permissions.get('proposed_action')}")
        print(f"permission_result: {permissions.get('permission_result')}")
        print()

        print("Profile Permission")
        profile = permissions.get("profile", {})
        print(f"profile: {profile.get('id')}")
        allowed = permissions.get("allowed_actions", [])
        if allowed:
            print(f"allowed: {', '.join(allowed)}")
        print("restricted:")
        for item in permissions.get("restricted_actions", []):
            print(f"- {item['action']}: {item['permission_result']}")
        print()

    if _has_projection_mismatch(data):
        print("Projection Replay")
        print("This audit included a claimed projection. The independent replay did not match it.")
        print("Detailed projection diff is not implemented yet. See AUDIT-006.")
        print()

    print()
    print("Checks")
    for name, check in data["checks"].items():
        if isinstance(check, dict):
            print(f"{name}: {check['status']}")
        else:
            print(f"{name}: {check}")
    print()

    print("Because")
    print(_audit_because(data))
    print()
    print(f"Proof hash: {data['proof_hash']}")


def _json_scalar(value: Any) -> str:
    return json.dumps(value)


def _has_projection_mismatch(data: dict[str, Any]) -> bool:
    read_replay = data["checks"].get("read_replay", {})
    return read_replay.get("status") == "fail" and read_replay.get("matches") is False


def _audit_because(data: dict[str, Any]) -> str:
    target_type = data["target"]["type"]
    active_context = data["target_status"]["active_context"]
    if target_type == "claim" and active_context == "included":
        return "The claim was interpreted, validated admissible true, included by READ, and the ledger/payload hashes verified."
    if target_type == "claim" and active_context == "excluded":
        return "The claim exists historically, but latest validation marks admissible false, so READ excludes it from active context."
    if target_type == "output":
        permissions = data["checks"].get("profile_permissions", {})
        profile = permissions.get("profile", {}).get("id")
        action = permissions.get("proposed_action")
        return (
            f"The generated output resolved to a ledger payload, referenced {profile}, "
            f"and the proposed action {action} is allowed by that profile."
        )
    return data["target_status"].get("reason", "Audit checks were evaluated against the ledger proof.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m corus", description="Interactive Corus engine playground.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ["validate", "reconstruct", "explain", "diff"]:
        child = sub.add_parser(name)
        child.add_argument("fixture", type=Path)
        child.add_argument("--json", action="store_true", help="Print JSON output.")
    write = sub.add_parser("write")
    write.add_argument("payload", type=Path)
    write.add_argument("--timpo")
    write.add_argument("--json", action="store_true", help="Print JSON output.")
    ingest = sub.add_parser("ingest")
    ingest.add_argument("bundle", type=Path)
    ingest.add_argument("--out", required=True, type=Path)
    ingest.add_argument("--json", action="store_true", help="Print JSON output.")
    source = sub.add_parser("source")
    source_sub = source.add_subparsers(dest="source_command", required=True)
    source_add = source_sub.add_parser("add")
    source_add.add_argument("--name", required=True)
    source_add.add_argument("--ref", required=True)
    source_add.add_argument("--kind", required=True)
    source_add.add_argument("--out", required=True, type=Path)
    source_add.add_argument("--admit", action="store_true")
    source_add.add_argument("--json", action="store_true", help="Print JSON output.")
    project = sub.add_parser("project")
    project.add_argument("fixture", type=Path)
    project.add_argument("--profile")
    project.add_argument("--lens")
    project.add_argument("--json", action="store_true", help="Print JSON output.")
    read = sub.add_parser("read")
    read.add_argument("fixture", type=Path)
    read.add_argument("--profile")
    read.add_argument("--lens")
    read.add_argument("--json", action="store_true", help="Print JSON output.")
    audit = sub.add_parser("audit")
    audit.add_argument("fixture", type=Path)
    audit.add_argument("--target", required=True)
    audit.add_argument("--profile")
    audit.add_argument("--lens")
    audit.add_argument("--json", action="store_true", help="Print JSON output.")
    agent = sub.add_parser("agent-run")
    agent.add_argument("fixture", type=Path)
    agent.add_argument("--profile")
    agent.add_argument("--lens")
    agent.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    as_json = bool(getattr(args, "json", False))
    if args.command == "write":
        print_output(command_write(args.payload, args.timpo), as_json)
        return
    if args.command == "ingest":
        print_output(command_ingest(args.bundle, args.out), as_json)
        return
    if args.command == "source":
        if args.source_command == "add":
            print_output(add_source(args.name, args.ref, args.kind, args.out, args.admit), as_json)
            return
        raise SystemExit(f"unknown source command {args.source_command}")
    if args.command == "diff":
        print_output(command_diff(args.fixture), as_json)
        return
    bundle = load_bundle(args.fixture)
    if args.command == "validate":
        output = validate_bundle(bundle)
    elif args.command == "reconstruct":
        output = command_reconstruct(bundle)
    elif args.command == "project":
        output = command_project(bundle, args.profile, args.lens)
    elif args.command == "read":
        output = command_read(bundle, args.profile, args.lens)
    elif args.command == "audit":
        output = command_audit(bundle, args.target, args.profile, args.lens)
    elif args.command == "explain":
        output = command_explain(bundle)
    elif args.command == "agent-run":
        output = command_agent_run(bundle, args.profile, args.lens)
    else:
        raise SystemExit(f"unknown command {args.command}")
    print_output(output, as_json)
