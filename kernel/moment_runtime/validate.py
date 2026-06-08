from __future__ import annotations

from kernel.moment_runtime.model import (
    ALLOWED_ARTIFACT_STATES,
    ALLOWED_ORIENTATION_PREFIXES,
    ALLOWED_PROFILE_TYPES,
    MOMENT_KEYS,
    MomentRuntimeBundle,
)


class MomentRuntimeValidationError(ValueError):
    pass


def validate_moment_runtime(bundle: MomentRuntimeBundle) -> None:
    source_ids = {source.id for source in bundle.sources}
    profile_ids = {profile.id for profile in bundle.profiles}
    role_ids = {role.id for role in bundle.roles}
    team_ids = {team.id for team in bundle.teams}
    contract_ids = {contract.id for contract in bundle.contracts}
    artifact_ids = {artifact.id for artifact in bundle.artifacts}
    commit_ids = {commit.id for commit in bundle.commits}
    moment_ids = {moment.id for moment in bundle.moments}
    state_ids = {rule.id for rule in bundle.state_rules}
    subject_ids = source_ids | contract_ids | artifact_ids | commit_ids | state_ids | team_ids | role_ids

    for profile in bundle.profiles:
        if profile.type not in ALLOWED_PROFILE_TYPES:
            raise MomentRuntimeValidationError(f"profile {profile.id} has invalid type {profile.type}")
        if profile.type == "role" and profile.role not in role_ids:
            raise MomentRuntimeValidationError(f"profile {profile.id} references missing role {profile.role}")
        if profile.type == "team" and profile.team not in team_ids:
            raise MomentRuntimeValidationError(f"profile {profile.id} references missing team {profile.team}")
        if profile.type == "system" and not profile.system:
            raise MomentRuntimeValidationError(f"profile {profile.id} missing system")

    for team in bundle.teams:
        for role_id in team.roles:
            if role_id not in role_ids:
                raise MomentRuntimeValidationError(f"team {team.id} references missing role {role_id}")

    for contract in bundle.contracts:
        if contract.owner not in role_ids:
            raise MomentRuntimeValidationError(f"contract {contract.id} references missing owner {contract.owner}")
        if contract.artifact not in artifact_ids:
            raise MomentRuntimeValidationError(f"contract {contract.id} references missing artifact {contract.artifact}")
        if isinstance(contract.artifact, list):
            raise MomentRuntimeValidationError(f"contract {contract.id} must reference exactly one artifact")
        for source_id in contract.derived_from:
            if source_id not in source_ids:
                raise MomentRuntimeValidationError(f"contract {contract.id} references missing source {source_id}")

    for artifact in bundle.artifacts:
        if artifact.current_state not in ALLOWED_ARTIFACT_STATES:
            raise MomentRuntimeValidationError(f"artifact {artifact.id} has invalid state {artifact.current_state}")
        if artifact.latest_commit and artifact.latest_commit not in commit_ids:
            raise MomentRuntimeValidationError(f"artifact {artifact.id} references missing latest_commit {artifact.latest_commit}")

    for commit in bundle.commits:
        if commit.target not in artifact_ids:
            raise MomentRuntimeValidationError(f"commit {commit.id} references missing artifact {commit.target}")
        if commit.author not in profile_ids:
            raise MomentRuntimeValidationError(f"commit {commit.id} references missing author {commit.author}")
        if commit.from_state not in ALLOWED_ARTIFACT_STATES or commit.to_state not in ALLOWED_ARTIFACT_STATES:
            raise MomentRuntimeValidationError(f"commit {commit.id} has invalid artifact state transition")
        if commit.previous and commit.previous not in commit_ids:
            raise MomentRuntimeValidationError(f"commit {commit.id} references missing previous commit {commit.previous}")

    for moment in bundle.moments:
        if set(moment.__dict__) != MOMENT_KEYS:
            raise MomentRuntimeValidationError(f"moment {moment.id} is not minimal")
        if moment.initiator not in profile_ids:
            raise MomentRuntimeValidationError(f"moment {moment.id} references missing initiator {moment.initiator}")
        if not moment.orientation.startswith(ALLOWED_ORIENTATION_PREFIXES):
            raise MomentRuntimeValidationError(f"moment {moment.id} has invalid orientation {moment.orientation}")
        if moment.orientation.startswith("contract.") and moment.orientation not in contract_ids:
            raise MomentRuntimeValidationError(f"moment {moment.id} references missing contract {moment.orientation}")
        if moment.subject not in subject_ids:
            raise MomentRuntimeValidationError(f"moment {moment.id} references missing subject {moment.subject}")
        for previous_id in _previous_ids(moment.previous):
            if previous_id not in moment_ids:
                raise MomentRuntimeValidationError(f"moment {moment.id} references missing previous moment {previous_id}")

    for rule in bundle.state_rules:
        for artifact_id in rule.requires:
            if artifact_id not in artifact_ids:
                raise MomentRuntimeValidationError(f"state {rule.id} references missing artifact {artifact_id}")


def _previous_ids(previous: str | list[str] | None) -> list[str]:
    if previous is None:
        return []
    if isinstance(previous, list):
        return previous
    return [previous]
