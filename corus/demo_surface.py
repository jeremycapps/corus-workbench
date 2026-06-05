from __future__ import annotations

import argparse
import html
import json
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable

from kernel.engine.hashing import hash_data
from kernel.verify.hash import read_yaml


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = Path("tests/fixtures/sce_vegetation")
BUNDLE = Path("bundles/sce_vegetation/corus.bundle.yaml")
TITLE = "Neara / SCE Value Translation Demo"
SOURCE_STATUS = "demo-synthetic / internally hash-backed / source-authority missing where applicable"
TRUST_BANNER = (
    "public-source grounded scenario with synthetic fixture data. This is not an official Neara export or SCE operating model. "
    "Public sources ground the implementation context; the 72-watch-point count and cost assumptions remain synthetic or rejected where applicable."
)
OPERATIONAL_EXPLANATION = (
    "Broad risk intelligence becomes customer-specific implementation context by moving through policy interpretation, "
    "watch-point classification, wildfire risk, operational priority, crew planning, cost exposure, and customer value."
)
HERO_HEADLINE = "When risk models change, customer implementation changes."
HERO_SUBHEAD = (
    "This proof-of-work uses public SCE wildfire mitigation materials and Neara's public RVO framing to show how broad "
    "risk intelligence becomes customer-specific implementation context: affected workstreams, stakeholder questions, "
    "evidence needs, rejected assumptions, and defensible next actions."
)

CommandRunner = Callable[[list[str]], dict[str, Any]]


def _run_corus_json(args: list[str], root: Path = ROOT) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, "-m", "corus", *args, "--json"],
        cwd=root,
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(completed.stdout)


def load_demo_data(root: Path = ROOT, runner: CommandRunner | None = None) -> dict[str, Any]:
    run = runner or (lambda args: _run_corus_json(args, root=root))
    fixture = str(FIXTURE)
    return {
        "manifest": read_yaml(root / BUNDLE),
        "explain": run(["explain", fixture]),
        "sce_grid_ops": run(["agent-run", fixture, "--profile", "sce_grid_ops", "--lens", "vegetation_ops"]),
        "neara_value_architect": run(
            ["agent-run", fixture, "--profile", "neara_value_architect", "--lens", "vegetation_ops"]
        ),
        "audit_watch_points": run(["audit", fixture, "--target", "claim.sce.watch_points_added"]),
        "audit_unsupported_cost": run(["audit", fixture, "--target", "claim.sce.unsupported_cost_assumption"]),
        "audit_work_packet": run(["audit", fixture, "--target", "output.sce_grid_ops.work_packet"]),
    }


def build_demo_model(data: dict[str, Any]) -> dict[str, Any]:
    manifest = data.get("manifest", {})
    ui_copy = manifest.get("ui_copy", {})
    ui_hero = ui_copy.get("hero", {})
    source_context = manifest.get("source_context", {})
    sources = [_decorate_source(source) for source in manifest.get("sources", [])]
    public_sources = [source for source in sources if "public_source" in source.get("trust_status", [])]
    synthetic_sources = [source for source in sources if "demo_synthetic" in source.get("trust_status", [])]
    facts = [_decorate_fact(fact, sources) for fact in manifest.get("facts", [])]
    stakeholder_views = list(manifest.get("stakeholder_views", []))
    implementation_output = _manifest_output(manifest, "output.implementation_context_trace")
    implementation_data = implementation_output.get("data", {})
    implementation_summary = implementation_data.get("decision_summary", {})
    explain = data["explain"]
    operational = explain["operational_trace"]
    claims = {claim["id"]: claim for claim in operational["claims"]}
    watch_claim = claims["fact.watch_points.added"]
    cost_claim = claims["fact.cost.validation_exposure"]
    customer_value_claim = claims["fact.cost.customer_value"]
    product_pattern_claim = claims["fact.neara.repeatable_pattern"]

    audits = {
        "admitted_claim": _audit_summary(data["audit_watch_points"]),
        "rejected_claim": _audit_summary(data["audit_unsupported_cost"]),
        "work_packet": _audit_summary(data["audit_work_packet"]),
    }
    return {
        "title": TITLE,
        "headline": ui_hero.get("headline", HERO_HEADLINE),
        "subhead": ui_hero.get("subhead", HERO_SUBHEAD),
        "source_status": SOURCE_STATUS,
        "trust_banner": TRUST_BANNER,
        "source_context": source_context,
        "sources": sources,
        "public_sources": public_sources,
        "synthetic_sources": synthetic_sources,
        "facts": facts,
        "implementation_details": _implementation_detail_cards(),
        "stakeholder_views": stakeholder_views,
        "source_boundary": {
            "status": source_context.get("status", TRUST_BANNER),
            "public_context_sources": public_sources,
            "synthetic_fixture_sources": synthetic_sources,
            "bounded_claims": list(source_context.get("bounded_claims", [])),
        },
        "framing": (
            "This does not replace Neara's model. It starts from a Neara-style model output "
            "and translates it into customer-specific value, action, and audit proof."
        ),
        "operational_explanation": OPERATIONAL_EXPLANATION,
        "input_model_delta": {
            "type": "Neara-style model output",
            "label": "72 vegetation watch points",
            "claim": watch_claim["claim"],
            "value": watch_claim["value"],
            "unit": watch_claim["unit"],
            "source_observation": watch_claim["source_observation"],
            "trust": "demo-synthetic / demo_model_output",
        },
        "operational_path": operational["path_summary"]["domain_path"],
        "surface_path": operational["path_summary"]["surface_path"],
        "story_ladder": [
            "Model result",
            "Policy interpretation",
            "Watch-point classification",
            "Risk framing",
            "Operational priority",
            "Crew planning",
            "Cost exposure",
            "Customer value",
        ],
        "outcome_metrics": [
            *implementation_data.get(
                "metric_cards",
                [
                    {"value": "Public context", "label": "source-grounded scenario"},
                    {"value": "72", "label": "synthetic watch points translated"},
                    {"value": "1", "label": "recommended action"},
                    {"value": "Audit proof", "label": "available"},
                ],
            )
        ],
        "decision_summary": {
            "what_changed": "Broad risk intelligence exists",
            "why_it_matters": implementation_summary.get(
                "why_it_matters",
                "The customer needs significance before intelligence becomes action",
            ),
            "customer_value": implementation_summary.get(
                "customer_value",
                "Implementation context for each stakeholder",
            ),
            "recommended_action": implementation_summary.get(
                "recommended_action",
                "Generate implementation context trace",
            ),
            "trust_status": implementation_summary.get(
                "trust_status",
                "Public-source grounded · synthetic fixture bounded · rejected cost assumption preserved",
            ),
        },
        "workflow": [
            {
                "step": "1",
                "title": "Start with the model output",
                "body": "Treat the 72 vegetation watch points as synthetic fixture output from a Neara-style model delta.",
            },
            {
                "step": "2",
                "title": "Ask the customer-value question",
                "body": "Use public SCE/Neara context to ask what workstream, stakeholder, evidence, and action boundary changes.",
            },
            {
                "step": "3",
                "title": "Evaluate the defensible action",
                "body": "Generate a work packet, preserve rejected assumptions, and expose audit proof when needed.",
            },
        ],
        "action_options": [
            {
                "option": "Generate work packet",
                "action_id": "generate_work_packet",
                "purpose": "Plan validation work from the 72 watch points",
                "status": "Recommended / Allowed",
                "trust": "Allowed by SCE Grid Ops profile",
            },
            {
                "option": "Estimate crew hours",
                "action_id": "estimate_crew_hours",
                "purpose": "Translate watch points into workforce planning",
                "status": "Allowed",
                "trust": "Demo assumption; source authority pending",
            },
            {
                "option": "Flag budget exposure",
                "action_id": "flag_budget_exposure",
                "purpose": "Surface potential budget impact",
                "status": "Allowed",
                "trust": "Budget exposure is illustrative",
            },
            {
                "option": "Dispatch crew",
                "action_id": "dispatch_crew",
                "purpose": "Execute field work",
                "status": "Approval required",
                "trust": "Restricted action",
            },
            {
                "option": "Approve budget change",
                "action_id": "approve_budget_change",
                "purpose": "Commit spend",
                "status": "Approval required",
                "trust": "Unsupported cost claim rejected",
            },
        ],
        "output": {
            "title": "SCE operational value",
            "items": [
                "workforce planning",
                "budget exposure",
                "operational priority",
                "customer value story",
            ],
        },
        "roles": [
            _role_summary("SCE Grid Ops", data["sce_grid_ops"]["agent_run"]),
            _role_summary("Neara Value Architect", data["neara_value_architect"]["agent_run"]),
        ],
        "value_story": {
            "customer_value": customer_value_claim["claim"],
            "product_pattern": product_pattern_claim["claim"],
            "because": data["sce_grid_ops"]["agent_run"]["because"],
            "value_metrics": operational["path_summary"]["value_metrics"],
        },
        "evidence_status": {
            "admitted_claim": {
                "id": "claim.sce.watch_points_added",
                "claim": watch_claim["claim"],
                "status": data["audit_watch_points"]["status"],
                "trust": "source-labeled / demo-synthetic",
            },
            "rejected_claim": {
                "id": "claim.sce.unsupported_cost_assumption",
                "claim": _first_excluded_claim(data["audit_unsupported_cost"]),
                "status": data["audit_unsupported_cost"]["status"],
                "trust": "demo-synthetic / source-authority missing",
            },
            "synthetic_assumptions": [
                cost_claim["claim"],
                "Customer value and product-pattern statements are fixture-defined demo assumptions.",
            ],
        },
        "audit_proofs": audits,
        "proves": ui_copy.get(
            "what_this_demo_proves",
            [
                "A model output can be translated into a customer-facing decision.",
                "Claims can be admitted or rejected.",
                "Recommended actions can be checked against role permissions.",
                "Audit proof can explain why a claim or action was included, excluded, or allowed.",
            ],
        ),
        "out_of_scope": ui_copy.get(
            "out_of_scope",
            [
                "Official Neara export verification.",
                "Externally approved SCE operating model.",
                "Actual SCE cost exposure.",
                "Replacement of Neara's grid modeling, LiDAR, GIS, or simulation pipeline.",
            ],
        ),
    }


def _role_summary(label: str, agent_run: dict[str, Any]) -> dict[str, Any]:
    action_result = agent_run["action_result"]
    return {
        "label": label,
        "profile_id": agent_run["profile_id"],
        "core_question": agent_run["core_question"],
        "output": _role_output(agent_run["profile_id"]),
        "proposed_action": action_result["proposed_action"],
        "proposed_action_label": _human_action(action_result["proposed_action"]),
        "permission_result": action_result["permission_result"],
        "allowed_actions": action_result.get("allowed_actions") or _default_allowed_actions(agent_run["profile_id"]),
        "restricted_actions": action_result["restricted_actions"],
        "audit_event_hash": agent_run["audit_event_hash"],
    }


def _role_output(profile_id: str) -> str:
    if profile_id == "sce_grid_ops":
        return "Work packet recommendation"
    if profile_id == "neara_value_architect":
        return "Customer value story"
    return "Translated customer output"


def _default_allowed_actions(profile_id: str) -> list[str]:
    if profile_id == "sce_grid_ops":
        return ["generate_work_packet", "estimate_crew_hours", "flag_budget_exposure"]
    if profile_id == "neara_value_architect":
        return ["generate_value_story", "identify_repeatable_pattern", "prepare_customer_demo"]
    return []


def _human_action(action: str) -> str:
    return action.replace("_", " ").capitalize()


def _decorate_source(source: dict[str, Any]) -> dict[str, Any]:
    source_id = str(source.get("id", ""))
    labels = {
        "source.demo_model_output": "Synthetic Neara-style model output",
        "source.neara_risk_impact_scoring": "Neara RVO / risk impact scoring",
        "source.neara_risk_prioritization_case_study": "Neara risk prioritization case study",
        "source.neara_pole_replacement_case_study": "Neara pole replacement case study",
        "source.sce_2025_wmp_update": "SCE 2025 WMP update",
    }
    decorated = dict(source)
    decorated["label"] = labels.get(source_id, source_id)
    return decorated


def _manifest_output(manifest: dict[str, Any], output_id: str) -> dict[str, Any]:
    for output in manifest.get("outputs", []):
        if output.get("id") == output_id:
            return output
    return {}


def _decorate_fact(fact: dict[str, Any], sources: list[dict[str, Any]]) -> dict[str, Any]:
    source_labels = {source.get("id"): source.get("label", source.get("id", "")) for source in sources}
    decorated = dict(fact)
    decorated["lineage_hash"] = hash_data(fact)
    decorated["source_labels"] = [
        source_labels.get(source_id, source_id)
        for source_id in fact.get("source_context_ids", [])
    ]
    return decorated


def _implementation_detail_cards() -> list[dict[str, Any]]:
    return [
        {
            "id": "detail.asset_inspection_prioritization",
            "title": "Asset inspection prioritization",
            "what_changed": "Refreshed risk-model outputs may affect inspection strategy and prioritization.",
            "who_needs_this": ["Grid Ops", "Customer Success", "Regulatory"],
            "source_ids": ["source.sce_2025_wmp_update"],
            "still_unknown": [
                "Customer-approved inspection schedule",
                "Field execution owner",
                "Data handoff path",
            ],
            "next_validation_step": "Confirm whether refreshed risk intelligence changes inspection prioritization for the target account.",
            "trace_status": ["public_source", "source_labeled"],
            "related_fact_ids": ["fact.sce.risk_model_outputs_affect_workstreams"],
        },
        {
            "id": "detail.vegetation_management_scope",
            "title": "Vegetation management scope",
            "what_changed": "Risk outputs may affect vegetation management scope and review attention.",
            "who_needs_this": ["Grid Ops", "Finance", "Regulatory"],
            "source_ids": ["source.sce_2025_wmp_update"],
            "still_unknown": [
                "Official work order scope",
                "Crew assumptions",
                "Approved cost model",
            ],
            "next_validation_step": "Identify which operating assumptions are customer-provided versus modeled or synthetic.",
            "trace_status": ["public_source", "source_labeled", "synthetic_fixture_bounded"],
            "related_fact_ids": ["fact.sce.risk_model_outputs_affect_workstreams"],
        },
        {
            "id": "detail.system_hardening_schedule",
            "title": "System hardening schedule",
            "what_changed": "Risk intelligence may influence hardening scoping or schedules.",
            "who_needs_this": ["Executive Sponsor", "Finance", "Regulatory", "Implementation Team"],
            "source_ids": ["source.sce_2025_wmp_update"],
            "still_unknown": [
                "Approved capital-plan decision",
                "Regulatory evidence packet",
                "Schedule commitment",
            ],
            "next_validation_step": "Separate near-term implementation action from multi-year planning implication.",
            "trace_status": ["public_source", "source_labeled"],
            "related_fact_ids": ["fact.sce.risk_model_outputs_affect_workstreams"],
        },
        {
            "id": "detail.unsupported_cost_amount",
            "title": "Unsupported cost amount",
            "what_changed": "A specific dollar impact was attempted but cannot be supported by the available public sources.",
            "who_needs_this": ["Finance", "Regulatory", "Customer Success"],
            "source_ids": ["source.neara_pole_replacement_case_study"],
            "still_unknown": [
                "Customer-approved cost model",
                "Approved labor assumptions",
                "Budget owner confirmation",
            ],
            "next_validation_step": "Reject the cost amount until customer-approved assumptions exist.",
            "trace_status": ["rejected_assumption", "source_authority_missing"],
            "related_fact_ids": ["fact.customer.unsupported_specific_cost"],
        },
    ]


def _audit_summary(proof: dict[str, Any]) -> dict[str, Any]:
    checks = proof["checks"]
    return {
        "target": proof["target"]["id"],
        "valid": proof["valid"],
        "status": proof["status"],
        "proof_hash": proof["proof_hash"],
        "checks": {
            "ledger_chain": checks["ledger_chain"]["status"],
            "payload_hashes": checks["payload_hashes"]["status"],
            "admissibility": checks["admissibility"]["status"],
            "profile_permissions": checks["profile_permissions"]["status"],
        },
    }


def _first_excluded_claim(proof: dict[str, Any]) -> str:
    excluded = proof.get("excluded") or []
    if not excluded:
        return "Unsupported cost assumption was rejected."
    return str(excluded[0].get("claim", "Unsupported cost assumption was rejected."))


def render_demo_html(model: dict[str, Any]) -> str:
    audit_cards = "\n".join(_render_audit(name, proof) for name, proof in model["audit_proofs"].items())
    outcome_metrics = "\n".join(_render_outcome_metric(metric) for metric in model["outcome_metrics"])
    source_lookup = {source.get("id"): source for source in model["sources"]}
    fact_lookup = {fact.get("id"): fact for fact in model["facts"]}
    implementation_detail_cards = "\n".join(
        _render_implementation_detail_card(detail, source_lookup, fact_lookup)
        for detail in model["implementation_details"]
    )
    public_source_cards = "\n".join(_render_source_card(source) for source in model["public_sources"])
    synthetic_source_cards = "\n".join(_render_source_card(source) for source in model["synthetic_sources"])
    bounded_claims = "".join(f"<li>{_esc(claim)}</li>" for claim in model["source_boundary"]["bounded_claims"])
    fact_cards = "\n".join(_render_fact_card(fact) for fact in model["facts"])
    stakeholder_cards = "\n".join(_render_stakeholder_card(stakeholder) for stakeholder in model["stakeholder_views"])
    proves = "".join(f"<li>{_esc(item)}</li>" for item in model["proves"])
    out_of_scope = "".join(f"<li>{_esc(item)}</li>" for item in model["out_of_scope"])
    proof_hash_items = "".join(
        f"<li>{_esc(label.replace('_', ' ').title())}: <code>{_esc(proof['proof_hash'])}</code></li>"
        for label, proof in model["audit_proofs"].items()
    )
    legacy_domain_path = "".join(f"<li>{_esc(node)}</li>" for node in model["operational_path"])
    legacy_surface_path = "".join(f"<li>{_esc(edge)}</li>" for edge in model["surface_path"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{_esc(model["title"])}</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #08171f;
      --muted: #5b6770;
      --line: #d9e1db;
      --panel: #ffffff;
      --wash: #f2f5f2;
      --accent: #2f7d69;
      --accent-strong: #1f5f50;
      --accent-soft: #dff7e8;
      --signal: #c7ff4f;
      --signal-soft: #f1ffd2;
      --blue: #264a73;
      --blue-soft: #dcefff;
      --warn: #9a5b13;
      --warn-soft: #fff3d6;
      --bad: #9a3412;
      --bad-soft: #ffe2d5;
      --dark: #08171f;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: var(--wash);
      line-height: 1.45;
    }}
    header, section {{ padding: 28px max(24px, calc((100vw - 1120px) / 2)); }}
    header {{ background: var(--dark); color: white; }}
    h1 {{ margin: 0 0 12px; font-size: clamp(2.2rem, 5vw, 4.8rem); line-height: 1.02; letter-spacing: 0; max-width: 980px; }}
    h2 {{ margin: 0 0 14px; font-size: 1.45rem; letter-spacing: 0; }}
    h3 {{ margin: 0 0 8px; font-size: 1rem; letter-spacing: 0; }}
    p {{ margin: 0 0 12px; }}
    ul, ol {{ margin: 0; padding-left: 22px; }}
    li {{ margin: 6px 0; }}
    code {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
    .hero-copy {{ max-width: 900px; font-size: 1.13rem; color: #d9e7ee; }}
    .status-row {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 18px; }}
    .pill {{ display: inline-flex; align-items: center; min-height: 28px; border-radius: 999px; padding: 4px 10px; font-size: .84rem; font-weight: 650; background: var(--accent-soft); color: var(--accent); }}
    .pill-signal {{ background: var(--signal); color: var(--dark); }}
    .pill-public {{ background: var(--accent-soft); color: var(--accent-strong); }}
    .pill-synthetic {{ background: #edf0ef; color: var(--muted); }}
    .pill-blue {{ background: var(--blue-soft); color: var(--blue); }}
    .pill-warn {{ background: var(--warn-soft); color: var(--warn); }}
    .pill-bad {{ background: var(--bad-soft); color: var(--bad); }}
    header .pill {{ background: rgba(255,255,255,.12); color: white; border: 1px solid rgba(255,255,255,.22); }}
    header .pill-signal {{ background: var(--signal); color: var(--dark); border-color: var(--signal); }}
    .grid {{ display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); }}
    .card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 18px; box-shadow: 0 1px 2px rgba(15, 23, 42, .04); }}
    .notice {{ background: #fffaf0; border: 1px solid #ead5aa; border-radius: 8px; padding: 12px 14px; color: #5e4312; font-size: .94rem; }}
    .receipt {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 22px; box-shadow: 0 10px 30px rgba(16, 32, 43, .08); }}
    .receipt-head {{ display: flex; justify-content: space-between; align-items: start; gap: 16px; flex-wrap: wrap; margin-bottom: 16px; }}
    .receipt-title {{ margin: 0; font-size: 1.8rem; }}
    .receipt-grid {{ display: grid; gap: 14px; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); }}
    .receipt-item {{ background: var(--wash); border: 1px solid var(--line); border-radius: 8px; padding: 14px; }}
    .receipt-label {{ color: var(--muted); font-size: .84rem; font-weight: 720; text-transform: uppercase; }}
    .receipt-value {{ margin-top: 8px; font-size: 1.15rem; font-weight: 760; }}
    .metric-strip {{ display: grid; gap: 14px; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }}
    .outcome-card {{ display: block; text-decoration: none; color: var(--ink); background: white; border: 1px solid var(--line); border-radius: 8px; padding: 18px; min-height: 120px; transition: border-color .15s ease, transform .15s ease; }}
    .outcome-card:hover {{ border-color: var(--accent); transform: translateY(-1px); }}
    .outcome-value {{ color: var(--accent); font-size: 2.4rem; line-height: 1; font-weight: 820; margin-bottom: 10px; }}
    .outcome-label {{ color: var(--ink); font-weight: 720; }}
    .io-grid {{ display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); margin-top: 16px; }}
    .io-card {{ border: 1px solid var(--line); border-radius: 8px; padding: 18px; background: white; }}
    .metric {{ font-size: 3rem; line-height: 1; font-weight: 780; color: var(--accent); margin: 6px 0; }}
    .metric-text {{ font-size: 2.1rem; line-height: 1.08; font-weight: 780; color: var(--accent); margin: 8px 0 12px; }}
    .muted {{ color: var(--muted); }}
    .ladder {{ counter-reset: step; list-style: none; padding: 0; display: grid; gap: 8px; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }}
    .ladder li {{ display: flex; gap: 10px; align-items: center; padding: 11px 12px; border: 1px solid var(--line); border-radius: 8px; background: white; }}
    .ladder li::before {{ counter-increment: step; content: counter(step); flex: 0 0 26px; height: 26px; display: inline-grid; place-items: center; border-radius: 999px; background: var(--accent-soft); color: var(--accent); font-weight: 700; font-size: .82rem; }}
    .role-title {{ display: flex; justify-content: space-between; gap: 12px; align-items: start; }}
    .hash {{ overflow-wrap: anywhere; font-size: .82rem; color: var(--muted); }}
    .checks {{ display: grid; gap: 8px; grid-template-columns: repeat(auto-fit, minmax(132px, 1fr)); margin-top: 10px; }}
    .check {{ padding: 8px 10px; border-radius: 8px; background: var(--wash); border: 1px solid var(--line); }}
    .source-card {{ background: white; border: 1px solid var(--line); border-radius: 8px; padding: 14px; }}
    .source-public {{ border-color: #b9d9ca; }}
    .source-synthetic {{ background: #fafbfa; }}
    .source-card-head {{ display: flex; justify-content: space-between; align-items: start; gap: 12px; }}
    .source-card h3 {{ margin-bottom: 4px; }}
    .source-meta {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }}
    .source-actions {{ display: flex; flex-wrap: wrap; gap: 12px; align-items: center; margin-top: 12px; }}
    .source-actions a {{ color: var(--blue); font-weight: 760; text-decoration: none; }}
    .source-actions a:hover {{ text-decoration: underline; }}
    .fact-card {{ background: white; border: 1px solid var(--line); border-radius: 8px; padding: 18px; }}
    .fact-head {{ display: flex; justify-content: space-between; align-items: start; gap: 12px; }}
    .implementation-card {{ background: white; border: 1px solid var(--line); border-radius: 8px; padding: 20px; min-height: 260px; }}
    .implementation-card h3 {{ font-size: 1.15rem; }}
    .implementation-use {{ border-left: 3px solid var(--signal); padding-left: 12px; margin: 14px 0; }}
    .chips {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }}
    .pass {{ color: var(--accent); font-weight: 700; }}
    .not-applicable {{ color: var(--muted); font-weight: 700; }}
    .warn {{ background: var(--warn-soft); color: var(--warn); }}
    .bad {{ background: var(--bad-soft); color: var(--bad); }}
    .split {{ display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }}
    .workflow {{ display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); }}
    .workflow-step {{ background: white; border: 1px solid var(--line); border-radius: 8px; padding: 18px; }}
    .step-number {{ display: inline-grid; place-items: center; width: 34px; height: 34px; border-radius: 999px; background: var(--accent-soft); color: var(--accent); font-weight: 820; margin-bottom: 12px; }}
    table {{ width: 100%; border-collapse: collapse; background: white; border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }}
    th, td {{ text-align: left; vertical-align: top; padding: 12px; border-bottom: 1px solid var(--line); }}
    th {{ color: var(--muted); font-size: .82rem; text-transform: uppercase; letter-spacing: .02em; background: var(--wash); }}
    tr:last-child td {{ border-bottom: 0; }}
    details {{ margin-top: 14px; border-top: 1px solid var(--line); padding-top: 12px; }}
    summary {{ cursor: pointer; font-weight: 720; color: var(--blue); }}
    pre {{ white-space: pre-wrap; overflow-wrap: anywhere; background: #101820; color: #ecf3f7; padding: 12px; border-radius: 8px; font-size: .78rem; }}
    footer {{ padding: 24px max(24px, calc((100vw - 1120px) / 2)); color: var(--muted); }}
    @media (max-width: 760px) {{ header, section {{ padding: 22px 18px; }} .metric {{ font-size: 2.4rem; }} .metric-text {{ font-size: 1.7rem; }} }}
  </style>
</head>
<body>
  <header>
    <h1>{_esc(model["headline"])}</h1>
    <p class="hero-copy">{_esc(model["subhead"])}</p>
    <div class="status-row">
      <span class="pill pill-public">Public-source context</span>
      <span class="pill pill-synthetic">Synthetic fixture bounded</span>
      <span class="pill">No RVO replacement</span>
      <span class="pill pill-signal">Audit proof available</span>
    </div>
  </header>

  <section>
    <div class="metric-strip">{outcome_metrics}</div>
  </section>

  <section id="implementation-details">
    <h2>Implementation details surfaced from broad intelligence</h2>
    <p class="muted">Each card is a customer-specific detail that an implementation team would need to validate, explain, or hand off.</p>
    <div class="grid">{implementation_detail_cards}</div>
  </section>

  <section>
    <div class="notice">{_esc(model["trust_banner"])}</div>
  </section>

  <section id="source-boundary">
    <h2>Source boundary</h2>
    <p class="muted">Public-source grounded context shapes the implementation story. The synthetic fixture supplies the 72-watch-point count, and the unsupported cost assumption is rejected rather than treated as source-backed fact.</p>
    <p class="muted">Status: {_esc(model["source_status"])}</p>
    <div class="grid">
      <div class="card">
        <h3>Public context sources</h3>
        <div class="grid">{public_source_cards}</div>
      </div>
      <div class="card">
        <h3>Synthetic fixture</h3>
        <div class="grid">{synthetic_source_cards}</div>
      </div>
      <div class="card">
        <h3>Boundary notes</h3>
        <p class="muted">{_esc(model["source_boundary"]["status"])}</p>
        <ul>{bounded_claims}</ul>
      </div>
    </div>
  </section>

  <section id="decision-summary">
    <div class="receipt">
      <div class="receipt-head">
        <div>
          <h2 class="receipt-title">Decision Summary</h2>
          <p class="muted">Broad intelligence becomes customer-specific significance: what changed, who cares, what evidence is trusted, what assumptions are rejected, and what action is defensible.</p>
        </div>
        <span class="pill pill-signal">{_esc(model["decision_summary"]["trust_status"])}</span>
      </div>
      <div class="receipt-grid">
        <div class="receipt-item">
          <div class="receipt-label">What changed?</div>
          <div class="receipt-value">{_esc(model["decision_summary"]["what_changed"])}</div>
        </div>
        <div class="receipt-item">
          <div class="receipt-label">Why it matters</div>
          <div class="receipt-value">{_esc(model["decision_summary"]["why_it_matters"])}</div>
        </div>
        <div class="receipt-item">
          <div class="receipt-label">Customer value</div>
          <div class="receipt-value">{_esc(model["decision_summary"]["customer_value"])}</div>
        </div>
        <div class="receipt-item">
          <div class="receipt-label">Recommended action</div>
          <div class="receipt-value">{_esc(model["decision_summary"]["recommended_action"])}</div>
        </div>
        <div class="receipt-item">
          <div class="receipt-label">Trust status</div>
          <div class="receipt-value">{_esc(model["decision_summary"]["trust_status"])}</div>
        </div>
      </div>
    </div>
  </section>

  <section id="stakeholder-questions">
    <h2>Stakeholder questions</h2>
    <p class="muted">The same intelligence creates different questions depending on who needs to act, defend, fund, or implement.</p>
    <div class="grid">{stakeholder_cards}</div>
  </section>

  <section id="facts">
    <h2>Trace evidence behind the implementation details</h2>
    <p class="muted">These are the source-backed or rejected claims that support the implementation-detail cards above.</p>
    <div class="grid">{fact_cards}</div>
  </section>

  <section id="decision-confidence">
    <h2>Decision Confidence</h2>
    <div class="grid">
      <div class="card">
        <h3>Public context included</h3>
        <p>Neara RVO framing and SCE wildfire-planning context remain visible as source-bounded context.</p>
        <span class="pill pill-public">Included</span>
      </div>
      <div class="card">
        <h3>Unsupported cost rejected</h3>
        <p>Specific cost impact is rejected unless customer-approved cost evidence exists.</p>
        <span class="pill pill-bad">Rejected assumption</span>
      </div>
      <div class="card">
        <h3>Next action allowed</h3>
        <p>Generate implementation context trace is the source-bounded next action.</p>
        <span class="pill pill-signal">Allowed</span>
      </div>
    </div>
  </section>

  <section id="audit-proof">
    <h2>Can this be defended?</h2>
    <p class="muted">Yes: the trace separates public-source context, synthetic fixture data, rejected assumptions, and allowed next action.</p>
    <div class="grid">
      <div class="card">
        <h3>Public context included</h3>
        <span class="pill pill-public">Included</span>
      </div>
      <div class="card">
        <h3>Unsupported cost rejected</h3>
        <span class="pill pill-bad">Rejected</span>
      </div>
      <div class="card">
        <h3>Next action allowed</h3>
        <span class="pill pill-signal">Allowed</span>
      </div>
      <div class="card">
        <h3>Proof hash available</h3>
        <span class="pill pill-blue">Audit proof available</span>
      </div>
    </div>
    <details>
      <summary>Show proof details</summary>
      <div class="grid">{audit_cards}</div>
      <h3>Show proof hashes</h3>
      <ul>{proof_hash_items}</ul>
    </details>
    <details>
      <summary>Show raw audit JSON</summary>
      <pre>{_esc(json.dumps(model["audit_proofs"], indent=2, sort_keys=True))}</pre>
    </details>
  </section>

  <section id="legacy-fixture">
    <details>
      <summary>Legacy synthetic fixture</summary>
      <p class="muted">The original 72-watch-point fixture is retained only to exercise Corus admission, validation, permissioning, and audit behavior. It is no longer the central demo event.</p>
      <div class="grid">
        <div class="card">
          <h3>Legacy input</h3>
          <p>{_esc(model["input_model_delta"]["claim"])}</p>
          <span class="pill pill-synthetic">{_esc(model["input_model_delta"]["trust"])}</span>
        </div>
        <div class="card">
          <h3>Customer meaning path</h3>
          <ol>{legacy_domain_path}</ol>
        </div>
        <div class="card">
          <h3>Audit edge path</h3>
          <ol>{legacy_surface_path}</ol>
        </div>
      </div>
    </details>
  </section>

  <section>
    <details>
      <summary>Scope and proof notes</summary>
      <div class="split">
        <div class="card">
          <h3>What this demo proves</h3>
          <ul>{proves}</ul>
        </div>
        <div class="card">
          <h3>Out of scope</h3>
          <p class="muted">{_esc(model["trust_banner"])}</p>
          <ul>{out_of_scope}</ul>
        </div>
      </div>
    </details>
  </section>
  <footer>Generated from existing <code>python -m corus</code> JSON commands.</footer>
</body>
</html>
"""


def _render_outcome_metric(metric: dict[str, str]) -> str:
    href = _metric_href(metric)
    return f"""
<a class="outcome-card" href="{_esc(href)}">
  <div class="outcome-value">{_esc(metric["value"])}</div>
  <div class="outcome-label">{_esc(metric["label"])}</div>
</a>
"""


def _metric_href(metric: dict[str, str]) -> str:
    value = str(metric.get("value", "")).lower()
    label = str(metric.get("label", "")).lower()
    if "public" in value or "source" in label:
        return "#source-boundary"
    if "workstream" in label:
        return "#implementation-details"
    if "stakeholder" in label:
        return "#stakeholder-questions"
    if "rejected" in label:
        return "#implementation-details"
    if "audit" in value or "proof" in label:
        return "#decision-confidence"
    return "#decision-summary"


def _render_implementation_detail_card(
    detail: dict[str, Any],
    source_lookup: dict[str, dict[str, Any]],
    fact_lookup: dict[str, dict[str, Any]],
) -> str:
    who = " · ".join(_esc(item) for item in detail.get("who_needs_this", []))
    trace = "".join(_render_trust_pill(status) for status in detail.get("trace_status", []))
    sources = [
        source_lookup.get(source_id, {"id": source_id, "label": source_id})
        for source_id in detail.get("source_ids", [])
    ]
    source_links = "".join(_render_compact_source_link(source) for source in sources)
    source_ids = "".join(f"<li><code>{_esc(source_id)}</code></li>" for source_id in detail.get("source_ids", []))
    unknowns = "".join(f"<li>{_esc(item)}</li>" for item in detail.get("still_unknown", []))
    related_facts = [fact_lookup.get(fact_id) for fact_id in detail.get("related_fact_ids", []) if fact_lookup.get(fact_id)]
    related_fact_items = "".join(
        f"<li><code>{_esc(fact.get('id'))}</code>: {_esc(fact.get('claim'))}</li>"
        for fact in related_facts
    )
    lineage_hashes = "".join(
        f"<li><code>{_esc(fact.get('lineage_hash'))}</code></li>"
        for fact in related_facts
        if fact.get("lineage_hash")
    )
    return f"""
<article class="implementation-card">
  <h3>{_esc(detail["title"])}</h3>
  <div class="chips">{trace}</div>
  <p><strong>What changed:</strong><br>{_esc(detail["what_changed"])}</p>
  <p><strong>Who needs this:</strong><br>{who}</p>
  <p><strong>Next validation step:</strong><br>{_esc(detail["next_validation_step"])}</p>
  <details>
    <summary>Show source and implementation details</summary>
    <p>Sources</p>
    <div class="chips">{source_links}</div>
    <p>Still unknown</p>
    <ul>{unknowns}</ul>
    <p>Source IDs</p>
    <ul>{source_ids}</ul>
    <p>Related facts</p>
    <ul>{related_fact_items}</ul>
    <p>Trace status</p>
    <div class="chips">{trace}</div>
    <p>Lineage hashes</p>
    <ul class="hash">{lineage_hashes}</ul>
  </details>
</article>
"""


def _render_action_option(row: dict[str, str]) -> str:
    return f"""
<tr>
  <td><strong>{_esc(row["option"])}</strong></td>
  <td>{_esc(row["purpose"])}</td>
  <td>{_esc(row["status"])}</td>
  <td>{_esc(row["trust"])}</td>
</tr>
"""


def _render_source_card(source: dict[str, Any]) -> str:
    statuses = "".join(_render_trust_pill(status) for status in source.get("trust_status", []))
    url = source.get("url")
    source_class = "source-public" if "public_source" in source.get("trust_status", []) else "source-synthetic"
    source_link = (
        f"<a href=\"{_esc(url)}\" target=\"_blank\" rel=\"noreferrer\">Open source</a>"
        if url
        else "<span class=\"muted\">Internal fixture</span>"
    )
    supports = list(source.get("supports", []))
    limits = list(source.get("limits", []))
    support_sentence = supports[0] if supports else source.get("trust_note", "Source context is declared for this demo.")
    support_items = "".join(f"<li>{_esc(item)}</li>" for item in supports)
    limit_items = "".join(f"<li>{_esc(item)}</li>" for item in limits)
    public_pill = (
        "<span class=\"pill pill-public\">Public source</span>"
        if "public_source" in source.get("trust_status", [])
        else "<span class=\"pill pill-synthetic\">Synthetic fixture</span>"
    )
    return f"""
<article class="source-card {source_class}">
  <div class="source-card-head">
    <h3>{_esc(source.get("label", source.get("id", "source")))}</h3>
    {public_pill}
  </div>
  <p>{_esc(support_sentence)}</p>
  <div class="source-meta">{statuses}</div>
  <div class="source-actions">
    {source_link}
    <details>
      <summary>Show evidence details</summary>
      <p>Source ID: <code>{_esc(source.get("id", ""))}</code></p>
      <p>Kind: {_esc(source.get("kind", ""))}</p>
      <p>Authority: {_esc(source.get("authority", "source authority missing"))}</p>
      <p>Source status: {_esc(source.get("source_status", "unknown"))}</p>
      <p class="hash">URL: {_esc(url or "not applicable")}</p>
      <p>Trust status</p>
      <div class="chips">{statuses}</div>
      <p>Supports</p>
      <ul>{support_items}</ul>
      <p>Limits</p>
      <ul>{limit_items}</ul>
    </details>
  </div>
</article>
"""


def _render_compact_source_link(source: dict[str, Any]) -> str:
    label = _esc(source.get("label", source.get("id", "source")))
    url = source.get("url")
    if url:
        return f"<a class='pill pill-public' href='{_esc(url)}' target='_blank' rel='noreferrer'>{label}</a>"
    return f"<span class='pill pill-synthetic'>{label}</span>"


def _render_fact_card(fact: dict[str, Any]) -> str:
    statuses = "".join(_render_trust_pill(status) for status in fact.get("trust_status", []))
    sources = "".join(
        f"<span class='pill pill-public'>{_esc(label)}</span>"
        for label in fact.get("source_labels", [])
    )
    title = str(fact.get("id", "fact")).replace("fact.", "").replace(".", " ").replace("_", " ").title()
    trace = {
        "fact_id": fact.get("id"),
        "source_context_ids": fact.get("source_context_ids", []),
        "supports_domain_node": fact.get("supports_domain_node"),
        "trust_note": fact.get("trust_note"),
        "lineage_hash": fact.get("lineage_hash"),
    }
    return f"""
<article class="fact-card">
  <div class="fact-head">
    <h3>{_esc(title)}</h3>
    <div>{statuses}</div>
  </div>
  <p>{_esc(fact.get("claim", ""))}</p>
  <p class="muted">{_esc(_fact_meaning(fact))}</p>
  <div class="chips">{sources}</div>
  <details>
    <summary>Show trace</summary>
    <pre>{_esc(json.dumps(trace, indent=2, sort_keys=True))}</pre>
  </details>
</article>
"""


def _fact_meaning(fact: dict[str, Any]) -> str:
    meanings = {
        "fact.customer.needs_significance": "This is the root implementation question. It explains why the page starts after intelligence exists.",
        "fact.rvo.intelligence_exists": "This grounds the broad intelligence side of the demo.",
        "fact.sce.risk_model_outputs_affect_workstreams": "This grounds the affected-workstream implementation-detail cards.",
        "fact.customer.unsupported_specific_cost": "This explains why the cost claim is rejected rather than rendered as customer value.",
        "fact.corus.situated_significance": "This is the Corus output: a customer-specific reason for action with source boundaries attached.",
    }
    return meanings.get(str(fact.get("id")), "This source-backed trace supports the implementation-detail cards above.")


def _render_workstream_card(workstream: dict[str, str]) -> str:
    return f"""
<div class="card">
  <h3>{_esc(workstream["title"])}</h3>
  <p><strong>What changes?</strong><br>{_esc(workstream["changes"])}</p>
  <p><strong>What evidence is needed?</strong><br>{_esc(workstream["evidence"])}</p>
  <p><strong>What is still unknown?</strong><br>{_esc(workstream["unknown"])}</p>
</div>
"""


def _render_stakeholder_card(stakeholder: dict[str, Any]) -> str:
    needs = "".join(f"<li>{_esc(item)}</li>" for item in stakeholder.get("needs", []))
    receives = "".join(f"<li>{_esc(item)}</li>" for item in stakeholder.get("receives", []))
    return f"""
<article class="card">
  <h3>{_esc(stakeholder.get("label", stakeholder.get("id", "Stakeholder")))}</h3>
  <p><strong>{_esc(stakeholder.get("core_question", ""))}</strong></p>
  <p class="muted">Needs</p>
  <ul>{needs}</ul>
  <details>
    <summary>Show stakeholder details</summary>
    <p>Receives</p>
    <ul>{receives}</ul>
  </details>
</article>
"""


def _render_trust_pill(status: str) -> str:
    css = "pill-public"
    if status in {"demo_synthetic", "demo_interpretation"}:
        css = "pill-synthetic"
    elif status == "rejected_assumption":
        css = "pill-bad"
    elif status == "source_authority_missing":
        css = "pill-warn"
    elif status == "internally_hash_backed":
        css = "pill-blue"
    return f"<span class='pill {css}'>{_esc(status)}</span>"


def _render_role(role: dict[str, Any]) -> str:
    allowed = "".join(f"<li>{_esc(_human_action(action))}</li>" for action in role["allowed_actions"])
    restricted = "".join(
        f"<li>{_esc(_human_action(item['action']))}</li>"
        for item in role["restricted_actions"]
    )
    action_ids = "".join(f"<li><code>{_esc(action)}</code></li>" for action in role["allowed_actions"])
    restricted_ids = "".join(
        f"<li><code>{_esc(item['action'])}</code>: {_esc(item['permission_result'])}</li>"
        for item in role["restricted_actions"]
    )
    return f"""
<div class="card">
  <div class="role-title">
    <h3>{_esc(role["label"])}</h3>
    <span class="pill">{_esc(role["proposed_action_label"])}</span>
  </div>
  <p class="muted">Needs:</p>
  <p>{_esc(role["core_question"])}</p>
  <p class="muted">Output:</p>
  <p><strong>{_esc(role["output"])}</strong></p>
  <p class="muted">Allowed:</p>
  <ul>{allowed}</ul>
  <p class="muted">Requires approval:</p>
  <ul>{restricted}</ul>
  <details>
    <summary>Show action IDs</summary>
    <p class="muted">Allowed actions</p>
    <ul>{action_ids}</ul>
    <p class="muted">Restricted actions</p>
    <ul>{restricted_ids}</ul>
  </details>
  <details>
    <summary>Show profile details</summary>
    <p>Profile ID: <code>{_esc(role["profile_id"])}</code></p>
    <p class="hash">audit event hash: {_esc(role["audit_event_hash"])}</p>
  </details>
</div>
"""


def _render_audit(name: str, proof: dict[str, Any]) -> str:
    checks = "".join(
        f"<div class='check'><div>{_esc(label.replace('_', ' '))}</div><div class='{_status_class(status)}'>{_esc(status)}</div></div>"
        for label, status in proof["checks"].items()
    )
    return f"""
<div class="card">
  <h3>{_esc(name.replace("_", " ").title())}</h3>
  <p><code>{_esc(proof["target"])}</code></p>
  <p>Status: <strong>{_esc(proof["status"])}</strong> Valid: <strong>{_esc(str(proof["valid"]).lower())}</strong></p>
  <div class="checks">{checks}</div>
  <p class="hash">proof hash: {_esc(proof["proof_hash"])}</p>
</div>
"""


def _status_class(status: str) -> str:
    if status == "pass":
        return "pass"
    if status == "not_applicable":
        return "not-applicable"
    return "bad"


def _esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def build_html(root: Path = ROOT) -> str:
    return render_demo_html(build_demo_model(load_demo_data(root=root)))


def write_html(output: Path, root: Path = ROOT) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_html(root=root), encoding="utf-8")
    return output


class DemoHandler(BaseHTTPRequestHandler):
    root = ROOT

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        if self.path not in {"/", "/index.html"}:
            self.send_error(404)
            return
        body = build_html(root=self.root).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def serve(host: str, port: int, root: Path = ROOT) -> None:
    DemoHandler.root = root
    server = ThreadingHTTPServer((host, port), DemoHandler)
    print(f"{TITLE}: http://{host}:{port}/")
    server.serve_forever()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Render the Neara/SCE value translation web demo.")
    parser.add_argument("--out", type=Path, help="Write a static HTML file instead of serving.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--serve", action="store_true", help="Serve the demo locally.")
    args = parser.parse_args(argv)

    if args.out:
        output = write_html(args.out)
        print(output)
        return
    if args.serve:
        serve(args.host, args.port)
        return
    print(build_html())


if __name__ == "__main__":
    main()
