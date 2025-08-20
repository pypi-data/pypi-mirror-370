import importlib
import inspect
import os

from uncountable.integration.job import Job
from uncountable.types.job_definition_t import JobExecutorScript, ProfileMetadata


def resolve_script_executor(
    executor: JobExecutorScript, profile_metadata: ProfileMetadata
) -> Job:
    job_module_path = ".".join([
        os.environ["UNC_PROFILES_MODULE"],
        profile_metadata.name,
        executor.import_path,
    ])
    job_module = importlib.import_module(job_module_path)
    found_jobs: list[Job] = []
    for _, job_class in inspect.getmembers(job_module, inspect.isclass):
        if getattr(job_class, "_unc_job_registered", False):
            found_jobs.append(job_class())
    assert len(found_jobs) == 1, (
        f"expected exactly one job class in {executor.import_path}, found {len(found_jobs)}"
    )
    return found_jobs[0]
