# Corus Engine Playground

Run the local interactive playground from the repository root:

```bash
python -m corus validate tests/fixtures/sce_vegetation
python -m corus reconstruct tests/fixtures/sce_vegetation
python -m corus project tests/fixtures/sce_vegetation --profile sce_grid_ops --lens vegetation_ops
python -m corus explain tests/fixtures/sce_vegetation
python -m corus diff tests/fixtures/neara_policy_delta
python -m corus read tests/fixtures/sce_vegetation --profile sce_grid_ops --lens vegetation_ops
python -m corus audit tests/fixtures/sce_vegetation --target claim.sce.watch_points_added
python -m corus audit tests/fixtures/sce_vegetation --target claim.sce.unsupported_cost_assumption
python -m corus agent-run tests/fixtures/sce_vegetation --profile sce_grid_ops --lens vegetation_ops
python -m corus agent-run tests/fixtures/sce_vegetation --profile neara_value_architect --lens vegetation_ops
```

Every command also supports JSON output:

```bash
python -m corus explain tests/fixtures/sce_vegetation --json
```

The playground is a thin wrapper over the current file-backed engine runtime.
The ledger-first demo follows: Timpos anchors. The ledger preserves. Admission
writes. Corus reads. Audit proves.

`read` verifies the ledger chain, resolves payload admission, includes
validated candidate claims in active context, and excludes rejected or
unvalidated candidates. `audit` explains why a target claim or output is
included or excluded and emits a replay proof hash.

`agent-run` uses a compatibility adapter because a separate agent runtime API
does not exist yet; it reports the profiled action recommendation, permission
status, graph path, because trace, and an audit-event hash derived from those
inputs.
When a fixture has multiple profiles, pass `--profile` to `agent-run` so the
action and permission boundary come from the selected profile.
