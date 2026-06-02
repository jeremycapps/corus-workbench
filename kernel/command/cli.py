from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from kernel.engine.runtime import resolve_context
from kernel.run.mount_fs import mount_fs, project_root
from kernel.run.run_program import run_program
from kernel.verify.hash import read_yaml
from kernel.verify.validate import validate_document

app = typer.Typer(help="Corus local context OS.")
fs_app = typer.Typer(help="Mount and inspect the Corus filesystem.")
protocol_app = typer.Typer(help="Validate protocols and semantic contracts.")
program_app = typer.Typer(help="List and run Corus programs.")
process_app = typer.Typer(help="List and inspect Corus processes.")
engine_app = typer.Typer(help="Resolve deterministic Corus context.")

app.add_typer(fs_app, name="fs")
app.add_typer(protocol_app, name="protocol")
app.add_typer(program_app, name="program")
app.add_typer(process_app, name="process")
app.add_typer(engine_app, name="engine")

console = Console()


@fs_app.command("mount")
def fs_mount() -> None:
    root = project_root()
    fs_path = mount_fs(root)
    console.print(f"[green]Mounted Corus fs at {fs_path}[/green]")


@protocol_app.command("validate")
def protocol_validate() -> None:
    root = project_root()
    mount_fs(root)
    errors: list[str] = []
    for path in sorted((root / "fs").rglob("*")):
        if not path.is_file() or path.name == ".gitkeep":
            continue
        if path.suffix in {
            ".domain",
            ".surface",
            ".profile",
            ".lens",
            ".value",
            ".program",
            ".process",
            ".input",
            ".source",
            ".protocol",
            ".timpos",
            ".ledger",
        }:
            data = read_yaml(path)
            errors.extend(validate_document(path, data))
    if errors:
        for error in errors:
            console.print(f"[red]{error}[/red]")
        raise typer.Exit(1)
    console.print("[green]Protocols and semantic contracts are valid.[/green]")


@program_app.command("list")
def program_list() -> None:
    root = project_root()
    table = Table(title="Corus Programs")
    table.add_column("Program")
    table.add_column("Version")
    table.add_column("Path")
    for path in sorted((root / "fs" / "02_programs").glob("*.program")):
        program = read_yaml(path)
        table.add_row(program.get("program", path.stem), str(program.get("version", "")), str(path.relative_to(root)))
    console.print(table)


@program_app.command("run")
def program_run(program_name: str) -> None:
    root = project_root()
    mount_fs(root)
    value_result, run_dir = run_program(root, program_name)
    outputs = value_result["value_outputs"]
    table = Table(title=f"Program Run: {program_name}")
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    for key in [
        "total_inspection_hours",
        "total_person_hours",
        "crew_days_required",
        "labor_cost",
        "truck_roll_cost_total",
        "contractor_markup_cost",
        "total_validation_exposure",
    ]:
        table.add_row(key, str(outputs[key]))
    console.print(table)
    console.print(f"[green]Recorded process run: {run_dir.relative_to(root)}[/green]")


@process_app.command("list")
def process_list() -> None:
    root = project_root()
    table = Table(title="Corus Processes")
    table.add_column("Process")
    table.add_column("Paradigm")
    table.add_column("Path")
    for path in sorted((root / "fs" / "03_processes" / "library").glob("*.process")):
        process = read_yaml(path)
        table.add_row(process.get("process", path.stem), process.get("paradigm", ""), str(path.relative_to(root)))
    console.print(table)


@process_app.command("inspect")
def process_inspect(which: str) -> None:
    if which != "latest":
        raise typer.BadParameter("Only 'latest' is supported in phase one.")
    root = project_root()
    runs_dir = root / "fs" / "03_processes" / "runs"
    run_dirs = sorted([path for path in runs_dir.glob("*.process") if path.is_dir() and not path.name.startswith("legacy-")])
    if not run_dirs:
        run_dirs = sorted([path for path in runs_dir.glob("*.process") if path.is_dir()])
    if not run_dirs:
        console.print("[yellow]No recorded process runs found.[/yellow]")
        return
    latest = run_dirs[-1]
    manifest = read_yaml(latest / "manifest.process")
    outputs = read_yaml(latest / "outputs.output")
    console.print(f"[bold]Latest run:[/bold] {latest.relative_to(root)}")
    console.print(f"Program: {manifest.get('program')}")
    console.print(f"Status: {manifest.get('status')}")
    value_result = outputs.get("data", {}).get("value_result")
    if value_result:
        console.print(value_result["value_outputs"])
    else:
        console.print("[yellow]No computed value_result is available for this preserved run.[/yellow]")


@engine_app.command("resolve-cody")
def engine_resolve_cody() -> None:
    root = project_root()
    fixture = root / "kernel" / "fixtures" / "neara_sce"
    result = resolve_context(
        profile_path=fixture / "cody_yakimoff.profile",
        surface_path=fixture / "sce_value_translation.surface",
        domain_path=fixture / "sce.domain",
        lens_paths=[fixture / "model_delta_to_product_pattern.lens"],
        value_path=fixture / "sce_customer_value.value",
    )
    console.print(f"[bold]Question:[/bold] {result['core_question']}")
    console.print(f"[bold]Replay hash:[/bold] {result['replay_hash']}")
    console.print(f"[bold]First-order context:[/bold] {', '.join(result['first_order_context']['node_ids'])}")
    if result["value_resolution"]:
        console.print(f"[bold]Value:[/bold] {result['value_resolution']['narrative']}")
        console.print(f"[bold]Action:[/bold] {result['action_recommendation']}")


if __name__ == "__main__":
    app()
