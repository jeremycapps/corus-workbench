from __future__ import annotations

from pathlib import Path
from typing import Any

from kernel.domain.loader import load_domain
from kernel.domain.loader import domain_to_data
from kernel.domain.validate import validate_domain
from kernel.engine.hashing import hash_data
from kernel.engine.replay import build_replay_hash
from kernel.lens.loader import load_lens
from kernel.lens.loader import lens_to_data
from kernel.lens.resolver import resolve_lens
from kernel.lens.validate import validate_lens
from kernel.lens.weighting import apply_lens, weighted_graph_to_data
from kernel.profile.initiate import initiate
from kernel.profile.loader import load_profile
from kernel.profile.loader import profile_to_data
from kernel.profile.model import Profile
from kernel.surface.loader import load_surface
from kernel.surface.loader import surface_to_data
from kernel.surface.validate import validate_surface
from kernel.value.loader import load_value
from kernel.value.loader import value_to_data
from kernel.value.resolve import resolve_value
from kernel.value.validate import validate_value


class RuntimeResolutionError(ValueError):
    pass


def resolve_context(
    *,
    profile_path: Path | None,
    surface_path: Path,
    domain_path: Path,
    lens_paths: list[Path],
    value_path: Path | None = None,
    runtime_input: dict[str, Any] | None = None,
) -> dict[str, Any]:
    profile: Profile | None = load_profile(profile_path) if profile_path else None
    core_question = initiate(profile)
    assert profile is not None

    domain = load_domain(domain_path)
    validate_domain(domain)

    surface = load_surface(surface_path)
    validate_surface(surface, domain)

    lenses = {lens.id: lens for lens in [load_lens(path) for path in lens_paths]}
    lens = resolve_lens(profile, lenses)
    validate_lens(lens, domain)

    weighted_graph = apply_lens(lens, surface, domain)
    weighted_data = weighted_graph_to_data(weighted_graph)

    value_resolution = None
    value = None
    if value_path:
        value = load_value(value_path)
        validate_value(value)
        value_resolution = resolve_value(value, weighted_data)

    profile_hash = hash_data(profile_to_data(profile))
    domain_hash = hash_data(domain_to_data(domain))
    surface_hash = hash_data(surface_to_data(surface))
    lens_hash = hash_data(lens_to_data(lens))
    value_hash = hash_data(value_to_data(value)) if value else None
    context_hash = hash_data(
        {
            "domain_hash": domain_hash,
            "surface_hash": surface_hash,
            "domain_node_ids_used": sorted(surface.nodes),
        }
    )
    projection_hash = hash_data(
        {
            "context_hash": context_hash,
            "lens_hash": lens_hash,
            "weighted_graph": weighted_data,
        }
    )
    profiled_output_hash = hash_data(
        {
            "projection_hash": projection_hash,
            "profile_hash": profile_hash,
            "core_question": core_question,
        }
    )
    value_output_hash = (
        hash_data(
            {
                "profiled_output_hash": profiled_output_hash,
                "value_hash": value_hash,
                "value_resolution": value_resolution,
            }
        )
        if value_resolution
        else None
    )
    source_refs = sorted(
        {
            source_ref
            for node in domain.nodes
            for source_ref in node.source_refs
            if node.id in surface.nodes
        }
    )
    because_trace = {
        "observations": source_refs,
        "domain_nodes": sorted(surface.nodes),
        "surface_edges": [edge["id"] for edge in weighted_data["weighted_edges"]],
        "profile": profile.id,
        "lens": lens.id,
        "value": value.id if value else None,
        "value_metrics": value.success_criteria if value else [],
        "claims": [
            {
                "claim": "context is reconstructed from observations, domain nodes, and surface edges",
                "lineage": ["observations", "domain_nodes", "surface_edges"],
            },
            {
                "claim": "projection is shaped by profile core question and lens weights",
                "lineage": ["profile", "lens", "weighted_node_list", "weighted_edge_list"],
            },
            {
                "claim": "value significance is resolved from projected context and value criteria",
                "lineage": ["value", "value_metrics", "first_order_context"],
            },
        ],
        "hash": hash_data(
            {
                "observations": source_refs,
                "domain_nodes": sorted(surface.nodes),
                "surface_edges": [edge["id"] for edge in weighted_data["weighted_edges"]],
                "profile": profile.id,
                "lens": lens.id,
                "value": value.id if value else None,
            }
        ),
    }

    result_without_hash: dict[str, Any] = {
        "profile_id": profile.id,
        "core_question": core_question,
        "lens_id": lens.id,
        "surface_graph_id": surface.id,
        "domain_node_ids_used": sorted(surface.nodes),
        "weighted_node_list": weighted_data["weighted_nodes"],
        "weighted_edge_list": weighted_data["weighted_edges"],
        "first_order_context": weighted_data["first_order_context"],
        "value_resolution": value_resolution,
        "evidence_summary": {
            "domain_id": domain.id,
            "surface_graph_id": surface.id,
            "source_refs": source_refs,
        },
        "gaps": weighted_data["gaps"],
        "context_gap": weighted_data["gaps"],
        "because_trace": because_trace,
        "layer_hashes": {
            "profile_hash": profile_hash,
            "domain_hash": domain_hash,
            "surface_hash": surface_hash,
            "lens_hash": lens_hash,
            "value_hash": value_hash,
            "context_hash": context_hash,
            "projection_hash": projection_hash,
            "profiled_output_hash": profiled_output_hash,
            "value_output_hash": value_output_hash,
        },
        "action_recommendation": value_resolution["action_recommendation"] if value_resolution else None,
        "runtime_order": ["profile", "core_question", "lens", "surface", "domain", "value"],
        "construction_order": ["domain", "surface", "lens", "profile", "value"],
    }
    replay_hash, replay_metadata = build_replay_hash(
        paths={
            "profile": profile_path,
            "domain": domain_path,
            "surface": surface_path,
            "lens": next(path for path in lens_paths if load_lens(path).id == lens.id),
            "value": value_path,
        },
        runtime_input=runtime_input,
        canonical_weighted_graph=weighted_data,
        result_without_hash=result_without_hash,
    )
    result_without_hash["replay_hash"] = replay_hash
    result_without_hash["replay_metadata"] = replay_metadata
    return result_without_hash
