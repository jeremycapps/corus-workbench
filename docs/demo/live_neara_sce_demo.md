# Live Neara / SCE Demo Surface

This page is a CVA decision summary: model output in, customer decision out, with stakeholder-specific views and proof available through progressive disclosure.

Primary user: Neara Customer Value Architect, Customer Success lead, or implementation reviewer who needs to understand how Corus translates a Neara-style model output into customer-specific value, governed action, and audit evidence.

Primary question:

```text
Can this technical model output become a defensible customer decision?
```

Primary UI hierarchy:

1. Decision outcome
2. Model input
3. Customer value output
4. Action options
5. Stakeholder views
6. Decision confidence
7. Technical proof behind disclosure

Trust/status framing shown on the page:

```text
Proof-of-work demo: synthetic Neara-style input, internally hash-backed, not an official Neara or SCE export.
```

Run a local one-page web demo:

```bash
python -m corus.demo_surface --serve --port 8765
```

Then open:

```text
http://127.0.0.1:8765/
```

Generate a static HTML file:

```bash
python -m corus.demo_surface --out docs/demo/neara_sce_value_translation_demo.html
```

The page wraps existing Corus JSON commands. It does not refactor the engine, introduce a database, call external services, or replace Neara's physical modeling pipeline.

Run the focused demo tests:

```bash
.venv/bin/python -m pytest tests/test_demo_surface.py
```

Run the targeted demo/playground checks:

```bash
.venv/bin/python -m pytest tests/test_demo_surface.py tests/test_neara_demo_boundary.py tests/test_playground_cli.py
```

## Sendable Demo Checklist

- Page loads locally.
- Decision summary visible.
- Outcome metrics visible.
- Action options visible.
- Stakeholder views visible.
- Trust boundary visible.
- 72 watch points visible.
- Admitted/rejected claims visible.
- Audit/proof hashes visible.
- Out-of-scope section visible.
