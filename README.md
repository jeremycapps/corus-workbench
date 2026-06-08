# Corus Workbench

Corus is a context orchestration engine.

Artifacts have commit histories. Contexts have moment histories.

```txt
Commit = artifact history
Moment = context history
Context = derived from linked moments
```

Corus helps an orchestrator understand which contracts are in scope, which artifacts are expected, what has changed, and whether the context is ready, blocked, or unresolved.

## Core Model

A contract has one owner, one focus, one artifact, and one state.

A commit records a durable state change to an artifact.

A moment records how a subject enters context through an initiator's orientation.

```txt
Orchestrator
  -> derived Context
    -> Contracts
      -> Artifact + State
        -> Commits
          -> Moments
```

The smallest atom of context is a moment:

```txt
Moment = timpo + initiator + orientation + subject + previous
```

The engine keeps these boundaries:

- `Artifact`: durable proof/output object expected by a contract.
- `Commit`: durable state change to an artifact.
- `Moment`: contextual occurrence linked to prior moment(s).
- `Context`: derived chain/graph of moments around an orchestrated subject.
- `Contract`: measurable unit of responsibility.
- `Profile`: initiator that orients a moment.

## Neara V0 Demo

The Neara v0 fixture shows RVO entering a Director-orchestrated account context. CVA and FDE contracts become visible inside that context, expected artifacts are identified, and alignment remains unresolved until those artifacts exist.

Run:

```bash
python -m corus moment tests/fixtures/neara_moment_v0
```

The default fixture has no commits, so it proves:

```txt
RVO enters a Director-orchestrated account context.
CVA and FDE role contracts are visible.
Each contract has one artifact.
Expected artifacts are missing.
Neara alignment is unresolved.
Customer adoption is unresolved.
```

If commits later set the required artifacts to `present`, Corus can resolve the corresponding state.

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python -m corus moment tests/fixtures/neara_moment_v0
```

## Keeper

Commits are artifact history. Moments are context history. Context is derived from linked moments.
