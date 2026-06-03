from __future__ import annotations

import argparse
import html
import json
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = Path("tests/fixtures/sce_vegetation")
TITLE = "Neara / SCE Value Translation Demo"
SOURCE_STATUS = "demo-synthetic / internally hash-backed / source-authority missing where applicable"
TRUST_BANNER = (
    "Proof-of-work demo: synthetic Neara-style input, internally hash-backed, not an official Neara or SCE export."
    " Source authority pending; source-authority missing where applicable."
)
OPERATIONAL_EXPLANATION = (
    "A Neara-style model delta becomes customer value by moving through policy interpretation, "
    "watch-point classification, wildfire risk, operational priority, crew planning, cost exposure, and SCE value."
)
HERO_HEADLINE = "Turn grid model outputs into defensible work and budget decisions."
HERO_SUBHEAD = (
    "This proof-of-work starts with 72 vegetation watch points and shows how a Customer Value Architect "
    "can translate them into SCE-specific operational impact, recommended action, business value, and audit evidence."
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
        "headline": HERO_HEADLINE,
        "subhead": HERO_SUBHEAD,
        "source_status": SOURCE_STATUS,
        "trust_banner": TRUST_BANNER,
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
            {"value": "72", "label": "watch points translated"},
            {"value": "1", "label": "recommended action"},
            {"value": "1", "label": "rejected assumption"},
            {"value": "Audit proof", "label": "available"},
        ],
        "decision_summary": {
            "what_changed": "72 vegetation watch points",
            "why_it_matters": "Vegetation items may require operational review under clearance policy",
            "customer_value": "Workforce planning + budget exposure",
            "recommended_action": "Generate work packet",
            "trust_status": "Included claim · rejected assumption · audit proof available",
        },
        "workflow": [
            {
                "step": "1",
                "title": "Start with the model output",
                "body": "72 vegetation watch points from a Neara-style output.",
            },
            {
                "step": "2",
                "title": "Ask the customer-value question",
                "body": "What work, budget, and operational priority does this create for SCE?",
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
        "proves": [
            "A model output can be translated into a customer-facing decision.",
            "Claims can be admitted or rejected.",
            "Recommended actions can be checked against role permissions.",
            "Audit proof can explain why a claim or action was included, excluded, or allowed.",
        ],
        "out_of_scope": [
            "Official Neara export verification.",
            "Externally approved SCE operating model.",
            "Actual SCE cost exposure.",
            "Replacement of Neara's grid modeling, LiDAR, GIS, or simulation pipeline.",
        ],
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
    path_items = "".join(f"<li>{_esc(node)}</li>" for node in model["operational_path"])
    surface_items = "".join(f"<li>{_esc(edge)}</li>" for edge in model["surface_path"])
    ladder_items = "".join(f"<li>{_esc(step)}</li>" for step in model["story_ladder"])
    roles = "\n".join(_render_role(role) for role in model["roles"])
    audit_cards = "\n".join(_render_audit(name, proof) for name, proof in model["audit_proofs"].items())
    value_metrics = "".join(f"<li>{_esc(metric)}</li>" for metric in model["value_story"]["value_metrics"])
    outcome_metrics = "\n".join(_render_outcome_metric(metric) for metric in model["outcome_metrics"])
    workflow = "\n".join(_render_workflow_step(step) for step in model["workflow"])
    action_rows = "\n".join(_render_action_option(row) for row in model["action_options"])
    action_ids = "".join(
        f"<li>{_esc(row['option'])}: <code>{_esc(row['action_id'])}</code></li>" for row in model["action_options"]
    )
    output_items = "".join(f"<li>{_esc(item)}</li>" for item in model["output"]["items"])
    assumptions = "".join(f"<li>{_esc(item)}</li>" for item in model["evidence_status"]["synthetic_assumptions"])
    proves = "".join(f"<li>{_esc(item)}</li>" for item in model["proves"])
    out_of_scope = "".join(f"<li>{_esc(item)}</li>" for item in model["out_of_scope"])
    proof_hash_items = "".join(
        f"<li>{_esc(label.replace('_', ' ').title())}: <code>{_esc(proof['proof_hash'])}</code></li>"
        for label, proof in model["audit_proofs"].items()
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{_esc(model["title"])}</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #17202a;
      --muted: #5f6b76;
      --line: #d9e0e6;
      --panel: #ffffff;
      --wash: #f5f7f9;
      --accent: #126c5b;
      --accent-soft: #dcefe9;
      --warn: #8a4f08;
      --warn-soft: #fff1d6;
      --bad: #8b2f2f;
      --bad-soft: #f9e1df;
      --blue: #214f7a;
      --blue-soft: #e1edf7;
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
    header {{ background: #10202b; color: white; }}
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
    .pill-blue {{ background: var(--blue-soft); color: var(--blue); }}
    .pill-warn {{ background: var(--warn-soft); color: var(--warn); }}
    .pill-bad {{ background: var(--bad-soft); color: var(--bad); }}
    header .pill {{ background: rgba(255,255,255,.13); color: white; border: 1px solid rgba(255,255,255,.22); }}
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
    .outcome-card {{ background: white; border: 1px solid var(--line); border-radius: 8px; padding: 18px; min-height: 120px; }}
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
      <span class="pill">Synthetic demo</span>
      <span class="pill">Hash-backed</span>
      <span class="pill">No model replacement</span>
      <span class="pill">Source authority pending</span>
    </div>
  </header>

  <section>
    <div class="metric-strip">{outcome_metrics}</div>
  </section>

  <section>
    <div class="notice">{_esc(model["trust_banner"])}</div>
  </section>

  <section>
    <div class="receipt">
      <div class="receipt-head">
        <div>
          <h2 class="receipt-title">Decision Summary</h2>
          <p class="muted">A technical model output becomes a customer-facing decision: what changed, why it matters, what action is allowed, and what proof supports it.</p>
        </div>
        <span class="pill pill-blue">{_esc(model["decision_summary"]["trust_status"])}</span>
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
      <div class="io-grid">
        <div class="io-card">
          <h2>Input</h2>
          <p class="muted">{_esc(model["input_model_delta"]["type"])}</p>
        <div class="metric">{_esc(str(model["input_model_delta"]["value"]))}</div>
        <p><strong>{_esc(model["input_model_delta"]["unit"].replace("_", " "))}</strong></p>
          <p>Source: <code>{_esc(model["input_model_delta"]["source_observation"])}</code></p>
          <p>Status: {_esc(model["input_model_delta"]["trust"])}</p>
        <span class="pill">source: {_esc(model["input_model_delta"]["source_observation"])}</span>
        <span class="pill">{_esc(model["input_model_delta"]["trust"])}</span>
      </div>
        <div class="io-card">
          <h2>Output</h2>
          <div class="metric-text">{_esc(model["output"]["title"])}</div>
          <ul>{output_items}</ul>
          <span class="pill">Generate work packet</span>
          <span class="pill">Customer value story</span>
        </div>
      </div>
    </div>
  </section>

  <section>
    <h2>CVA decision workflow</h2>
    <div class="workflow">{workflow}</div>
  </section>

  <section>
    <h2>Action Options</h2>
    <table>
      <thead>
        <tr>
          <th>Option</th>
          <th>Customer purpose</th>
          <th>Status</th>
          <th>Trust note</th>
        </tr>
      </thead>
      <tbody>{action_rows}</tbody>
    </table>
    <details>
      <summary>Show action IDs</summary>
      <ul>{action_ids}</ul>
    </details>
  </section>

  <section>
    <h2>How the model output becomes customer value</h2>
    <p class="muted">{_esc(model["operational_explanation"])}</p>
    <ol class="ladder">{ladder_items}</ol>
    <details>
      <summary>Show technical trace</summary>
      <div class="grid">
        <div class="card">
          <h3>Customer meaning path</h3>
          <p class="muted">Domain node IDs preserved for auditability.</p>
          <ol>{path_items}</ol>
        </div>
        <div class="card">
          <h3>Audit edge path</h3>
          <p class="muted">Surface edge IDs preserved for auditability.</p>
          <ol>{surface_items}</ol>
        </div>
      </div>
    </details>
  </section>

  <section>
    <h2>Stakeholder Views</h2>
    <div class="grid">{roles}</div>
  </section>

  <section>
    <h2>Why it matters</h2>
    <div class="card">
      <h3>Customer value</h3>
      <p>{_esc(model["value_story"]["because"])}</p>
      <ul>{value_metrics}</ul>
    </div>
  </section>

  <section>
    <h2>Decision Confidence</h2>
    <div class="grid">
      <div class="card">
        <h3>Included claim</h3>
        <p><code>{_esc(model["evidence_status"]["admitted_claim"]["id"])}</code></p>
        <p>{_esc(model["evidence_status"]["admitted_claim"]["claim"])}</p>
        <span class="pill">Included</span>
        <span class="pill">Hash-backed</span>
        <span class="pill">{_esc(model["evidence_status"]["admitted_claim"]["trust"])}</span>
      </div>
      <div class="card">
        <h3>Rejected assumption</h3>
        <p><code>{_esc(model["evidence_status"]["rejected_claim"]["id"])}</code></p>
        <p>{_esc(model["evidence_status"]["rejected_claim"]["claim"])}</p>
        <span class="pill pill-bad">Rejected</span>
        <span class="pill pill-warn">Source authority pending</span>
      </div>
      <div class="card">
        <h3>Demo assumptions</h3>
        <ul>{assumptions}</ul>
        <span class="pill pill-warn">Synthetic</span>
      </div>
    </div>
  </section>

  <section>
    <h2>Can this decision be defended?</h2>
    <div class="grid">
      <div class="card">
        <h3>Included</h3>
        <p>72 vegetation watch points</p>
        <span class="pill">Included</span>
      </div>
      <div class="card">
        <h3>Rejected</h3>
        <p>Unsupported $999,999 cost assumption</p>
        <span class="pill pill-bad">Rejected</span>
      </div>
      <div class="card">
        <h3>Allowed</h3>
        <p>Generate work packet</p>
        <span class="pill">Allowed</span>
      </div>
      <div class="card">
        <h3>Proof</h3>
        <p>Audit checks passed</p>
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
      <summary>Show raw JSON</summary>
      <pre>{_esc(json.dumps(model["audit_proofs"], indent=2, sort_keys=True))}</pre>
    </details>
  </section>

  <section>
    <h2>What this demo proves</h2>
    <div class="split">
      <div class="card">
        <h3>What this proves</h3>
        <ul>{proves}</ul>
      </div>
      <div class="card">
        <h3>Out of scope</h3>
        <p class="muted">{_esc(model["trust_banner"])}</p>
        <ul>{out_of_scope}</ul>
      </div>
    </div>
  </section>
  <footer>Generated from existing <code>python -m corus</code> JSON commands.</footer>
</body>
</html>
"""


def _render_outcome_metric(metric: dict[str, str]) -> str:
    return f"""
<div class="outcome-card">
  <div class="outcome-value">{_esc(metric["value"])}</div>
  <div class="outcome-label">{_esc(metric["label"])}</div>
</div>
"""


def _render_workflow_step(step: dict[str, str]) -> str:
    return f"""
<div class="workflow-step">
  <div class="step-number">{_esc(step["step"])}</div>
  <h3>{_esc(step["title"])}</h3>
  <p>{_esc(step["body"])}</p>
</div>
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
