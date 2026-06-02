# Intake Bundle

An intake bundle is a drop-in folder that Corus can turn into a ledger-backed run.

The bundle is not the Neara export itself. Neara exports model or scenario outputs; Corus wraps those outputs in an intake bundle. See [Neara to Corus Intake Bundle](neara_corus_intake_bundle.md) for the Neara-facing model.

## What it does

- Adds source artifacts.
- Interprets manifest claims as candidate claims.
- Validates or rejects claims.
- Declares contracts.
- Generates output payloads.
- Produces a runnable Corus fixture/run.

## What it does not do yet

- It does not automatically extract facts from PDFs.
- It does not decide source authority.
- It does not weight evidence.
- It does not use DuckDB.

## Example

```bash
python -m corus ingest bundles/sce_vegetation --out runs/sce_vegetation
python -m corus read runs/sce_vegetation --profile sce_grid_ops --lens vegetation_ops
python -m corus audit runs/sce_vegetation --target claim.sce.watch_points_added
python -m corus audit runs/sce_vegetation --target output.sce_grid_ops.work_packet
```

Dropping in files creates provenance. Claims become active only through interpretation and validation.
