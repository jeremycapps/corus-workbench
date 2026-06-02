# Corus Codebase Review Log

Review date: 2026-06-02

Workspace: `/Users/jeremycapps/Documents/corus/corus-workbench`

Product framing for this review: Neara tells utilities what changed in the network. Corus tells each customer why that change matters.

Corrected review scope: for the Neara demo, Corus should be evaluated as a value translation layer, not as a replacement for Neara's physical network reconstruction, LiDAR/GIS processing, clearance modeling, or vegetation detection. The central review question is: is the codebase structurally organized around translating a Neara-style model delta into customer-specific value, action, and why?

## 1. Executive Summary

This repo is currently a strong Neara value-translation demo engine and early protocol implementation, not yet a production-shaped Context Management System. The most active and coherent path is `python -m corus`, implemented in `corus/playground.py`, with ledger-backed WRITE/READ/AUDIT behavior for the SCE vegetation demo. The source-to-extent PoC is useful, but it should be read as supporting provenance infrastructure rather than the main Neara demo path. Tests are broad and architectural: 227 tests collected, with 182 passing and 45 intentionally xfailed.

The intended demo path is:

```text
Neara model output / model delta
  -> Corus intake wrapper
  -> .domain meaning nodes
  -> .surface operational graph
  -> .lens / .profile role-specific attention and permissions
  -> .value customer value definitions
  -> .evidence source-backed business assumptions
  -> READ reconstruction
  -> because trace
  -> AUDIT proof
  -> value story / work packet
```

The review should not judge Corus by whether it can recreate raw LiDAR ingestion, raw GIS reconciliation, raw GeoJSON polygon processing, raw PDF extraction, generic physical-world source synthesis, or Neara's modeling pipeline. Those are future-upstream or optional capabilities. For the demo, Corus receives a clean Neara-style output and answers: what changed, why it matters to SCE, who needs to act, what operational decision is affected, what cost/crew/budget/risk exposure is implied, which assumptions are source-backed, which assumptions are synthetic, what can be audited, what can be replayed, and what remains unproven.

What exists and works:

- Neara-style intake wrapper: `bundles/sce_vegetation/corus.bundle.yaml` and `bundles/sce_vegetation/artifacts/demo_model_output.json` model the handoff from Neara output into Corus.
- Value translation layers: `.domain`, `.surface`, `.lens`, `.profile`, `.value`, and `.evidence` fixtures exist for SCE vegetation operations.
- Explain/value path: `corus.playground.command_explain` emits architectural and operational traces that connect model delta concepts to operational priority, crew hours, cost exposure, customer value, and repeatable product pattern.
- Work/action path: `agent-run` deterministically proposes `generate_work_packet`, respects restricted profile actions, and emits audit hashes without calling an LLM.
- WRITE/admission: `kernel/ledger/store.py`, `kernel/source/*`, and `corus.playground.command_ingest` can create payloads and append verified ledger entries.
- READ: `kernel/ledger/read.py` reconstructs active candidate-claim context from ledger interpretation/validation payloads.
- Runtime reconstruction: `kernel/engine/runtime.py` loads domain/surface/lens/profile/value files, applies lens weights, computes hashes, and emits because traces.
- AUDIT: `kernel/audit/*` now proves target resolution, ledger hash continuity, payload hashes, claim admissibility, optional READ replay comparison, and output profile permissions.
- CLI/demo: `python -m corus validate|reconstruct|project|read|audit|explain|diff|agent-run|ingest|source add` is the central verified surface.
- Timpo: Mojo and Python tests verify deterministic when/where encoding and benchmark read/write.

What is partial or synthetic:

- The SCE vegetation fixture is highly useful but demo-synthetic. `tests/fixtures/sce_vegetation/observations.timpos` uses `source: demo`; `sce.evidence` contains asserted facts such as `fact.cost.validation_exposure` without external source authority.
- The Neara model delta/watch point output is represented by demo artifacts and claims, not by a real Neara export contract with external provenance.
- `agent-run` is deterministic demo logic in `corus/playground.py`, not a real agent runtime. The xfail suite explicitly marks agent runtime behavior as not implemented.
- `AUDIT-006` detailed diff/comparison and `AUDIT-007B` object-level paths are placeholders.
- Source/extent/validation objects are implemented as a PoC and materialized into the current ledger grammar, but READ does not yet include validated extents as active context.

What appears stale or split:

- There are two CLI surfaces: `python -m corus` uses `corus/playground.py`; the installed script in `pyproject.toml` points `corus = "kernel.command.cli:app"`, an older Typer interface over `fs/`.
- `fs/03_processes/runs` contains many generated process runs. They preserve old program-run outputs, but are not central to the current WRITE/READ/AUDIT demo path.
- `kernel/connect/*` imports compile but appear unused by tests and CLI paths.

The codebase is optimized right now for explaining and testing value translation architecture, not for ingesting raw customer geospatial data at scale. Its strongest aspect is the chain from Neara-style model delta to SCE-specific value/action/why, backed by proof-shaped audit and explicit tests. Its weakest aspect is that fixtures and docs can make synthetic assumptions feel more real than they are unless the source-grounding boundary stays visible.

## Neara Value Translation Readiness

| Component | Role in value translation | Current status | Evidence | Gap |
| --------- | ------------------------- | -------------- | -------- | --- |
| Neara-style input object | Supplies the model delta/watch point output Corus translates. | present but synthetic | `bundles/sce_vegetation/artifacts/demo_model_output.json`, `bundles/sce_vegetation/corus.bundle.yaml`, `claim.sce.watch_points_added` | Needs a stable Neara export shape and explicit source authority. |
| SCE operational domain | Names the customer-specific meaning nodes used to interpret model deltas. | implemented for demo | `tests/fixtures/sce_vegetation/sce.domain`, `kernel/domain/*` tests | Domain nodes are asserted demo contracts, not externally approved SCE ontology. |
| Surface graph from model delta to customer value | Connects model delta through policy, operations, risk, cost, and product pattern. | implemented for demo | `tests/fixtures/sce_vegetation/sce.surface`, operational trace path | Needs object-level audit for each surface edge and better source-backed relationship evidence. |
| Lens/profile role routing | Selects role-specific attention and permissions. | implemented for demo | `vegetation_ops.lens`, `sce_grid_ops.profile`, `neara_value_architect.profile`, `agent-run` output | Approval workflows are deterministic/demo-only; no real user or org permission system. |
| Customer value file | Defines how translated context maps to customer value. | implemented for demo | `sce_customer.value`, value/scenario tests | Value metrics are fixture-defined; customer approval/source status is not proven. |
| Evidence file | Holds source-backed and synthetic business assumptions used by explain. | present but partly synthetic | `sce.evidence`, operational trace claims | Needs explicit distinction between file-backed, source-backed, approved, and synthetic facts. |
| Explain/because trace | Shows why a value/action conclusion follows from the layer chain. | implemented with architectural and operational traces | `corus explain`, `tests/test_playground_cli.py` | Operational trace is demo-specific and should become reusable trace logic if it grows. |
| Audit proof | Proves ledger continuity, payload hashes, admissibility, replay status, and permissions. | implemented/partial | `kernel/audit/*`, `tests/ledger/test_ledger_read_audit.py` | Object-level paths, source authority, and detailed diff proof remain incomplete. |
| Work packet generation | Turns translated value/action context into a proposed operational action. | minimal deterministic demo | `agent-run` proposes `generate_work_packet`; profile permissions checked | Needs a real work-packet artifact/schema if shown as product output. |
| Value story generation | Frames why the change matters to this customer. | present as explain/value-story behavior, not a distinct generator | `explain` operational path, `docs/demo_sce_vegetation.md`, value fixtures | Needs clearer output contract separating story, assumptions, and audit references. |
| Synthetic assumptions | Make the demo possible while showing unproven claims. | visible but easy to overstate | `claim.sce.unsupported_cost_assumption`, `sce.evidence`, audit partial statuses | Demo docs should label synthetic assumptions wherever business value is discussed. |
| Source-backed assumptions | Anchor claims that can be trusted or audited. | internally hash-backed, externally weak | ledger payload hashes, bundle artifact hashes, source references | Needs source authority/admissibility verifier and evidence-to-source extraction records. |

## Demo Path Classification

| File/module | Classification | Why | Recommendation |
| ----------- | -------------- | --- | -------------- |
| `bundles/sce_vegetation/artifacts/demo_model_output.json` | central-demo-path | Represents the Neara-style model delta/watch point input. | Keep central, but rename/docs should make clear it is a clean Neara-style output fixture. |
| `bundles/sce_vegetation/corus.bundle.yaml` | central-demo-path | Wraps model output and contracts into Corus intake. | Keep as the handoff contract from Neara output to Corus value translation. |
| `tests/fixtures/sce_vegetation/observations.timpos` | supporting-provenance | Anchors observations in time/place, but does not itself translate value. | Keep visible as provenance for demo claims. |
| `tests/fixtures/sce_vegetation/sce.domain` | central-demo-path | Defines SCE meaning nodes for the translation path. | Keep central; add customer/source approval metadata later. |
| `tests/fixtures/sce_vegetation/sce.surface` | central-demo-path | Encodes the operational graph from model delta to customer value. | Keep central; prioritize edge-level audit and evidence references. |
| `tests/fixtures/sce_vegetation/vegetation_ops.lens` | central-demo-path | Routes attention for vegetation operations. | Keep central; test selected path stability. |
| `tests/fixtures/sce_vegetation/sce_grid_ops.profile` | central-demo-path | Defines core question and permissions for grid ops. | Keep central; expand permission proof only as needed for demo. |
| `tests/fixtures/sce_vegetation/neara_value_architect.profile` | central-demo-path | Defines the value-translation role/persona. | Keep central if the demo includes role-specific value framing. |
| `tests/fixtures/sce_vegetation/sce_customer.value` | central-demo-path | Maps operational context to customer value. | Keep central; label synthetic/customer-approved metrics explicitly. |
| `tests/fixtures/sce_vegetation/sce.evidence` | central-demo-path | Carries business assumptions used by operational trace. | Keep central, but split or annotate source-backed versus synthetic assumptions. |
| `tests/fixtures/sce_vegetation/ledger/*` | supporting-provenance | Proves admission, payload hashes, and READ replay around claims. | Keep as provenance/audit substrate, not the product story by itself. |
| `corus/playground.py` | central-demo-path | Implements validate/reconstruct/project/explain/diff/agent-run demo commands. | Keep as demo CLI; extract operational trace/work packet modules if complexity grows. |
| `corus/__main__.py` | central-demo-path | Makes `python -m corus` the current demo entry point. | Keep primary for demo instructions. |
| `kernel/engine/runtime.py` | central-demo-path | Reconstructs and projects domain/surface/lens/profile/value context. | Keep central; add explicit value-story contract if needed. |
| `kernel/domain/*`, `kernel/surface/*`, `kernel/lens/*`, `kernel/profile/*`, `kernel/value/*` | central-demo-path | Contract loaders/validators for translation layers. | Keep central and protect with conformance tests. |
| `kernel/audit/*` | central-demo-path | Supplies proof for what can be audited/replayed. | Keep central; build source authority and object-level lineage next. |
| `kernel/ledger/*` | supporting-provenance | Provides WRITE/READ/AUDIT substrate. | Keep as supporting proof layer for value translation. |
| `kernel/source/*` | supporting-provenance | Creates source/extent/validation objects and materializes ledger payloads. | Keep as provenance PoC; avoid presenting it as main Neara demo flow. |
| `kernel/fixtures/neara_sce/*` | central-demo-path | Contains Neara/SCE value translation fixture names and contracts. | Review for duplication with `tests/fixtures/sce_vegetation`; consolidate if redundant. |
| `tests/fixtures/neara_policy_delta/*` | central-demo-path | Exercises policy/domain delta explanation. | Keep if framed as delta/value translation, not physical model reconstruction. |
| `tests/fixtures/eaton_poc/sources/eaton_perimeter.geojson` | future-upstream | Raw GeoJSON source-add fixture; useful for provenance, not core Neara demo. | Keep separate from Neara demo narrative. |
| `sources/eaton_fire/incident/eaton_perimeter_20250121.geojson` | future-upstream | Raw incident geometry can imply GIS reconciliation if foregrounded. | Document as upstream/source provenance experiment. |
| `kernel/connect/arcgis.py`, `kernel/connect/geo.py`, `kernel/connect/laz.py`, `kernel/connect/pdf.py`, `kernel/connect/web.py`, `kernel/connect/csv.py` | future-upstream | Connector names suggest Corus will ingest raw GIS/LiDAR/PDF/web sources. | Mark experimental/out-of-scope for Neara demo to avoid competing-with-Neara framing. |
| `fs/04_evidence/sources/*` | supporting-provenance | Older source references can support assumptions. | Keep only if linked to evidence authority; otherwise label legacy/demo. |
| `fs/04_evidence/inputs/sce/model-output.input` | central-demo-path | Older model-output input aligns with value translation. | Decide whether to migrate into current fixture path or mark legacy. |
| `fs/01_protocols/contracts/*` | supporting-provenance | Older contracts mirror domain/surface/profile/value concepts. | Keep as legacy/protocol examples or consolidate with active fixtures. |
| `fs/02_programs/neara-value-intake.program` | unclear | Name is aligned with translation, but current demo uses `python -m corus`. | Clarify whether this remains a supported demo path. |
| `fs/03_processes/runs/*` | stale-or-misleading | Generated run history obscures the current clean demo path. | Archive or move out of source tree unless used as fixtures. |
| `kernel/command/cli.py` | stale-or-misleading | Installed Typer CLI competes with `python -m corus` as the visible entry point. | Decide one primary CLI surface for demo docs. |
| `kernel/run/*`, `kernel/transform/*` | unclear | Older program runner may still model value translation, but current tests/demo emphasize playground/runtime. | Either fold useful pieces into current demo path or label as legacy. |
| `timpo/*` | supporting-provenance | Provides when/where identity and deterministic encoding. | Keep as foundational provenance, not value translation logic. |

Code or fixture surfaces that can make Corus look like it competes with Neara are `kernel/connect/laz.py`, `kernel/connect/arcgis.py`, `kernel/connect/geo.py`, raw GeoJSON fixtures, raw PDF placeholders, and generated source/process material that foregrounds ingestion over value translation. These should remain clearly labeled as supporting provenance, future-upstream, or legacy experiments. The Neara demo should foreground the clean model-delta handoff and the SCE-specific translation into value, action, and why.

## 2. Repository Map

| Path | Purpose | Status | Evidence |
| ---- | ------- | ------ | -------- |
| `corus/` | Current module entry point and playground CLI. | active | `corus/__main__.py` calls `corus.playground.main`; `tests/test_playground_cli.py` covers commands. |
| `kernel/audit/` | AUDIT proof pipeline. | active | `tests/ledger/test_ledger_read_audit.py` covers target resolver, ledger, payload, admissibility, replay, permissions. |
| `kernel/ledger/` | Ledger store and READ active context. | active | `LedgerStore.write/verify_chain`; `read_active_context`; ledger tests. |
| `kernel/source/` | Source/extent/validation PoC object files and materialization. | active | `tests/test_source_add.py` covers creation, hashing, materialization, ledger write. |
| `kernel/domain/`, `kernel/surface/`, `kernel/lens/`, `kernel/profile/`, `kernel/value/` | Load and validate contract layers. | active | Conformance tests directly import loaders/validators. |
| `kernel/engine/` | Runtime reconstruction from domain/surface/lens/profile/value. | active | Scenario, determinism, reconstruction tests use `resolve_context`. |
| `kernel/run/` | Older program runner over `fs/` process contracts. | partial | `tests/test_program_run.py` covers `run_program`; less central to current ledger READ/AUDIT. |
| `kernel/command/` | Typer CLI for older `corus` script. | partial | `pyproject.toml` script entry points here; README quickstart uses it; current demo uses `python -m corus`. |
| `kernel/connect/` | Connector stubs/adapters. | likely stale | No direct tests found in collected suite; imports compile but no runtime evidence. |
| `kernel/verify/` | Hashing, validation, replay/diff utilities. | active/partial | `hash.py` and `validate.py` used; `diff.py`/`replay.py` appear thin or older. |
| `kernel/transform/` | Older domain/surface/profile/value transforms for program runner. | partial | Used by `kernel/run/run_program.py`, covered by `tests/test_program_run.py`. |
| `timpo/` | Timpo codec and Mojo benchmark/tests. | active | `pixi run test` runs Mojo tests and benchmark; Python codec tests pass. |
| `tests/` | Architectural, conformance, scenario, CLI, ledger, and PoC tests. | active | 227 collected; 182 passed, 45 xfailed. |
| `tests/fixtures/sce_vegetation/` | Main SCE demo fixture with ledger and contracts. | fixture-only | Used by most CLI/ledger/scenario tests. |
| `tests/fixtures/eaton_poc/` | Source-add PoC GeoJSON fixture. | fixture-only | Used by `tests/test_source_add.py`. |
| `tests/fixtures/neara_policy_delta/` | Before/after domain delta fixture. | fixture-only | Used by diff/policy delta tests. |
| `bundles/sce_vegetation/` | Intake bundle demo wrapper. | active fixture | Used by `tests/test_intake_bundle.py` and docs. |
| `fs/` | Older Corus filesystem: protocols, programs, process runs, evidence. | partial/generated | README and Typer CLI use it; many `fs/03_processes/runs/*` are generated. |
| `docs/` | Architecture/demo/audit/intake docs. | active | Current review, audit matrix, demo and intake docs. |
| `.pixi/`, `.venv/`, `corus_workbench.egg-info/`, `.pytest_cache/` | Tooling/generated metadata. | generated | Present in `find`; should not be treated as source. |

## 3. Runtime Entry Points

| Entry Point | What it does | Files/modules touched | Confidence |
| ----------- | ------------ | --------------------- | ---------- |
| `python -m corus validate <fixture>` | Validates Timpo/domain/surface/lens/profile/value/evidence files. | `corus/playground.py`, loaders/validators. | high |
| `python -m corus reconstruct <fixture>` | Runs deterministic reconstruction summary. | `corus/playground.py`, `kernel.engine.runtime`. | high |
| `python -m corus project <fixture>` | Resolves profile/lens projection. | `corus/playground.py`, runtime/lens. | high |
| `python -m corus read <fixture>` | Reads ledger active context and prints included/excluded claims. | `kernel.ledger.read`, `LedgerStore`. | high |
| `python -m corus audit <fixture> --target ...` | Emits proof for claim/output/ledger/payload/object-like targets. | `kernel.audit.*`, `kernel.ledger.*`. | high |
| `python -m corus explain <fixture>` | Emits architectural and operational traces. | `corus/playground.py`, runtime/evidence fixture. | high |
| `python -m corus diff <fixture>` | Diffs policy/domain fixture. | `corus/playground.py`. | high |
| `python -m corus agent-run <fixture>` | Deterministic, no-LLM agent-run demo. | `corus/playground.py`, runtime/profile permissions. | high |
| `python -m corus ingest <bundle> --out <run>` | Builds ledger-backed run from manifest bundle. | `corus/playground.command_ingest`, `LedgerStore`. | high |
| `python -m corus source add ...` | Source artifact to `.source/.extent/.validation` and ledger entries. | `kernel.source.*`, `LedgerStore`. | high |
| `corus fs/protocol/program/process/engine ...` installed script | Older Typer CLI over `fs/` and program runner. | `kernel.command.cli`, `kernel.run.*`. | medium |
| `pixi run test` | Mojo Timpo tests, Timpo benchmark, pytest. | `pixi.toml`, `timpo`, tests. | high |
| `kernel.run.run_program` | Program-run value pipeline over `fs/`. | `kernel/run`, `kernel/transform`. | medium |

## 4. Architecture Coverage

| Layer | Intended responsibility | Current implementation | Coverage | Notes |
| ----- | ----------------------- | ---------------------- | -------- | ----- |
| Source intake | Bring external artifacts into provenance. | `ingest` bundle and `source add` PoC. | partial | Files become provenance; no adapters/extraction. |
| Interpretation | Convert manifest/source info into candidates/objects. | Manifest claims -> `interpret`; source -> `.extent`. | partial | Explicit only, no automated interpretation. |
| Validation | Decide admissibility. | Claim validations and extent validation object. | partial | Claims affect READ; extents only ledger/audit target currently. |
| Ledger admission | Append payloads with hashes and prev continuity. | `LedgerStore.write`. | implemented | Strong tests for payload and chain tampering. |
| Ledger verification | Recompute entry hash and prev chain. | `verify_ledger_chain_check`, `LedgerStore.verify_chain`. | implemented | Per-entry evidence emitted in proofs. |
| Payload verification | Verify `payload_ref` contents match `payload_hash`. | `verify_payload_hashes`. | implemented | Explicit proof evidence. |
| Domain loading | Load meaning nodes. | `kernel.domain.loader/validate`. | implemented | Good conformance tests. |
| Surface graph loading | Load relationships over domain nodes. | `kernel.surface.loader/validate`. | implemented | Good dangling-edge tests. |
| Lens weighting / routing | Weight graph and select first-order context. | `kernel.lens.weighting`, runtime. | implemented | Deterministic and scenario tests. |
| Profile permissions | Govern generated output actions. | `kernel.audit.permissions`; demo agent-run reads profile fields. | implemented for output targets | No multi-step approval workflow. |
| Value evaluation | Translate projected context to customer value. | `kernel.value.resolve`, `kernel.transform.compute_value`. | partial | Useful but fixture/program-specific. |
| Evidence grounding | Connect facts to source observations. | `.evidence` fixture and operational trace. | synthetic-only/partial | Facts are source-labeled but not independently verified. |
| Read reconstruction | Build active context from ledger. | `read_active_context`. | partial | Claims only; extents not active context. |
| Explain / because trace | Show why context/output exists. | `command_explain`, runtime `because_trace`. | partial | Operational trace is more specific than runtime generic trace. |
| Diff / comparison | Explain mismatches/deltas. | Policy fixture diff; audit comparison placeholder. | placeholder | AUDIT-006 remains missing. |
| Audit proof emission | Structured proof object and hash. | `audit_target`. | implemented/partial | Strong for claims/output permissions, not object paths/source authority. |
| CLI | Demo and legacy commands. | `python -m corus` plus Typer script. | implemented but split | Needs ownership decision. |
| Tests | Preserve architecture behavior. | 227 tests, 45 xfails. | implemented | Tests are the clearest protocol statement. |
| Fixtures | Provide SCE/Neara/Eaton examples. | `tests/fixtures`, `bundles`, `fs`. | synthetic-only/partial | Good demos but source-backed trust boundary incomplete. |

## 5. Used vs Unused Code

Coverage was unavailable: `.venv/bin/python -m coverage run -m pytest` failed with `No module named coverage`. Usage below is estimated from test imports, CLI paths, and pytest collection.

### Clearly Used

| File/module | Used by | Evidence |
| ----------- | ------- | -------- |
| `corus/playground.py` | `python -m corus`, CLI tests. | `corus/__main__.py`; `tests/test_playground_cli.py`. |
| `kernel/ledger/store.py` | ingest, source add, audit/read tests. | `tests/ledger/test_ledger_read_audit.py`, `tests/test_intake_bundle.py`, `tests/test_source_add.py`. |
| `kernel/ledger/read.py` | READ and audit replay. | `command_read`, `kernel.audit.replay`, tests. |
| `kernel/audit/*` | audit proofs. | `tests/ledger/test_ledger_read_audit.py`. |
| `kernel/source/*` | source-add PoC. | `tests/test_source_add.py`; `python -m corus source add`. |
| `kernel/domain/*`, `surface/*`, `lens/*`, `profile/*`, `value/*` | Runtime and conformance. | Direct test imports and `resolve_context`. |
| `kernel/engine/runtime.py` | project/reconstruct/explain/agent-run and tests. | `tests/scenarios`, `tests/reconstruction`. |
| `kernel/engine/canonicalize.py`, `hashing.py` | Determinism and hashing. | `tests/determinism/*`. |
| `kernel/run/*`, `kernel/transform/*` | Older program run. | `tests/test_program_run.py`, Typer `program run`. |
| `kernel/verify/hash.py`, `validate.py` | YAML/hash/semantic validation. | Tests and runtime imports. |
| `timpo/src`, `timpo/python/codec.py` | Timpo tests/benchmark. | `pixi run test`, `timpo/tests/test_timpo_codec.py`. |

### Possibly Used

| File/module | Why uncertain | How to verify |
| ----------- | ------------- | ------------- |
| `kernel/command/cli.py` | Installed script target but current demo uses `python -m corus`. | Run `corus ...` smoke tests or decide CLI ownership. |
| `kernel/verify/diff.py`, `kernel/verify/replay.py` | Names suggest old verification path; not prominent in current audit. | Add import/use tests or archive. |
| `kernel/surface/edges.py`, `graph.py` | Used by loaders/validators but small. | Already indirectly covered. |
| `kernel/run/record_process.py` | Used by old program runner; generated many `fs` runs. | Keep if `fs` program path remains supported. |
| `fs/01_protocols/*` schemas/contracts | Used by old Typer protocol validation, not current playground. | Run installed `corus protocol validate` regularly. |

### Likely Unused or Stale

| File/module | Why it appears unused | Recommendation |
| ----------- | --------------------- | -------------- |
| `kernel/connect/*` | No direct tests or current CLI references found. | Mark experimental or move behind future connector docs. |
| Many `fs/03_processes/runs/*` | Generated historical process outputs, large and repetitive. | Archive or keep outside source tree if not part of test fixtures. |
| `kernel/fixtures/neara_sce` | Referenced by Typer `engine resolve-cody`, not shown in `find -maxdepth 3`. | Verify existence/depth and decide whether legacy. |
| `corus_workbench.egg-info/` | Generated packaging metadata. | Do not treat as source; consider cleanup from repo if tracked. |

Rough summary:

- Total Python files under `corus`, `kernel`, `tests`, `timpo`: 116.
- Product/runtime Python files under `corus`, `kernel`, `timpo`: 75.
- Test Python files: 41.
- Files touched by tests: at least 40 product modules are directly or indirectly imported; no coverage tool available to prove exact count.
- Files imported by runtime entry points: most core modules plus source/audit/ledger/runtime; `connect` appears isolated.
- Files that appear isolated or stale: roughly 8-15, depending on whether old `fs` program paths are retained.
- Estimated active code percentage: 70-80% for Python modules; lower if `fs/` generated artifacts are counted as codebase surface.

## 6. Test Coverage Review

| Test file | What it covers | Architectural value | Gaps |
| --------- | -------------- | ------------------- | ---- |
| `tests/ledger/test_ledger_read_audit.py` | Ledger semantics, READ inclusion/exclusion, audit proof checks. | Very high | Object audit and detailed diff still missing. |
| `tests/test_playground_cli.py` | Human/JSON CLI outputs and demo path. | High | CLI ownership split not covered. |
| `tests/test_intake_bundle.py` | Manifest bundle -> ledger -> read/audit. | High | No real file extraction/authority. |
| `tests/test_source_add.py` | Source/extent/validation PoC and geometry hash stability. | High | Extents not yet READ active context. |
| `tests/conformance/*` | Contract boundaries for timpo/domain/surface/lens/profile/value. | High | Mostly validates shape, not external truth. |
| `tests/determinism/*` | Hash stability and golden outputs. | High | Golden files lock demo behavior, not real evidence. |
| `tests/reconstruction/*` | Context lineage and because trace. | High | Because trace partly synthetic/generic. |
| `tests/scenarios/*` | SCE/Neara demo outcomes. | Medium-high | Scenario data synthetic. |
| `tests/agentic/*` | Desired future agent behavior. | High as spec | Most are xfailed; runtime absent. |
| `timpo/tests/test_timpo_codec.py` | Timpo encoding round-trips/goldens. | High | Separate from Corus ledger admission. |
| `tests/test_program_run.py` | Older `fs` program execution. | Medium | Only one test; current demo path differs. |
| `tests/test_protocol_validate.py` | Semantic document validation. | Medium | Validation schema appears minimal. |

Well covered:

- Ledger append/hash/prev-hash semantics.
- Claim admissibility and READ inclusion/exclusion.
- Audit proof check statuses and validity rule.
- CLI demo output.
- Contract layer separation.
- Deterministic hashing.
- Timpo codec behavior.

Xfailed:

- `tests/XFAILS.md` reports 45 xfails.
- Most are agent runtime gaps: graph traversal, permission boundaries, action initiation, missing-context behavior, no-fabrication reports, audit events, replayability.
- One determinism xfail: context reconstruction does not yet ingest Timpo ledgers as runtime inputs.
- One malformed fixture xfail: lens entrypoint validation as agent-runtime contract.

Missing:

- Coverage metrics.
- Real source authority tests.
- Object-level audit paths.
- Detailed projection diff tests beyond placeholder status.
- Tests proving READ never consults out-of-ledger claims in source/extent flows.

## 7. Fixture and Source Grounding Review

| File | Type | Source-backed? | Synthetic? | Used by | Notes |
| ---- | ---- | -------------- | ---------- | ------- | ----- |
| `tests/fixtures/sce_vegetation/observations.timpos` | Timpo anchors | Partly | yes | SCE tests | `payload.source: demo`; coordinates/time are demo anchors. |
| `tests/fixtures/sce_vegetation/sce.evidence` | Evidence facts | Partly | yes | explain/scenario tests | Uses source labels but facts are asserted fixture content. |
| `tests/fixtures/sce_vegetation/sce.domain` | Domain contract | No external source | yes | runtime/tests | Encodes meaning and business ontology. |
| `tests/fixtures/sce_vegetation/sce.surface` | Surface graph | No external source | yes | runtime/tests | Encodes relationship assumptions. |
| `tests/fixtures/sce_vegetation/vegetation_ops.lens` | Lens weights | No external source | yes | runtime/tests | Encodes attention/priority assumptions. |
| `tests/fixtures/sce_vegetation/*.profile` | Profile permissions/questions | No external source | yes | runtime/audit | Important governance assumptions. |
| `tests/fixtures/sce_vegetation/sce_customer.value` | Value criteria | No external source | yes | value/scenario tests | Business value assumptions. |
| `tests/fixtures/sce_vegetation/ledger/*` | Ledger demo history | Internally hash-backed | yes | read/audit tests | Strong provenance inside fixture, but source data synthetic. |
| `bundles/sce_vegetation/corus.bundle.yaml` | Intake manifest | Manifest-backed | yes | ingest tests | Explicitly creates candidate claims/validations. |
| `bundles/sce_vegetation/artifacts/demo_model_output.json` | Source artifact | File-backed | yes | ingest tests | Demo artifact; no extraction. |
| `bundles/sce_vegetation/artifacts/sce_public_source.pdf` | Placeholder PDF | File-backed | yes | docs/bundle | Not parsed; should not imply truth. |
| `tests/fixtures/eaton_poc/sources/eaton_perimeter.geojson` | Source artifact | File-backed fixture | yes | source-add tests | Raw bytes and normalized geometry hash are proven. |
| `sources/eaton_fire/incident/eaton_perimeter_20250121.geojson` | Source artifact | File-backed | unclear | source-add docs/path | Needs provenance if used beyond PoC. |
| `tests/fixtures/neara_policy_delta/*.domain` | Domain delta fixture | No external source | yes | diff tests | Useful for diff mechanics, not source authority. |
| `fs/04_evidence/*` | Older evidence/source/input files | Mixed | likely demo | Typer/program path | Some source-named files, but source authority not audited. |

Real source inputs today:

- The Eaton GeoJSON fixture is real in the limited sense that raw bytes are hashed and geometry is normalized/hashes are stable.
- Bundle artifacts are file-backed but demo/synthetic.

Synthetic claims:

- `claim.sce.watch_points_added`, `claim.sce.unsupported_cost_assumption`, SCE value/cost facts, and Neara repeatable pattern facts.

Business/domain assumptions:

- `.domain`, `.surface`, `.lens`, `.profile`, `.value`, and `.evidence` all encode business assumptions. These are testable contracts, not externally proven truth.

Highest-risk synthetic files if demoed as real:

- `sce.evidence`, `sce_customer.value`, `sce.surface`, and profile permissions. These make the demo compelling but should eventually cite real source references or explicit user approval.

## 8. Structural Soundness

| Finding | Severity | Evidence | Recommendation |
| ------- | -------- | -------- | -------------- |
| The Neara value translation path is structurally coherent. | low | Bundle/model output, domain, surface, lens/profile, value, evidence, explain, agent-run, READ, and AUDIT all exist and are test-backed. | Keep the demo centered on translating model deltas into SCE-specific value/action/why. |
| Two CLI surfaces exist. | medium | `python -m corus` uses `corus/playground.py`; `pyproject.toml` script uses `kernel.command.cli:app`. | Decide whether Typer `corus` is legacy or primary; avoid split user mental model. |
| WRITE/READ/AUDIT boundaries are now clearer than older fs/program boundaries. | low | Ledger/audit/source modules are cohesive; `fs` program runner remains. | Preserve both only if docs explain their different roles. |
| Audit validity is well-structured around check statuses. | low | `audit_target._compute_valid` and tests enforce pass/not_applicable only. | Keep this rule protected. |
| Evidence grounding is currently label-based, not authority-based. | high | `sce.evidence` uses `source_observation: demo_model_output`; no source authority verifier. | Build source authority/admissibility model before real-world claims. |
| Object file grammar is cleaner than current ledger payload grammar. | medium | `kernel/source/materialize.py` compiles object files into payloads. | Continue materialization layer; do not prematurely refactor ledger. |
| READ only handles candidate claims as active context. | medium | `read_active_context` only includes interpreted candidate claims. | Add typed active context objects deliberately when needed. |
| Raw-source surfaces can misframe the demo as competing with Neara. | medium | `kernel/connect/laz.py`, `kernel/connect/arcgis.py`, `kernel/connect/geo.py`, PDF placeholders, and raw GeoJSON fixtures foreground upstream ingestion. | Mark them supporting/future-upstream and keep demo narrative focused on clean Neara output. |
| `connect` modules are premature or dormant. | low | No tests or current CLI references. | Mark experimental, future-upstream, or archive. |
| Generated `fs/03_processes/runs` clutter obscures source. | low | Many timestamped preserved runs in `find` output. | Move generated runs to ignored/run storage or fixture subset. |
| Compileall default behavior fails due macOS bytecode cache permissions. | low | `compileall .` and project-only compile failed until `PYTHONPYCACHEPREFIX=/private/tmp/...`. | Document or configure compile checks to set cache prefix. |

## 9. Audit Architecture Review

| Audit capability | Current status | Evidence | Missing piece |
| ---------------- | -------------- | -------- | ------------- |
| target resolver | implemented for claims, outputs, ledger entries, payload hashes, extension IDs; placeholder for domain/surface/profile/value objects | `kernel/audit/target.py`, tests | Full object path tracing and AUDIT-007B. |
| ledger verifier | implemented | `verify_ledger_chain_check`, tests | Rich schema diagnostics optional. |
| payload verifier | implemented | `verify_payload_hashes`, tests | Schema/evidence semantics. |
| admissibility resolver | implemented for candidate claims | `kernel/audit/admissibility.py` | Non-claim object admissibility and source authority. |
| read replay engine | implemented for projection hash comparison | `kernel/audit/replay.py` | Detailed mismatch diff. |
| diff/comparison engine | placeholder | `compare_projection_placeholder` | AUDIT-006. |
| profile permission verifier | implemented for generated output targets | `kernel/audit/permissions.py` | Approval workflows and non-output permissions. |
| proof emitter | implemented/partial | `audit_target` emits proof hash and checks | Stronger source/evidence proof and object lineage. |

What can currently be audited:

- Included and excluded candidate claims.
- Generated output permission against referenced profile contract.
- Ledger entries and payload hashes.
- Raw entry hashes and payload hashes.
- Source/extent-style extension targets at target-resolution level.

What cannot yet be audited:

- Real source authority.
- Object-level paths for domain nodes/surface edges/profile/value objects.
- Detailed projection differences.
- Whether evidence facts are externally true.
- Agent runtime decisions beyond deterministic demo output.

What proof actually proves today:

- Ledger entries have correct hashes and continuity.
- Payload files match ledger hashes.
- Candidate claims were interpreted and validated, and READ inclusion/exclusion matches latest validation.
- Output action is allowed by referenced profile file.
- Optional claimed READ projection hash either matches or does not.

What proof may appear to claim but does not prove yet:

- That an SCE/Neara business fact is true in the world.
- That a PDF/source artifact supports a claim.
- That domain/surface/value assumptions are externally authorized.

What would make audit trustworthy:

- Source authority verifier.
- Evidence-to-claim lineage with file hashes and extraction/admission records.
- Object-level audit for domain/surface/value/profile elements.
- Detailed diff/comparison for replay mismatches.
- Clear separation of demo-synthetic and customer-source-backed fixtures.

## 10. Recommended Cleanup Plan

### Keep

- `kernel/ledger/*`: reason: central WRITE/READ substrate; benefit: preserves auditability; risk: low.
- `kernel/audit/*`: reason: strongest architectural foundation; benefit: explicit proof semantics; risk: medium if overextended before source authority.
- `kernel/source/*`: reason: clean source/extent object grammar; benefit: future real-world ingestion path; risk: low.
- `kernel/domain/surface/lens/profile/value`: reason: clear layer contracts; benefit: conformance guarantees; risk: low.
- `tests/ledger`, `tests/conformance`, `tests/test_source_add.py`, `tests/test_intake_bundle.py`: reason: architectural guarantees; benefit: protects direction; risk: low.

### Clarify

- CLI ownership: affected files `corus/playground.py`, `kernel/command/cli.py`, `pyproject.toml`; benefit: less user confusion; risk: medium because docs/scripts may rely on both.
- Synthetic fixture labeling: affected `tests/fixtures/sce_vegetation/*`, `bundles/sce_vegetation/*`; benefit: demo credibility; risk: low.
- READ object model: affected `kernel/ledger/read.py`; benefit: typed active context beyond claims; risk: medium.

### Refactor

- Move demo-specific operational trace logic out of `corus/playground.py` if it grows; benefit: CLI stays thin; risk: low.
- Extract ingest command from playground into `kernel/intake` once bundle handling grows; benefit: cleaner WRITE boundary; risk: low.
- Align object-file grammar and ledger payload grammar through stable materializers; benefit: cleaner protocol evolution; risk: medium.

### Remove or Archive

- `kernel/connect/*` if no near-term connector implementation; benefit: reduce perceived capability; risk: low.
- Generated `fs/03_processes/runs/*` outside source tree or under explicit fixtures; benefit: reduce noise; risk: medium if used by demos.
- `corus_workbench.egg-info` if tracked/generated; benefit: clean repo; risk: low.

### Build Next

- Source authority/admissibility verifier for assumptions: reason: value translation must distinguish source-backed from synthetic; files: `kernel/audit`, `kernel/source`, fixtures; benefit: demo credibility; risk: high design impact.
- AUDIT-006 diff comparison: reason: replay mismatch currently says placeholder; files: `kernel/audit/proof.py`; benefit: proof explains failures; risk: medium.
- AUDIT-007B object-level paths: reason: domain/surface/value audit is core to proving the translation path; benefit: audit can prove more than ledger existence; risk: high.
- Value story and work packet output contracts: reason: the demo endpoint should clearly answer why it matters and who acts; files: `corus/playground.py`, fixtures, docs; benefit: stronger product story; risk: medium.
- Typed READ for extents: reason: source-add PoC should become visible in context when provenance is part of the demo; benefit: source->extent lifecycle completes; risk: medium.
- CLI consolidation: reason: two surfaces split architecture; benefit: coherent product; risk: medium.

## 11. Top 10 Questions for Jeremy

1. Is the ledger the only canonical source after admission, or are `.source/.extent/.validation` files canonical before materialization?
2. Should READ ever use files outside the ledger, or only ledger-admitted payloads?
3. Is `.evidence` required for every domain/surface/value claim, or only for operational facts?
4. What makes a source authority acceptable: user validation, file hash, known source type, external signature, or policy?
5. Are `.domain`, `.surface`, `.lens`, `.profile`, and `.value` protocol examples, demo assets, or customer-specific contracts?
6. Should synthetic demo files be allowed in the same paths as production fixtures?
7. What must an audit proof prove before the SCE/Neara demo is credible to an external viewer?
8. Should object-level audit target domain nodes, surface edges, profile permissions, and value metrics by stable IDs?
9. Should the Typer `corus` CLI survive, or should `python -m corus` become the only command surface?
10. Is Timpo strictly when/where identity, or should Timpo-ledger admission become the primary observation history for READ?

## 12. Final Assessment

This codebase is a Neara value-translation demo engine plus early protocol implementation. It has crossed beyond a sketch: the path from Neara-style model delta to SCE domain/surface/lens/profile/value/evidence, explain, READ, AUDIT, and deterministic work action is real and test-backed. It is not yet production-shaped because external source authority, object-level audit, detailed diffing, and formal value-story/work-packet output contracts are missing.

Strongest part:

- The translated value path plus audit/ledger proof structure. The system can now say what changed, why it matters to the customer, why a claim is included/excluded, and why an output action is allowed by profile.

Weakest part:

- Assumption grounding. The demo is honest in code when treated as synthetic, but many business/value facts are asserted by fixtures rather than proven from external evidence or customer approval.

Protect:

- The validity rule: only `pass` and `not_applicable` checks make proofs valid.
- Layer separation tests.
- Ledger hash/payload hash verification.
- Explicit interpretation and validation before READ inclusion.

Simplify:

- CLI split.
- Generated `fs` run clutter.
- Dormant connector surface.

Build next:

- Source authority, object-level audit, and explicit value-story/work-packet output contracts. Those pieces would make the Neara demo much harder to mistake for either synthetic storytelling or an attempt to rebuild Neara's upstream modeling.

## Command Log

| Command | Result | Notes |
| ------- | ------ | ----- |
| `pwd` | pass | `/Users/jeremycapps/Documents/corus/corus-workbench`. |
| `git status --short` | fail | Not a git repository. Non-blocking for architecture review. |
| `find . -maxdepth 3 -type f \| sort` | pass | Revealed source, docs, fixtures, generated env/cache files. |
| `python -m pytest` | fail | `python` command not found in shell. Used `.venv/bin/python` equivalent. |
| `.venv/bin/python -m pytest` | pass | 182 passed, 45 xfailed in 10.00s. |
| `pixi run test` | pass | Mojo tests/benchmark plus pytest: 182 passed, 45 xfailed in 6.68s. |
| `python -m coverage run -m pytest` | fail | `python` missing; `.venv/bin/python -m coverage...` also failed because coverage is not installed. |
| `.venv/bin/python -m pytest --collect-only` | pass | 227 tests collected. |
| `.venv/bin/python -m compileall .` | fail | Walked `.pixi` and hit macOS Python cache permission errors. |
| `.venv/bin/python -m compileall corus kernel tests timpo` | fail | Same cache permission path. |
| `env PYTHONPYCACHEPREFIX=/private/tmp/corus_pycache .venv/bin/python -m compileall corus kernel tests timpo` | pass | Project source compiles with writable bytecode cache. |
