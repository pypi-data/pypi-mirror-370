import asyncio
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass

from opentelemetry.trace import get_current_span

from uncountable.core.async_batch import AsyncBatchProcessor
from uncountable.integration.construct_client import construct_uncountable_client
from uncountable.integration.executors.executors import execute_job
from uncountable.integration.job import JobArguments
from uncountable.integration.queue_runner.datastore.interface import Datastore
from uncountable.integration.queue_runner.types import ListenQueue, ResultQueue
from uncountable.integration.scan_profiles import load_profiles
from uncountable.integration.telemetry import JobLogger, Logger, get_otel_tracer
from uncountable.types import base_t, job_definition_t, queued_job_t


class Worker:
    def __init__(
        self,
        *,
        process_pool: ProcessPoolExecutor,
        listen_queue: ListenQueue,
        result_queue: ResultQueue,
        datastore: Datastore,
    ) -> None:
        self.process_pool = process_pool
        self.listen_queue = listen_queue
        self.result_queue = result_queue
        self.datastore = datastore

    async def run_worker_loop(self) -> None:
        logger = Logger(get_current_span())
        while True:
            try:
                queued_job = await self.listen_queue.get()
                self.datastore.increment_num_attempts(queued_job.queued_job_uuid)
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self.process_pool, run_queued_job, queued_job
                )
                assert isinstance(result, job_definition_t.JobResult)
                await self.result_queue.put(
                    queued_job_t.QueuedJobResult(
                        job_result=result, queued_job_uuid=queued_job.queued_job_uuid
                    )
                )
            except BaseException as e:
                logger.log_exception(e)
                raise e


@dataclass(kw_only=True)
class RegisteredJobDetails:
    profile_metadata: job_definition_t.ProfileMetadata
    job_definition: job_definition_t.JobDefinition


def get_registered_job_details(job_ref_name: str) -> RegisteredJobDetails:
    profiles = load_profiles()
    for profile_metadata in profiles:
        for job_definition in profile_metadata.jobs:
            if job_definition.id == job_ref_name:
                return RegisteredJobDetails(
                    profile_metadata=profile_metadata,
                    job_definition=job_definition,
                )
    raise Exception(f"profile not found for job {job_ref_name}")


def _resolve_queued_job_payload(queued_job: queued_job_t.QueuedJob) -> base_t.JsonValue:
    match queued_job.payload.invocation_context:
        case queued_job_t.InvocationContextCron():
            return None
        case queued_job_t.InvocationContextManual():
            return None
        case queued_job_t.InvocationContextWebhook():
            return queued_job.payload.invocation_context.webhook_payload


def run_queued_job(
    queued_job: queued_job_t.QueuedJob,
) -> job_definition_t.JobResult:
    with get_otel_tracer().start_as_current_span(name="run_queued_job") as span:
        job_details = get_registered_job_details(queued_job.job_ref_name)
        job_logger = JobLogger(
            base_span=span,
            profile_metadata=job_details.profile_metadata,
            job_definition=job_details.job_definition,
        )
        try:
            client = construct_uncountable_client(
                profile_meta=job_details.profile_metadata, logger=job_logger
            )
            batch_processor = AsyncBatchProcessor(client=client)

            payload = _resolve_queued_job_payload(queued_job)

            args = JobArguments(
                job_definition=job_details.job_definition,
                client=client,
                batch_processor=batch_processor,
                profile_metadata=job_details.profile_metadata,
                logger=job_logger,
                payload=payload,
            )

            return execute_job(
                args=args,
                profile_metadata=job_details.profile_metadata,
                job_definition=job_details.job_definition,
                job_uuid=queued_job.queued_job_uuid,
            )
        except BaseException as e:
            job_logger.log_exception(e)
            return job_definition_t.JobResult(success=False)
