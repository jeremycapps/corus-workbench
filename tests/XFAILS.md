# Expected Failures

The suite allows `xfail` only for intentional Corus conformance gaps. Current total: 45 xfails.

## 1. Agent Runtime Not Implemented

These tests require a concrete agent runtime API that does not exist yet.

### Graph Traversal

- `test_agent_starts_from_profile_selected_lens`
  - File: `tests/agentic/test_agent_graph_traversal.py`
  - Current reason: agent runtime not implemented: graph traversal API and selected path are not exposed
  - Category: Agent runtime not implemented
  - Needed to pass: expose an agent run object with profile ID, lens ID, and profile-allowed lenses.
- `test_agent_enters_graph_through_valid_lens_entrypoint`
  - File: `tests/agentic/test_agent_graph_traversal.py`
  - Current reason: agent runtime not implemented: graph traversal API and selected path are not exposed
  - Category: Agent runtime not implemented
  - Needed to pass: expose the agent graph entrypoint and surface node IDs.
- `test_agent_traverses_only_valid_surface_edges`
  - File: `tests/agentic/test_agent_graph_traversal.py`
  - Current reason: agent runtime not implemented: graph traversal API and selected path are not exposed
  - Category: Agent runtime not implemented
  - Needed to pass: expose traversal steps with surface edge IDs.
- `test_agent_cannot_jump_to_unrelated_nodes`
  - File: `tests/agentic/test_agent_graph_traversal.py`
  - Current reason: agent runtime not implemented: graph traversal API and selected path are not exposed
  - Category: Agent runtime not implemented
  - Needed to pass: expose selected node IDs constrained to the surface graph.
- `test_agent_returns_selected_path`
  - File: `tests/agentic/test_agent_graph_traversal.py`
  - Current reason: agent runtime not implemented: graph traversal API and selected path are not exposed
  - Category: Agent runtime not implemented
  - Needed to pass: return a selected traversal path.
- `test_agent_returns_reason_trace_for_path`
  - File: `tests/agentic/test_agent_graph_traversal.py`
  - Current reason: agent runtime not implemented: graph traversal API and selected path are not exposed
  - Category: Agent runtime not implemented
  - Needed to pass: return a path-specific reason trace with lineage.

### Permission Boundaries

- `test_agent_can_read_permitted_graph_region`
  - File: `tests/agentic/test_agent_permission_boundaries.py`
  - Current reason: agent runtime not implemented: permission boundary decisions are not exposed
  - Category: Agent runtime not implemented
  - Needed to pass: expose profile-derived read permissions.
- `test_agent_cannot_read_blocked_graph_region`
  - File: `tests/agentic/test_agent_permission_boundaries.py`
  - Current reason: agent runtime not implemented: permission boundary decisions are not exposed
  - Category: Agent runtime not implemented
  - Needed to pass: expose denied reads for blocked graph regions.
- `test_agent_can_propose_allowed_action`
  - File: `tests/agentic/test_agent_permission_boundaries.py`
  - Current reason: agent runtime not implemented: permission boundary decisions are not exposed
  - Category: Agent runtime not implemented
  - Needed to pass: expose proposed/executed status for profile-allowed actions.
- `test_agent_requires_approval_for_restricted_action`
  - File: `tests/agentic/test_agent_permission_boundaries.py`
  - Current reason: agent runtime not implemented: permission boundary decisions are not exposed
  - Category: Agent runtime not implemented
  - Needed to pass: expose `approval_required` for restricted actions.
- `test_agent_cannot_execute_denied_action`
  - File: `tests/agentic/test_agent_permission_boundaries.py`
  - Current reason: agent runtime not implemented: permission boundary decisions are not exposed
  - Category: Agent runtime not implemented
  - Needed to pass: expose `denied` for actions outside profile authority.
- `test_agent_cannot_mutate_domain`
  - File: `tests/agentic/test_agent_permission_boundaries.py`
  - Current reason: agent runtime not implemented: permission boundary decisions are not exposed
  - Category: Agent runtime not implemented
  - Needed to pass: expose before/after domain hashes for agent runs.
- `test_agent_cannot_mutate_surface`
  - File: `tests/agentic/test_agent_permission_boundaries.py`
  - Current reason: agent runtime not implemented: permission boundary decisions are not exposed
  - Category: Agent runtime not implemented
  - Needed to pass: expose before/after surface hashes for agent runs.
- `test_agent_cannot_silently_change_profile`
  - File: `tests/agentic/test_agent_permission_boundaries.py`
  - Current reason: agent runtime not implemented: permission boundary decisions are not exposed
  - Category: Agent runtime not implemented
  - Needed to pass: expose before/after profile hashes for agent runs.

### Action Initiation

- `test_action_includes_initiating_profile_id`
  - File: `tests/agentic/test_agent_action_initiation.py`
  - Current reason: agent runtime not implemented: action initiation records are not exposed
  - Category: Agent runtime not implemented
  - Needed to pass: return action records with `initiated_by`.
- `test_action_includes_lens_id`
  - File: `tests/agentic/test_agent_action_initiation.py`
  - Current reason: agent runtime not implemented: action initiation records are not exposed
  - Category: Agent runtime not implemented
  - Needed to pass: return action records with lens ID.
- `test_action_includes_graph_path`
  - File: `tests/agentic/test_agent_action_initiation.py`
  - Current reason: agent runtime not implemented: action initiation records are not exposed
  - Category: Agent runtime not implemented
  - Needed to pass: return action records with graph path.
- `test_action_includes_permission_check`
  - File: `tests/agentic/test_agent_action_initiation.py`
  - Current reason: agent runtime not implemented: action initiation records are not exposed
  - Category: Agent runtime not implemented
  - Needed to pass: return action records with permission check result.
- `test_action_includes_reason_trace`
  - File: `tests/agentic/test_agent_action_initiation.py`
  - Current reason: agent runtime not implemented: action initiation records are not exposed
  - Category: Agent runtime not implemented
  - Needed to pass: return action records with reason trace.
- `test_action_creates_audit_event`
  - File: `tests/agentic/test_agent_action_initiation.py`
  - Current reason: agent runtime not implemented: action initiation records are not exposed
  - Category: Agent runtime not implemented
  - Needed to pass: return or persist an audit event for initiated actions.

### Missing Context

- `test_missing_domain_node_returns_context_gap`
  - File: `tests/agentic/test_agent_missing_context_behavior.py`
  - Current reason: agent runtime not implemented: missing-context statuses are not exposed
  - Category: Agent runtime not implemented
  - Needed to pass: return `context_gap` for missing domain nodes.
- `test_missing_surface_edge_returns_missing_relationship`
  - File: `tests/agentic/test_agent_missing_context_behavior.py`
  - Current reason: agent runtime not implemented: missing-context statuses are not exposed
  - Category: Agent runtime not implemented
  - Needed to pass: return `missing_relationship` for missing surface edges.
- `test_missing_lens_entrypoint_returns_invalid_lens_entrypoint`
  - File: `tests/agentic/test_agent_missing_context_behavior.py`
  - Current reason: agent runtime not implemented: missing-context statuses are not exposed
  - Category: Agent runtime not implemented
  - Needed to pass: return `invalid_lens_entrypoint`.
- `test_missing_profile_permission_returns_approval_required_or_denied`
  - File: `tests/agentic/test_agent_missing_context_behavior.py`
  - Current reason: agent runtime not implemented: missing-context statuses are not exposed
  - Category: Agent runtime not implemented
  - Needed to pass: return `approval_required` or `denied` for missing permission.
- `test_missing_value_metric_returns_value_gap`
  - File: `tests/agentic/test_agent_missing_context_behavior.py`
  - Current reason: agent runtime not implemented: missing-context statuses are not exposed
  - Category: Agent runtime not implemented
  - Needed to pass: return `missing_metric` for missing value metrics.
- `test_agent_proposes_intake_requirement_instead_of_fabricating`
  - File: `tests/agentic/test_agent_missing_context_behavior.py`
  - Current reason: agent runtime not implemented: missing-context statuses are not exposed
  - Category: Agent runtime not implemented
  - Needed to pass: propose intake requirements and expose empty fabrication lists.

### No Fabrication

- `test_agent_cannot_reference_unknown_domain_node`
  - File: `tests/agentic/test_agent_no_fabrication.py`
  - Current reason: agent runtime not implemented: fabrication reports are not exposed
  - Category: Agent runtime not implemented
  - Needed to pass: expose referenced nodes and domain node IDs.
- `test_agent_cannot_reference_unknown_surface_edge`
  - File: `tests/agentic/test_agent_no_fabrication.py`
  - Current reason: agent runtime not implemented: fabrication reports are not exposed
  - Category: Agent runtime not implemented
  - Needed to pass: expose referenced edges and surface edge IDs.
- `test_agent_cannot_create_value_metric`
  - File: `tests/agentic/test_agent_no_fabrication.py`
  - Current reason: agent runtime not implemented: fabrication reports are not exposed
  - Category: Agent runtime not implemented
  - Needed to pass: expose referenced metrics and value metrics.
- `test_agent_cannot_invent_permission`
  - File: `tests/agentic/test_agent_no_fabrication.py`
  - Current reason: agent runtime not implemented: fabrication reports are not exposed
  - Category: Agent runtime not implemented
  - Needed to pass: expose permission checks and profile permissions.
- `test_agent_cannot_emit_unsupported_because_claim`
  - File: `tests/agentic/test_agent_no_fabrication.py`
  - Current reason: agent runtime not implemented: fabrication reports are not exposed
  - Category: Agent runtime not implemented
  - Needed to pass: expose because claims with lineage.
- `test_agent_outputs_empty_fabrication_lists`
  - File: `tests/agentic/test_agent_no_fabrication.py`
  - Current reason: agent runtime not implemented: fabrication reports are not exposed
  - Category: Agent runtime not implemented
  - Needed to pass: expose explicit fabricated nodes/edges/metrics/permissions lists.

## 4. Replay/Audit Behavior Pending

- `test_agent_run_creates_audit_event`
  - File: `tests/agentic/test_agent_audit_events.py`
  - Current reason: agent runtime not implemented: audit event records are not emitted
  - Category: Replay/audit behavior pending
  - Needed to pass: emit audit events for agent runs.
- `test_audit_event_contains_input_hashes`
  - File: `tests/agentic/test_agent_audit_events.py`
  - Current reason: agent runtime not implemented: audit event records are not emitted
  - Category: Replay/audit behavior pending
  - Needed to pass: include observation/domain/surface/context/projection hashes in audit events.
- `test_audit_event_contains_profile_id`
  - File: `tests/agentic/test_agent_audit_events.py`
  - Current reason: agent runtime not implemented: audit event records are not emitted
  - Category: Replay/audit behavior pending
  - Needed to pass: include profile ID in audit events.
- `test_audit_event_contains_lens_id`
  - File: `tests/agentic/test_agent_audit_events.py`
  - Current reason: agent runtime not implemented: audit event records are not emitted
  - Category: Replay/audit behavior pending
  - Needed to pass: include lens ID in audit events.
- `test_audit_event_contains_action_result`
  - File: `tests/agentic/test_agent_audit_events.py`
  - Current reason: agent runtime not implemented: audit event records are not emitted
  - Category: Replay/audit behavior pending
  - Needed to pass: include action result in audit events.
- `test_audit_event_contains_because_trace_hash`
  - File: `tests/agentic/test_agent_audit_events.py`
  - Current reason: agent runtime not implemented: audit event records are not emitted
  - Category: Replay/audit behavior pending
  - Needed to pass: include because trace hash in audit events.
- `test_agent_action_is_replayable`
  - File: `tests/agentic/test_agent_replayability.py`
  - Current reason: agent runtime not implemented: replayable action records are not exposed
  - Category: Replay/audit behavior pending
  - Needed to pass: mark agent action records replayable.
- `test_replayed_agent_action_has_same_hash`
  - File: `tests/agentic/test_agent_replayability.py`
  - Current reason: agent runtime not implemented: replayable action records are not exposed
  - Category: Replay/audit behavior pending
  - Needed to pass: produce stable action hashes across replay.
- `test_replayed_agent_action_has_same_because_trace`
  - File: `tests/agentic/test_agent_replayability.py`
  - Current reason: agent runtime not implemented: replayable action records are not exposed
  - Category: Replay/audit behavior pending
  - Needed to pass: produce stable because trace hashes across replay.
- `test_replayed_agent_action_has_same_permission_result`
  - File: `tests/agentic/test_agent_replayability.py`
  - Current reason: agent runtime not implemented: replayable action records are not exposed
  - Category: Replay/audit behavior pending
  - Needed to pass: produce stable permission decisions across replay.
- `test_replay_fails_if_source_hashes_change`
  - File: `tests/agentic/test_agent_replayability.py`
  - Current reason: agent runtime not implemented: replayable action records are not exposed
  - Category: Replay/audit behavior pending
  - Needed to pass: invalidate replay when source hashes change.

## 5. Intentional Conformance Target

- `test_reject_lens_missing_entrypoint`
  - File: `tests/boundaries/test_malformed_fixtures.py`
  - Current reason: lens entrypoint validation is an agent-runtime contract not implemented yet
  - Category: Intentional conformance target
  - Needed to pass: add lens entrypoint validation and return `invalid_lens_entrypoint`.
- `test_timpo_observation_change_changes_context_hash`
  - File: `tests/determinism/test_hash_boundaries.py`
  - Current reason: context reconstruction does not yet ingest Timpo ledgers as runtime inputs
  - Category: Intentional conformance target
  - Needed to pass: include Timpo observation ledger hashes in context reconstruction and context hash boundaries.

## 2. API Shape Not Finalized

No current xfails.

## 3. Fixture Lacks Required Data

No current xfails.

## 6. Test Too Vague And Should Be Rewritten

No current xfails.

