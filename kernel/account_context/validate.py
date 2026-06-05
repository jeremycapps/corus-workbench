from __future__ import annotations

from kernel.account_context.model import AccountContextBundle


class AccountContextValidationError(ValueError):
    pass


def validate_account_context(bundle: AccountContextBundle) -> None:
    sources = {source.id for source in bundle.sources}
    roles = {role.id: role for role in bundle.roles}
    teams = {bundle.team.id}
    contexts = {bundle.context.id}
    surfaces = {bundle.surface.id}
    relations = {relation.id: relation for relation in bundle.relations}
    artifacts = {artifact.id: artifact for artifact in bundle.artifacts}

    for role_id in bundle.team.contains:
        if role_id not in roles:
            raise AccountContextValidationError(f"team {bundle.team.id} contains missing role {role_id}")

    for role in bundle.roles:
        if role.team != bundle.team.id:
            raise AccountContextValidationError(f"role {role.id} belongs to missing team {role.team}")
        _validate_sources(role.id, role.source_basis, sources)

    if bundle.surface.owner not in roles:
        raise AccountContextValidationError(f"surface {bundle.surface.id} owner {bundle.surface.owner} does not exist")
    if bundle.surface.boundary not in teams:
        raise AccountContextValidationError(f"surface {bundle.surface.id} boundary team {bundle.surface.boundary} does not exist")
    if bundle.surface.context not in contexts:
        raise AccountContextValidationError(f"surface {bundle.surface.id} context {bundle.surface.context} does not exist")

    _validate_sources(bundle.context.id, bundle.context.source_basis, sources)

    for relation in bundle.relations:
        if relation.from_role not in roles:
            raise AccountContextValidationError(f"relation {relation.id} from_role {relation.from_role} does not exist")
        if relation.to_surface not in surfaces:
            raise AccountContextValidationError(f"relation {relation.id} to_surface {relation.to_surface} does not exist")
        for artifact_id in relation.produces:
            if artifact_id not in artifacts:
                raise AccountContextValidationError(f"relation {relation.id} produces missing artifact {artifact_id}")
        _validate_sources(relation.id, relation.source_basis, sources)

    for artifact in bundle.artifacts:
        if artifact.produced_by not in relations and artifact.produced_by not in surfaces:
            raise AccountContextValidationError(
                f"artifact {artifact.id} produced_by {artifact.produced_by} does not exist as relation or surface"
            )


def _validate_sources(owner_id: str, source_basis: list[str], known_sources: set[str]) -> None:
    for source_id in source_basis:
        if source_id not in known_sources:
            raise AccountContextValidationError(f"{owner_id} source_basis references missing source {source_id}")
