from typing import assert_never

from uncountable.core.client import Client
from uncountable.integration.executors.generic_upload_executor import GenericUploadJob
from uncountable.integration.executors.script_executor import resolve_script_executor
from uncountable.integration.job import Job, JobArguments
from uncountable.types import (
    async_jobs_t,
    entity_t,
    field_values_t,
    identifier_t,
    integration_server_t,
    job_definition_t,
    transition_entity_phase_t,
)


def resolve_executor(
    job_executor: job_definition_t.JobExecutor,
    profile_metadata: job_definition_t.ProfileMetadata,
) -> Job:
    match job_executor:
        case job_definition_t.JobExecutorScript():
            return resolve_script_executor(
                job_executor, profile_metadata=profile_metadata
            )
        case job_definition_t.JobExecutorGenericUpload():
            return GenericUploadJob(
                remote_directories=job_executor.remote_directories,
                upload_strategy=job_executor.upload_strategy,
                data_source=job_executor.data_source,
            )
    assert_never(job_executor)


def _create_run_entity(
    *,
    client: Client,
    logging_settings: job_definition_t.JobLoggingSettings,
    job_uuid: str,
) -> entity_t.Entity:
    run_entity = client.create_entity(
        entity_type=entity_t.EntityType.ASYNC_JOB,
        definition_key=identifier_t.IdentifierKeyRefName(
            ref_name="unc_integration_server_run_definition"
        ),
        field_values=[
            field_values_t.FieldRefNameValue(
                field_ref_name=async_jobs_t.ASYNC_JOB_TYPE_FIELD_REF_NAME,
                value=async_jobs_t.AsyncJobType.INTEGRATION_SERVER_RUN,
            ),
            field_values_t.FieldRefNameValue(
                field_ref_name=async_jobs_t.ASYNC_JOB_STATUS_FIELD_REF_NAME,
                value=async_jobs_t.AsyncJobStatus.IN_PROGRESS,
            ),
            field_values_t.FieldRefNameValue(
                field_ref_name=integration_server_t.INTEGRATION_SERVER_RUN_UUID_FIELD_REF_NAME,
                value=job_uuid,
            ),
        ],
    ).entity
    client.transition_entity_phase(
        entity=run_entity,
        transition=transition_entity_phase_t.TransitionIdentifierPhases(
            phase_from_key=identifier_t.IdentifierKeyRefName(
                ref_name="unc_integration_server_run__queued"
            ),
            phase_to_key=identifier_t.IdentifierKeyRefName(
                ref_name="unc_integration_server_run__started"
            ),
        ),
    )
    if logging_settings.share_with_user_groups is not None:
        client.grant_entity_permissions(
            entity_type=entity_t.EntityType.ASYNC_JOB,
            entity_key=identifier_t.IdentifierKeyId(id=run_entity.id),
            permission_types=[
                entity_t.EntityPermissionType.READ,
                entity_t.EntityPermissionType.WRITE,
            ],
            user_group_keys=logging_settings.share_with_user_groups,
        )
    return run_entity


def execute_job(
    *,
    job_definition: job_definition_t.JobDefinition,
    profile_metadata: job_definition_t.ProfileMetadata,
    args: JobArguments,
    job_uuid: str,
) -> job_definition_t.JobResult:
    with args.logger.push_scope(job_definition.name) as job_logger:
        job = resolve_executor(job_definition.executor, profile_metadata)

        job_logger.log_info("running job")

        run_entity: entity_t.Entity | None = None
        try:
            if (
                job_definition.logging_settings is not None
                and job_definition.logging_settings.enabled
            ):
                run_entity = _create_run_entity(
                    client=args.client,
                    logging_settings=job_definition.logging_settings,
                    job_uuid=job_uuid,
                )
            result = job.run_outer(args=args)
        except Exception as e:
            job_logger.log_exception(e)
            if run_entity is not None:
                args.client.set_values(
                    entity=run_entity,
                    values=[
                        field_values_t.ArgumentValueRefName(
                            field_ref_name=async_jobs_t.ASYNC_JOB_STATUS_FIELD_REF_NAME,
                            value=async_jobs_t.AsyncJobStatus.ERROR,
                        ),
                    ],
                )
            return job_definition_t.JobResult(success=False)

        if args.batch_processor.current_queue_size() != 0:
            args.batch_processor.send()

        submitted_batch_job_ids = args.batch_processor.get_submitted_job_ids()
        job_logger.log_info(
            "completed job",
            attributes={
                "submitted_batch_job_ids": submitted_batch_job_ids,
                "success": result.success,
            },
        )
        if run_entity is not None:
            args.client.set_values(
                entity=run_entity,
                values=[
                    field_values_t.ArgumentValueRefName(
                        field_ref_name=async_jobs_t.ASYNC_JOB_STATUS_FIELD_REF_NAME,
                        value=async_jobs_t.AsyncJobStatus.COMPLETED
                        if result.success
                        else async_jobs_t.AsyncJobStatus.ERROR,
                    ),
                ],
            )

        return result
