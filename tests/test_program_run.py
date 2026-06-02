from pathlib import Path

from kernel.run.run_program import run_program


def test_sce_program_computes_value_outputs() -> None:
    root = Path(__file__).resolve().parents[1]
    value_result, run_dir = run_program(root, "sce-vegetation-workforce")

    assert run_dir.exists()
    assert (run_dir / "manifest.process").exists()
    assert (run_dir / "inputs.input").exists()
    assert (run_dir / "outputs.output").exists()
    assert (run_dir / "hashes.hash").exists()
    assert (run_dir / "logs.txt").exists()
    assert value_result["value_outputs"] == {
        "total_inspection_hours": 108,
        "total_person_hours": 216,
        "crew_days_required": 9,
        "labor_cost": 18360,
        "truck_roll_cost_total": 4050,
        "contractor_markup_cost": 2754,
        "total_validation_exposure": 25164,
    }
    outputs = (run_dir / "outputs.output").read_text(encoding="utf-8")
    inputs = (run_dir / "inputs.input").read_text(encoding="utf-8")
    assert "count: 2" in outputs
    assert "vegetation-observations.timpos" in inputs
