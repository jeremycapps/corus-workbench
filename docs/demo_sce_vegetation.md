# SCE Vegetation Demo

## What this demo proves

- Payloads enter a Timpo-anchored ledger.
- Candidate claims are interpreted.
- Candidate claims are validated or rejected.
- READ includes only admissible claims.
- AUDIT proves included and excluded claims.
- AUDIT proves a generated output is allowed by profile.sce_grid_ops.

## Commands

```bash
python -m corus ingest bundles/sce_vegetation --out runs/sce_vegetation

python -m corus read runs/sce_vegetation --profile sce_grid_ops --lens vegetation_ops

python -m corus audit runs/sce_vegetation --target claim.sce.watch_points_added

python -m corus audit runs/sce_vegetation --target claim.sce.unsupported_cost_assumption

python -m corus audit runs/sce_vegetation --target output.sce_grid_ops.work_packet
```

## Expected story

The drop-in bundle is the Corus wrapper around Neara model/run outputs, not the Neara export itself.

The same ledger contains both accepted and rejected claims.

The accepted claim enters active context.

The rejected claim remains historical provenance but does not enter active context.

The generated output is allowed because profile.sce_grid_ops permits generate_work_packet and restricts dispatch_crew.

The READ output is organized as Architecture, Read Context, Ledger, Admission Trail, Included Claims, Excluded Claims, Declared Contracts, Outputs, Invariant, and Read projection hash.

The Admission Trail shows the WRITE-side events that made the READ projection possible.

Neara output becomes provenance. Manifest claims become candidate claims. Validations make claims admissible or rejected.

## What is intentionally not implemented yet

- AUDIT-006 detailed projection diff
- AUDIT-007B object-level payload path resolution
- source authority policy
- claim weighting
- PDF interpretation
- DuckDB index
