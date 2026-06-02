# Audit Capability Matrix

## Current status

| Audit component | Status | Current behavior | Gap | Next implementation step |
|---|---|---|---|---|
| Target resolver | implemented for claim, output, ledger entry, and payload targets | Resolves targets into ledger references and exposes records used by audit | Object-level payload paths for domain nodes and surface edges are placeholder-only | TODO[AUDIT-007B]: Add object-level payload paths |
| Ledger verifier | implemented | Recomputes each entry hash and emits per-entry `prev_hash` continuity evidence | Does not yet include richer ledger-field schema diagnostics | Extend verifier with schema evidence if needed |
| Payload verifier | implemented | Resolves each `payload_ref`, recomputes the payload hash, and emits per-entry verification results | Does not yet include richer schema diagnostics beyond hash status | Extend verifier with schema evidence if needed |
| Admissibility resolver | implemented for claim targets | Resolves interpret and latest validate payloads for candidate claims and compares against READ included/excluded state | Does not handle source, contract, output, proof, or supersession admissibility | Extend resolver beyond `candidate_claim` targets |
| Read replay engine | implemented for projection hash comparison | Replays READ independently from the ledger and compares an optional claimed projection hash against the replayed projection hash | Does not yet emit detailed mismatch diffs | TODO[AUDIT-006]: Add projection diff |
| Diff / comparison | placeholder | Returns `not_applicable` when no mismatch exists and `not_implemented` when a mismatch needs explanation | Does not explain projection or output mismatches | TODO[AUDIT-006]: Add projection diff |
| Profile permissions | implemented for generated output targets | Resolves generated output payloads, referenced profile contracts, proposed actions, allowed actions, and restricted actions | Does not yet support multi-step approval workflows or non-output permission targets | Extend to approval workflows later |
| Proof emitter | partial | Emits proof-shaped object and `proof_hash` | Proof can include partial or placeholder checks and will be invalid until required checks pass | Keep validity computed from structured check statuses |

## Validity rule

`valid` is true only when every check status is `pass` or `not_applicable`.
Statuses such as `partial`, `not_implemented`, `not_found`, and `fail` make
the proof invalid even when READ inclusion/exclusion is known.
