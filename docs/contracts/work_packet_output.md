# Work Packet Output Contract

This is the minimal contract implied by the current deterministic `agent-run` output for the SCE vegetation demo. It is not a real dispatch schema and does not call an LLM.

The current work-packet output must separate:

| Section | Current field(s) | Meaning |
|---|---|---|
| input model delta | `path_summary.start`, `path_summary.domain_path`, `path_summary.surface_path` | The model-delta path being translated. |
| customer value interpretation | `path_summary.value_metrics` | Customer value statements derived from the value translation path. |
| operational implication | `proposed_action`, `permission_result`, `because` | The proposed operational action and why it follows. |
| assumptions | `because`, `path_summary.source_observations` | Demo assumptions and source labels used by the path. |
| evidence references | `source_hashes`, `path_summary.source_observations` | Internal hashes and source labels. These do not prove source authority. |
| audit references | `audit_event_hash`, `audit_event`, `path_hash`, `because_trace_hash` | Replayable audit metadata emitted by the deterministic run. |
| profile permissions | `profile_id`, `restricted_actions`, `audit_event.action_result` | Allowed and restricted actions from the selected profile. |

Required current command:

```bash
python -m corus agent-run tests/fixtures/sce_vegetation --profile sce_grid_ops --lens vegetation_ops --json
```

Required current action:

```text
generate_work_packet
```

Trust boundary: this contract documents current demo output only. It does not prove external source authority, customer approval, dispatch permission, or a production work-management schema.
