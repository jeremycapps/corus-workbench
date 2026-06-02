# Neara to Corus Intake Bundle

The drop-in bundle is not the Neara export itself.

Neara exports model or scenario outputs. Corus wraps those outputs in an intake bundle that can be written to a provenance ledger, read through a profile/lens, and audited.

## Core Distinction

Do not say:

```txt
Neara export becomes truth.
```

Say:

```txt
Neara export becomes provenance.
```

Then:

```txt
manifest claims become candidate claims
validations make claims admissible or rejected
READ uses only admissible claims
AUDIT proves why claims and outputs were included, excluded, or allowed
```

## Bundle Shape

```txt
sce_vegetation_bundle/
  corus.bundle.yaml

  artifacts/
    neara_model_delta.csv
    neara_run_metadata.json
    neara_watch_points.geojson
    sce_customer_inputs.csv
    sce_public_source.pdf

  contracts/
    sce.domain
    sce.surface
    vegetation_ops.lens
    sce_grid_ops.profile
    neara_value_architect.profile
    sce_customer.value
```

The most important file is `corus.bundle.yaml`. The manifest tells Corus what each dropped-in artifact means.

## Ideal Neara Export

For this demo, Corus does not need Neara's full digital twin. Corus needs a model delta export.

Minimum useful package:

- run metadata JSON
- model delta CSV/table
- geospatial result layer as GeoJSON, CSV with coordinates, shapefile, or GeoPackage
- optional PDF/report snapshot

Example run metadata:

```json
{
  "run_id": "neara_sce_veg_001",
  "customer": "SCE",
  "scenario": "vegetation_clearance_policy_delta",
  "policy_before": "3m",
  "policy_after": "5m",
  "model_version": "unknown",
  "exported_at": "2026-06-01T00:00:00Z"
}
```

Example model delta row:

```csv
result_id,asset_id,result_type,value,unit,policy_delta,risk_tier
wp_001,span_001,watch_point_added,1,watch_point,3m_to_5m,moderate
```

The PDF, if present, is treated as an artifact, not truth.

## Manifest Mapping

Dropped files become `add` payloads:

```yaml
sources:
  - id: source.neara_model_delta
    file: artifacts/neara_model_delta.csv
    kind: model_delta
  - id: source.neara_watch_points
    file: artifacts/neara_watch_points.geojson
    kind: geospatial_result
  - id: source.neara_run_metadata
    file: artifacts/neara_run_metadata.json
    kind: run_metadata
```

Candidate claims come from explicit manifest entries:

```yaml
claims:
  - id: claim.sce.watch_points_added
    source: source.neara_model_delta
    claim: The Neara model delta produced 72 vegetation watch points.
    value: 72
    unit: watch_points
    candidate_for:
      - domain.sce.vegetation_watch_points
```

Validation decides whether a candidate claim enters active context:

```yaml
validations:
  - target: claim.sce.watch_points_added
    admissible: true
    reason: admissible true
```

Contracts define how admitted claims are read:

```yaml
contracts:
  - id: domain.sce_vegetation
    kind: domain
    ref: contracts/sce.domain
  - id: surface.sce_vegetation
    kind: surface
    ref: contracts/sce.surface
  - id: lens.vegetation_ops
    kind: lens
    ref: contracts/vegetation_ops.lens
  - id: profile.sce_grid_ops
    kind: profile
    ref: contracts/sce_grid_ops.profile
  - id: profile.neara_value_architect
    kind: profile
    ref: contracts/neara_value_architect.profile
  - id: value.sce_customer
    kind: value
    ref: contracts/sce_customer.value
```

Outputs can be generated as ledger payloads:

```yaml
outputs:
  - id: output.sce_grid_ops.work_packet
    from: corus.agent_run
    inputs:
      - claim.sce.watch_points_added
      - domain.sce_vegetation
      - surface.sce_vegetation
      - profile.sce_grid_ops
      - value.sce_customer
    data:
      proposed_action: generate_work_packet
      permission_result: allowed
      note: Generated output fixture for output target audit resolution.
```

## Neara-Facing Ask

Can you export a scenario result as a flat model-delta package?

Minimum:

- run metadata JSON
- result table CSV
- geospatial result layer as GeoJSON, CSV with coordinates, shapefile, or GeoPackage
- optional PDF/report snapshot

Corus does not need the full digital twin. Corus needs the model output and enough identifiers/provenance to translate the delta into customer value and audit proof.

## Demo Framing

Neara says:

```txt
72 watch points were produced by this model/scenario.
```

Corus says:

```txt
That output was admitted from this source,
interpreted as this candidate claim,
validated for this context,
read through this profile/lens,
converted into this work packet,
and audited as allowed by profile.sce_grid_ops.
```

## System Loop

```txt
WRITE:
  artifacts, claims, validations, contracts, and outputs enter the ledger as payloads

READ:
  admissible claims become active context through domain/surface/lens/profile/value

AUDIT:
  claims and outputs are proven against ledger integrity, payload integrity, admissibility, replay, and profile permissions
```

Dropping in files does not create truth. Dropping in files creates provenance. Claims become active only through interpretation and validation.
