# Corus Workbench

Corus is a local context OS.

```txt
timpo/   anchors observations and is Mojo-first.
kernel/  executes programs and processes.
fs/      preserves protocols, programs, processes, evidence, inputs, and ledgers.
```

Timpo is the primitive observation layer below the kernel/filesystem split.

```txt
Timpo = when + where
Timpo + Domain = Context
```

Kernel acts. FS preserves.

## Architecture

Process = FP.
Program = OS.
Protocol = immutable contract.

Processes are functional. Programs are operational. Protocols are immutable.

The kernel can:
- transform
- run
- connect
- verify
- command

The filesystem preserves:
- protocols
- programs
- processes
- evidence
- inputs
- ledgers

Timpo anchors observation.
Domain reconstructs meaning.
Context is reconstructed significance.
Surface exposes context.
Profile assigns attention.
Value defines why the customer cares.
Legacy preserves reconstruction capability through time.

```txt
Context + Surface = Interface candidate.
Interface candidate + Profile = Rendered experience.
Rendered experience + Value = Customer significance.
```

## Contracts

The extension names the contract. YAML carries the contract.

`.domain` = meaning contract.
`.surface` = context display contract.
`.profile` = attention/rendering/governance contract.
`.value` = customer value contract.
`.program` = reusable workflow contract.
`.process` = reusable step contract.
`.timpos` = input collection of Timpo observations.
`.ledger` = append-only retained Timpo observation history.

A recorded `.process/` directory under `fs/03_processes/runs/` means the program did run and was recorded.

## SCE Demo

The first runnable program is:

```txt
fs/02_programs/sce-vegetation-workforce.program
```

It converts:

```txt
Neara-style vegetation model output
+
SCE workforce/labor/money customer constraints
-> Corus .value
-> computed workforce/labor/money value result
-> recorded process run
```

Neara brings what changed in the network.
SCE brings what matters operationally.
Corus generates `.value`.

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
corus fs mount
corus protocol validate
corus program list
corus program run sce-vegetation-workforce
corus process inspect latest
```

Everything in the repo supports this:

```txt
Corus preserves the discernment required to reconstruct context from observations.
```
