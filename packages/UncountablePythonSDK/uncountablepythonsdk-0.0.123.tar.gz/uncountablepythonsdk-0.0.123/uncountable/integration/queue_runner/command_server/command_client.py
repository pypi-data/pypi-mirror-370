from contextlib import contextmanager
from typing import Generator

import grpc
import simplejson as json

from pkgs.serialization_util import serialize_for_api
from uncountable.integration.queue_runner.command_server.protocol.command_server_pb2 import (
    CheckHealthRequest,
    CheckHealthResult,
    EnqueueJobRequest,
    EnqueueJobResult,
    ListQueuedJobsRequest,
    ListQueuedJobsResult,
)
from uncountable.integration.queue_runner.command_server.types import (
    CommandServerBadResponse,
    CommandServerTimeout,
)
from uncountable.types import queued_job_t

from .protocol.command_server_pb2_grpc import CommandServerStub

_LOCAL_RPC_HOST = "localhost"
_DEFAULT_MESSAGE_TIMEOUT_SECS = 2


@contextmanager
def command_server_connection(
    host: str, port: int
) -> Generator[CommandServerStub, None, None]:
    try:
        with grpc.insecure_channel(f"{host}:{port}") as channel:
            stub = CommandServerStub(channel)
            yield stub
    except grpc._channel._InactiveRpcError as e:
        raise CommandServerTimeout() from e


def send_job_queue_message(
    *,
    job_ref_name: str,
    payload: queued_job_t.QueuedJobPayload,
    host: str = "localhost",
    port: int,
) -> str:
    with command_server_connection(host=host, port=port) as stub:
        request = EnqueueJobRequest(
            job_ref_name=job_ref_name,
            serialized_payload=json.dumps(serialize_for_api(payload)),
        )

        response = stub.EnqueueJob(request, timeout=_DEFAULT_MESSAGE_TIMEOUT_SECS)

        assert isinstance(response, EnqueueJobResult)
        if not response.successfully_queued:
            raise CommandServerBadResponse("queue operation was not successful")

        return response.queued_job_uuid


def check_health(*, host: str = _LOCAL_RPC_HOST, port: int) -> bool:
    with command_server_connection(host=host, port=port) as stub:
        request = CheckHealthRequest()

        response = stub.CheckHealth(request, timeout=_DEFAULT_MESSAGE_TIMEOUT_SECS)

        assert isinstance(response, CheckHealthResult)

        return response.success


def send_list_queued_jobs_message(
    *,
    offset: int,
    limit: int,
    host: str = "localhost",
    port: int,
) -> list[ListQueuedJobsResult.ListQueuedJobsResultItem]:
    with command_server_connection(host=host, port=port) as stub:
        request = ListQueuedJobsRequest(
            offset=offset,
            limit=limit,
        )

        try:
            response = stub.ListQueuedJobs(
                request, timeout=_DEFAULT_MESSAGE_TIMEOUT_SECS
            )
        except grpc.RpcError as e:
            raise ValueError(e.details())  # type: ignore

        assert isinstance(response, ListQueuedJobsResult)
        return list(response.queued_jobs)
