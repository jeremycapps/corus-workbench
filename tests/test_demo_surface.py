from __future__ import annotations

from corus.demo_surface import SOURCE_STATUS, build_demo_model, load_demo_data, render_demo_html


def test_demo_data_loader_runs_corus_commands() -> None:
    data = load_demo_data()
    assert data["explain"]["operational_trace"]["claims"]
    assert data["sce_grid_ops"]["agent_run"]["profile_id"] == "sce_grid_ops"
    assert data["neara_value_architect"]["agent_run"]["profile_id"] == "neara_value_architect"
    assert data["audit_watch_points"]["proof_hash"]


def test_rendered_model_includes_watch_point_claim() -> None:
    model = build_demo_model(load_demo_data())
    assert model["input_model_delta"]["value"] == 72
    assert "72 vegetation watch points" in model["input_model_delta"]["claim"]


def test_rendered_model_includes_rejected_unsupported_cost_assumption() -> None:
    model = build_demo_model(load_demo_data())
    rejected = model["evidence_status"]["rejected_claim"]
    assert rejected["id"] == "claim.sce.unsupported_cost_assumption"
    assert "$999,999" in rejected["claim"]
    assert rejected["status"] == "excluded"


def test_rendered_model_includes_both_profiles() -> None:
    model = build_demo_model(load_demo_data())
    profile_ids = {role["profile_id"] for role in model["roles"]}
    assert profile_ids == {"sce_grid_ops", "neara_value_architect"}


def test_rendered_model_includes_proof_hash() -> None:
    model = build_demo_model(load_demo_data())
    assert any(proof["proof_hash"] for proof in model["audit_proofs"].values())


def test_page_includes_source_status_language() -> None:
    model = build_demo_model(load_demo_data())
    html = render_demo_html(model)
    assert "demo-synthetic" in SOURCE_STATUS
    assert "demo-synthetic" in html
    assert "source-authority missing" in html
    assert "Neara / SCE Value Translation Demo" in html


def test_page_has_sendable_role_and_status_language() -> None:
    model = build_demo_model(load_demo_data())
    html = render_demo_html(model)
    assert "Stakeholder Views" in html
    assert "Pole Views" not in html
    assert "Proof-of-work demo" in html
    assert "Customer meaning path" in html
    assert "Audit edge path" in html


def test_page_has_both_profiles_and_action_boundaries() -> None:
    model = build_demo_model(load_demo_data())
    html = render_demo_html(model)
    assert "sce_grid_ops" in html
    assert "neara_value_architect" in html
    assert "Allowed actions" in html
    assert "Restricted actions" in html
    assert "generate_work_packet" in html
    assert "estimate_crew_hours" in html
    assert "flag_budget_exposure" in html
    assert "generate_value_story" in html
    assert "identify_repeatable_pattern" in html
    assert "prepare_customer_demo" in html
    assert "dispatch_crew" in html
    assert "approve_budget_change" in html
    assert "change_customer_policy" in html
    assert "commit_customer_budget" in html


def test_page_has_proof_and_scope_sections() -> None:
    model = build_demo_model(load_demo_data())
    html = render_demo_html(model)
    assert "What this proves" in html
    assert "Out of scope" in html
    assert "72 vegetation watch points" in html
    assert "SCE cost exposure is $999,999." in html
    assert "proof hash:" in html or "audit event hash:" in html


def test_page_prioritizes_decision_summary_inputs_and_outputs() -> None:
    model = build_demo_model(load_demo_data())
    html = render_demo_html(model)
    assert "Turn grid model outputs into defensible work and budget decisions." in html
    assert "Decision Summary" in html
    assert "What changed?" in html
    assert "Why it matters" in html
    assert "Customer value" in html
    assert "Recommended action" in html
    assert "Input" in html
    assert "Output" in html
    assert "72 vegetation watch points" in html
    assert "SCE operational value" in html
    assert "Generate work packet" in html
    assert "Customer value story" in html


def test_page_progressively_discloses_technical_details() -> None:
    model = build_demo_model(load_demo_data())
    html = render_demo_html(model)
    assert "How the model output becomes customer value" in html
    assert "Can this decision be defended?" in html
    assert "Included" in html
    assert "Rejected" in html
    assert "Allowed" in html
    assert "Decision Confidence" in html
    assert "demo_model_output" in html
    assert "claim.sce.unsupported_cost_assumption" in html
    assert "Show technical trace" in html
    assert "Show proof details" in html
    assert "proof hash:" in html or "audit event hash:" in html
    assert "<h3>Domain path</h3>" not in html
    assert "<h3>Surface path</h3>" not in html


def test_page_includes_action_options_table() -> None:
    model = build_demo_model(load_demo_data())
    html = render_demo_html(model)
    assert "Action Options" in html
    assert "Generate work packet" in html
    assert "Dispatch crew" in html
    assert "Approval required" in html
