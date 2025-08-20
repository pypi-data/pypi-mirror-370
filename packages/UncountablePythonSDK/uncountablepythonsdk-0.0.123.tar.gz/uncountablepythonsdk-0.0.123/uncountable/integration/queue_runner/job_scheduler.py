import asyncio
import sys
import typing
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass

from opentelemetry.trace import get_current_span

from uncountable.integration.queue_runner.command_server import (
    CommandEnqueueJob,
    CommandEnqueueJobResponse,
    CommandQueue,
    CommandTask,
)
from uncountable.integration.queue_runner.datastore import DatastoreSqlite
from uncountable.integration.queue_runner.datastore.interface import Datastore
from uncountable.integration.queue_runner.worker import Worker
from uncountable.integration.scan_profiles import load_profiles
from uncountable.integration.telemetry import Logger
from uncountable.types import job_definition_t, queued_job_t

from .types import ResultQueue, ResultTask

_MAX_JOB_WORKERS = 5


@dataclass(kw_only=True, frozen=True)
class JobListenerKey:
    profile_name: str
    subqueue_name: str = "default"


def _get_job_worker_key(
    job_definition: job_definition_t.JobDefinition, profile_name: str
) -> JobListenerKey:
    if job_definition.subqueue_name is not None:
        return JobListenerKey(
            profile_name=profile_name, subqueue_name=job_definition.subqueue_name
        )
    return JobListenerKey(profile_name=profile_name)


def on_worker_crash(
    worker_key: JobListenerKey,
) -> typing.Callable[[asyncio.Task], None]:
    def hook(task: asyncio.Task) -> None:
        Logger(get_current_span()).log_exception(
            Exception(
                f"worker {worker_key.profile_name}_{worker_key.subqueue_name} crashed unexpectedly"
            )
        )
        sys.exit(1)

    return hook


def _start_workers(
    process_pool: ProcessPoolExecutor, result_queue: ResultQueue, datastore: Datastore
) -> dict[str, Worker]:
    profiles = load_profiles()
    job_queue_worker_lookup: dict[JobListenerKey, Worker] = {}
    job_worker_lookup: dict[str, Worker] = {}
    job_definition_lookup: dict[str, job_definition_t.JobDefinition] = {}
    for profile in profiles:
        for job_definition in profile.jobs:
            job_definition_lookup[job_definition.id] = job_definition
            job_worker_key = _get_job_worker_key(job_definition, profile.name)
            if job_worker_key not in job_queue_worker_lookup:
                worker = Worker(
                    process_pool=process_pool,
                    listen_queue=asyncio.Queue(),
                    result_queue=result_queue,
                    datastore=datastore,
                )
                task = asyncio.create_task(worker.run_worker_loop())
                task.add_done_callback(on_worker_crash(job_worker_key))
                job_queue_worker_lookup[job_worker_key] = worker
            job_worker_lookup[job_definition.id] = job_queue_worker_lookup[
                job_worker_key
            ]
    return job_worker_lookup


async def start_scheduler(
    command_queue: CommandQueue, datastore: DatastoreSqlite
) -> None:
    logger = Logger(get_current_span())
    result_queue: ResultQueue = asyncio.Queue()

    with ProcessPoolExecutor(max_workers=_MAX_JOB_WORKERS) as process_pool:
        job_worker_lookup = _start_workers(
            process_pool, result_queue, datastore=datastore
        )

        queued_jobs = datastore.load_job_queue()

        async def enqueue_queued_job(queued_job: queued_job_t.QueuedJob) -> None:
            try:
                worker = job_worker_lookup[queued_job.job_ref_name]
            except KeyError as e:
                logger.log_exception(e)
                datastore.remove_job_from_queue(queued_job.queued_job_uuid)
                return
            await worker.listen_queue.put(queued_job)

        async def _enqueue_or_deduplicate_job(
            job_ref_name: str,
            payload: queued_job_t.QueuedJobPayload,
        ) -> str:
            if isinstance(
                payload.invocation_context,
                (
                    queued_job_t.InvocationContextCron,
                    queued_job_t.InvocationContextManual,
                ),
            ):
                existing_queued_job = datastore.get_next_queued_job_for_ref_name(
                    job_ref_name=job_ref_name
                )
                if existing_queued_job is not None:
                    return existing_queued_job.queued_job_uuid
            queued_job = datastore.add_job_to_queue(
                job_payload=payload,
                job_ref_name=job_ref_name,
            )
            await enqueue_queued_job(queued_job)
            return queued_job.queued_job_uuid

        async def _handle_enqueue_job_command(command: CommandEnqueueJob) -> None:
            queued_job_uuid = await _enqueue_or_deduplicate_job(
                job_ref_name=command.job_ref_name,
                payload=command.payload,
            )
            await command.response_queue.put(
                CommandEnqueueJobResponse(queued_job_uuid=queued_job_uuid)
            )

        for queued_job in queued_jobs:
            await enqueue_queued_job(queued_job)

        result_task: ResultTask = asyncio.create_task(result_queue.get())
        command_task: CommandTask = asyncio.create_task(command_queue.get())
        while True:
            finished, _ = await asyncio.wait(
                [result_task, command_task], return_when=asyncio.FIRST_COMPLETED
            )

            for task in finished:
                if task == command_task:
                    command = command_task.result()
                    match command:
                        case CommandEnqueueJob():
                            await _handle_enqueue_job_command(command=command)
                        case _:
                            typing.assert_never(command)
                    command_task = asyncio.create_task(command_queue.get())
                elif task == result_task:
                    queued_job_result = result_task.result()
                    datastore.remove_job_from_queue(queued_job_result.queued_job_uuid)
                    result_task = asyncio.create_task(result_queue.get())
