from __future__ import annotations

from typing import Any


def compute_value(
    profiled_context: dict[str, Any],
    value_contract: dict[str, Any],
    customer_constraints: dict[str, Any],
) -> dict[str, Any]:
    props = profiled_context["surface_context"]["props"]
    constraints = customer_constraints["constraints"]

    added_watch_items = props["added_watch_items"]
    crew_size = constraints["crew_size"]
    inspection_hours_per_item = constraints["inspection_hours_per_item"]
    items_per_crew_day = constraints["items_per_crew_day"]
    loaded_labor_rate = constraints["loaded_labor_rate"]
    truck_roll_cost_per_day = constraints["truck_roll_cost_per_day"]
    contractor_markup = constraints["contractor_markup"]

    total_inspection_hours = added_watch_items * inspection_hours_per_item
    total_person_hours = total_inspection_hours * crew_size
    crew_days_required = added_watch_items / items_per_crew_day
    labor_cost = total_person_hours * loaded_labor_rate
    truck_roll_cost_total = crew_days_required * truck_roll_cost_per_day
    contractor_markup_cost = labor_cost * contractor_markup
    total_validation_exposure = labor_cost + truck_roll_cost_total + contractor_markup_cost

    def clean_number(value: float) -> float | int:
        return int(value) if float(value).is_integer() else value

    outputs = {
        "total_inspection_hours": clean_number(total_inspection_hours),
        "total_person_hours": clean_number(total_person_hours),
        "crew_days_required": clean_number(crew_days_required),
        "labor_cost": clean_number(labor_cost),
        "truck_roll_cost_total": clean_number(truck_roll_cost_total),
        "contractor_markup_cost": clean_number(contractor_markup_cost),
        "total_validation_exposure": clean_number(total_validation_exposure),
    }
    return {
        "output": "value_result",
        "version": "1.0.0",
        "customer": value_contract["customer"],
        "value_question": value_contract["value_question"],
        "value_outputs": outputs,
        "formula_trace": {
            "total_inspection_hours": "added_watch_items * inspection_hours_per_item",
            "total_person_hours": "total_inspection_hours * crew_size",
            "crew_days_required": "added_watch_items / items_per_crew_day",
            "labor_cost": "total_person_hours * loaded_labor_rate",
            "truck_roll_cost_total": "crew_days_required * truck_roll_cost_per_day",
            "contractor_markup_cost": "labor_cost * contractor_markup",
            "total_validation_exposure": "labor_cost + truck_roll_cost_total + contractor_markup_cost",
        },
    }
