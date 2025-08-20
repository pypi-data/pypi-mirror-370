import asyncio
import typing
from dataclasses import dataclass
from enum import StrEnum

from uncountable.types import queued_job_t


class CommandType(StrEnum):
    ENQUEUE_JOB = "enqueue_job"


RT = typing.TypeVar("RT")


@dataclass(kw_only=True)
class CommandBase[RT]:
    type: CommandType
    response_queue: asyncio.Queue[RT]


@dataclass(kw_only=True)
class CommandEnqueueJobResponse:
    queued_job_uuid: str


@dataclass(kw_only=True)
class CommandEnqueueJob(CommandBase[CommandEnqueueJobResponse]):
    type: CommandType = CommandType.ENQUEUE_JOB
    job_ref_name: str
    payload: queued_job_t.QueuedJobPayload
    response_queue: asyncio.Queue[CommandEnqueueJobResponse]


_Command = CommandEnqueueJob


CommandQueue = asyncio.Queue[_Command]

CommandTask = asyncio.Task[_Command]


class CommandServerException(Exception):
    pass


class CommandServerTimeout(CommandServerException):
    pass


class CommandServerBadResponse(CommandServerException):
    pass
