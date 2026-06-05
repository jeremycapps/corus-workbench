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
    assert "Stakeholder questions" in html
    assert "Pole Views" not in html
    assert "Public-source context" in html
    assert "Synthetic fixture bounded" in html
    assert "No RVO replacement" in html
    assert "Audit proof available" in html
    assert "public-source grounded" in html
    assert "not an official Neara export" in html
    assert "Implementation details surfaced from broad intelligence" in html
    assert "Trace evidence behind the implementation details" in html
    assert "Facts, assumptions, and boundaries" not in html


def test_page_has_both_profiles_and_action_boundaries() -> None:
    model = build_demo_model(load_demo_data())
    html = render_demo_html(model)
    assert "Grid Ops" in html
    assert "Finance" in html
    assert "Regulatory" in html
    assert "Executive Sponsor" in html
    assert "Neara Implementation Team" in html
    assert "What operational work changes first?" in html
    assert "What budget or capital plan may be affected?" in html
    assert "Can the decision be defended?" in html
    assert "Why does this matter now?" in html
    assert "What does the customer need in order to act?" in html


def test_page_surfaces_implementation_details_before_engine_proof() -> None:
    model = build_demo_model(load_demo_data())
    html = render_demo_html(model)
    assert "Implementation details surfaced from broad intelligence" in html
    assert "Asset inspection prioritization" in html
    assert "Vegetation management scope" in html
    assert "System hardening schedule" in html
    assert "Unsupported cost amount" in html
    assert "Next validation step" in html
    assert "Show source and implementation details" in html
    assert html.index("Implementation details surfaced from broad intelligence") < html.index("Source boundary")
    assert html.index("Implementation details surfaced from broad intelligence") < html.index("Can this be defended?")
    assert "Scope and proof notes" in html


def test_page_has_proof_and_scope_sections() -> None:
    model = build_demo_model(load_demo_data())
    html = render_demo_html(model)
    assert "Scope and proof notes" in html
    assert "Out of scope" in html
    assert "72 vegetation watch points" in html
    assert "Specific cost impact is rejected unless customer-approved cost evidence exists." in html
    assert "proof hash:" in html or "audit event hash:" in html


def test_page_prioritizes_decision_summary_inputs_and_outputs() -> None:
    model = build_demo_model(load_demo_data())
    html = render_demo_html(model)
    assert "When intelligence exists, customers still need significance." in html
    assert "Decision Summary" in html
    assert "What changed?" in html
    assert "Why it matters" in html
    assert "Customer value" in html
    assert "Recommended action" in html
    assert "Broad intelligence becomes customer-specific significance" in html
    assert "Broad risk intelligence exists" in html
    assert "Customer-specific implementation meaning." in html
    assert "Generate implementation context trace." in html
    assert "72 synthetic watch points translated" not in html


def test_demo_model_includes_latest_source_context() -> None:
    model = build_demo_model(load_demo_data())
    assert model["source_context"]
    assert model["public_sources"]
    assert model["source_boundary"]
    assert model["source_context"]["central_question"]["text"] == "Why does this matter to me?"
    authorities = {source["authority"] for source in model["sources"]}
    assert "public_sce_regulatory_filing" in authorities
    assert "public_neara_marketing" in authorities
    assert model["decision_summary"]
    assert model["input_model_delta"]["trust"] == "demo-synthetic / demo_model_output"


def test_page_includes_latest_source_boundary_language() -> None:
    model = build_demo_model(load_demo_data())
    html = render_demo_html(model)
    assert "Source boundary" in html
    assert "public-source grounded" in html
    assert "not an official Neara export" in html
    assert "SCE 2025 WMP" in html
    assert "Neara RVO" in html
    assert "synthetic fixture" in html
    assert "unsupported cost assumption is rejected" in html
    assert "customer-specific implementation meaning" in html


def test_page_progressively_discloses_technical_details() -> None:
    model = build_demo_model(load_demo_data())
    html = render_demo_html(model)
    assert "Can this be defended?" in html
    assert "Public context included" in html
    assert "Unsupported cost rejected" in html
    assert "Next action allowed" in html
    assert "Decision Confidence" in html
    assert "Show trace" in html
    assert "Show evidence details" in html
    assert "Show proof details" in html
    assert "proof hash:" in html or "audit event hash:" in html
    assert "<h3>Domain path</h3>" not in html
    assert "<h3>Surface path</h3>" not in html


def test_page_uses_progressive_disclosure_for_sources_facts_and_legacy_fixture() -> None:
    model = build_demo_model(load_demo_data())
    html = render_demo_html(model)
    assert "Open source" in html
    assert "Show evidence details" in html
    assert "Trace evidence behind the implementation details" in html
    assert "Asset inspection prioritization" in html
    assert "Vegetation management scope" in html
    assert "System hardening schedule" in html
    assert "Unsupported cost amount" in html
    assert "Legacy synthetic fixture" in html
    assert "The original 72-watch-point fixture is retained only to exercise Corus admission" in html


def test_metric_cards_anchor_to_implementation_first_flow() -> None:
    model = build_demo_model(load_demo_data())
    html = render_demo_html(model)
    assert 'href="#implementation-details"' in html
    assert 'href="#stakeholder-questions"' in html
    assert 'href="#decision-confidence"' in html
    assert 'href="#source-boundary"' in html
    assert html.index("Implementation details surfaced from broad intelligence") < html.index("Trace evidence behind the implementation details")
