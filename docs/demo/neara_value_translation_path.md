# Neara Value Translation Path

Product framing: Neara tells utilities what changed in the network. Corus tells each customer why that change matters.

For the Neara demo, Corus is a value translation layer. Corus does not recreate Neara's physical modeling pipeline. Neara handles physical network reconstruction, LiDAR/GIS processing, clearance modeling, and vegetation detection.

Corus starts from a clean Neara-style model output or model delta. The demo translates that model delta into customer-specific value, action, and why:

```text
Neara model output / model delta
  -> Corus intake wrapper
  -> .domain meaning nodes
  -> .surface operational graph
  -> .lens / .profile role-specific attention and permissions
  -> .value customer value definitions
  -> .evidence source-backed or synthetic assumptions
  -> READ reconstruction
  -> because trace
  -> AUDIT proof
  -> value story / work packet
```

Raw GeoJSON, PDF, ArcGIS, LiDAR, and connector modules are supporting provenance or future-upstream work. They are not the main Neara demo path.

The `.domain`, `.surface`, `.lens`, `.profile`, `.value`, and `.evidence` files are value-translation contracts. They define how a Neara-style model delta becomes customer-specific meaning, operational attention, permissions, value, and assumptions.

Ledger and audit currently prove internal admission, replay checks, payload hashes, ledger continuity, profile permissions, and READ inclusion/exclusion. Ledger and audit do not yet prove external truth or source authority.

| Layer | Demo role | Current file(s) | Trust status |
|---|---|---|---|
| Neara-style model output | Provides the clean model delta/watch point input. | `bundles/sce_vegetation/artifacts/demo_model_output.json` | `demo-synthetic`, `source-authority-missing` |
| Corus intake wrapper | Declares source, claims, validations, contracts, and generated demo output. | `bundles/sce_vegetation/corus.bundle.yaml` | `internally-hash-backed`, `demo-synthetic` |
| `.domain` | Names SCE and Neara meaning nodes used in translation. | `tests/fixtures/sce_vegetation/sce.domain` | `demo-synthetic` |
| `.surface` | Connects model delta, policy, watch points, risk, operations, cost, customer value, and product pattern. | `tests/fixtures/sce_vegetation/sce.surface` | `demo-synthetic`, `source-labeled` |
| `.lens` | Selects role-specific attention over the surface graph. | `tests/fixtures/sce_vegetation/vegetation_ops.lens` | `demo-synthetic`, `deterministic-code-backed` |
| `.profile` | Defines core questions, allowed actions, and restricted actions. | `tests/fixtures/sce_vegetation/sce_grid_ops.profile`, `tests/fixtures/sce_vegetation/neara_value_architect.profile` | `demo-synthetic`, `deterministic-code-backed` |
| `.value` | Defines customer value criteria and value story inputs. | `tests/fixtures/sce_vegetation/sce_customer.value` | `demo-synthetic`, `source-authority-missing` |
| `.evidence` | Holds operational claims and source labels used by explain. | `tests/fixtures/sce_vegetation/sce.evidence` | `source-labeled`, `demo-synthetic`, `source-authority-missing` |
| Timpo observations | Anchors demo observations in time/place. | `tests/fixtures/sce_vegetation/observations.timpos` | `demo-synthetic`, `internally-hash-backed` |
| Ledger | Stores interpreted claims, validations, output, and hashes. | `tests/fixtures/sce_vegetation/ledger` | `internally-hash-backed` |
| READ reconstruction | Reconstructs active claim context from ledger state. | `kernel/ledger/read.py` | `deterministic-code-backed` |
| Because trace | Explains architectural and operational lineage. | `corus/playground.py`, `kernel/engine/runtime.py` | `deterministic-code-backed`, `source-labeled` |
| AUDIT proof | Proves ledger continuity, payload hashes, admissibility, replay status, and profile permissions. | `kernel/audit/*` | `internally-hash-backed`, `deterministic-code-backed`, `source-authority-missing` |
| Work packet action | Deterministically proposes an allowed action from profile permissions. | `python -m corus agent-run ... --profile sce_grid_ops` | `deterministic-code-backed`, `demo-synthetic` |

## Not Implemented Yet

- Source authority verifier
- Object-level audit for domain/surface/profile/value elements
- Detailed replay diff engine
- Real Neara export contract
- Real customer-approved `.value` file
- Real work-packet output schema
