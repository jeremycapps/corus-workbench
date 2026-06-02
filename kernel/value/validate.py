from __future__ import annotations

from kernel.value.model import ValueSpec


class ValueValidationError(ValueError):
    pass


def validate_value(value: ValueSpec, strict: bool = True) -> list[str]:
    warnings: list[str] = []
    if not value.id:
        raise ValueValidationError("value must have an id")
    if not value.stakeholders:
        message = f"value {value.id} must define stakeholders"
        if strict:
            raise ValueValidationError(message)
        warnings.append(message)
    if not value.success_criteria:
        raise ValueValidationError(f"value {value.id} must define success criteria")
    if not value.why_relation:
        raise ValueValidationError(f"value {value.id} must define why_relation")
    if value.required_metrics:
        available_text = " ".join(
            [
                *value.success_criteria,
                value.business_consequence,
                value.risk_opportunity,
                value.why_relation,
                value.action_trigger,
                value.narrative,
            ]
        )
        missing = [metric for metric in value.required_metrics if metric not in available_text]
        if missing:
            raise ValueValidationError(f"value {value.id} references unknown metric {missing[0]}")
    return warnings
