import functools
from importlib import resources

from pkgs.argument_parser import CachedParser
from uncountable.core import environment
from uncountable.types import integration_server_t, job_definition_t

profile_parser = CachedParser(job_definition_t.ProfileDefinition)

_DEFAULT_PROFILE_ENV = integration_server_t.IntegrationEnvironment.PROD
_IGNORED_PROFILE_FOLDERS = ["__pycache__"]


@functools.cache
def load_profiles() -> list[job_definition_t.ProfileMetadata]:
    profiles_module = environment.get_profiles_module()
    integration_envs = environment.get_integration_envs()
    profiles = [
        entry
        for entry in resources.files(profiles_module).iterdir()
        if entry.is_dir() and entry.name not in _IGNORED_PROFILE_FOLDERS
    ]
    profile_details: list[job_definition_t.ProfileMetadata] = []
    seen_job_ids: set[str] = set()
    for profile_file in profiles:
        profile_name = profile_file.name
        try:
            definition = profile_parser.parse_yaml_resource(
                package=f"{profiles_module}.{profile_name}",
                resource="profile.yaml",
            )
            for job in definition.jobs:
                if job.id in seen_job_ids:
                    raise Exception(f"multiple jobs with id {job.id}")
                seen_job_ids.add(job.id)

            if definition.environments is not None:
                for integration_env in integration_envs:
                    environment_config = definition.environments.get(integration_env)
                    if environment_config is not None:
                        profile_details.append(
                            job_definition_t.ProfileMetadata(
                                name=profile_name,
                                jobs=definition.jobs,
                                base_url=environment_config.base_url,
                                auth_retrieval=environment_config.auth_retrieval,
                                client_options=environment_config.client_options,
                            )
                        )
            elif _DEFAULT_PROFILE_ENV in integration_envs:
                assert (
                    definition.base_url is not None
                    and definition.auth_retrieval is not None
                ), f"define environments in profile.yaml for {profile_name}"
                profile_details.append(
                    job_definition_t.ProfileMetadata(
                        name=profile_name,
                        jobs=definition.jobs,
                        base_url=definition.base_url,
                        auth_retrieval=definition.auth_retrieval,
                        client_options=definition.client_options,
                    )
                )
        except FileNotFoundError as e:
            print(f"WARN: profile.yaml not found for {profile_name}", e)
            continue
    return profile_details
