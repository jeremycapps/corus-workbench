from __future__ import annotations

from pathlib import Path
from typing import Any

from kernel.run.bind_inputs import load_bindings
from kernel.run.load_program import load_program
from kernel.run.record_process import record_process
from kernel.transform.apply_domain import apply_domain
from kernel.transform.apply_profile import apply_profile
from kernel.transform.compute_value import compute_value
from kernel.transform.expose_surface import expose_surface
from kernel.verify.hash import read_yaml


def load_process_contracts(root: Path, program: dict[str, Any]) -> list[dict[str, Any]]:
    contracts = []
    for step in program.get("workflow", []):
        path = root / step["process"]
        contract = read_yaml(path)
        contract["_path"] = step["process"]
        contracts.append(contract)
    return contracts


def run_program(root: Path, program_name: str) -> tuple[dict[str, Any], Path]:
    program = load_program(root, program_name)
    bindings = load_bindings(root, program)
    process_contracts = load_process_contracts(root, program)

    model_output = bindings["inputs"]["model_output"]
    customer_constraints = bindings["inputs"]["customer_constraints"]
    timpos = bindings["inputs"].get("timpos")
    domain = bindings["protocols"]["domain"]
    surface = bindings["protocols"]["surface"]
    profile = bindings["protocols"]["profile"]
    value = bindings["protocols"]["value"]

    clearance_context = apply_domain(model_output, domain, timpos)
    surface_context = expose_surface(clearance_context, surface)
    profiled_context = apply_profile(surface_context, profile)
    value_result = compute_value(profiled_context, value, customer_constraints)

    outputs = {
        "clearance_context": clearance_context,
        "surface_context": surface_context,
        "profiled_context": profiled_context,
        "value_result": value_result,
    }
    inputs = {
        "model_output": model_output,
        "customer_constraints": customer_constraints,
        "timpos": timpos,
        "domain": domain,
        "surface": surface,
        "profile": profile,
        "value": value,
    }
    run_dir = record_process(root, program, inputs, outputs, process_contracts)
    return value_result, run_dir
