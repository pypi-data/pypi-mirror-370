from dataclasses import dataclass

from pkgs.argument_parser import CachedParser
from uncountable.core.environment import get_local_admin_server_port
from uncountable.integration.queue_runner.command_server.command_client import (
    send_job_queue_message,
)
from uncountable.types import queued_job_t
from uncountable.types.job_definition_t import JobDefinition, ProfileMetadata


@dataclass
class CronJobArgs:
    definition: JobDefinition
    profile_metadata: ProfileMetadata


cron_args_parser = CachedParser(CronJobArgs)


def cron_job_executor(**kwargs: dict) -> None:
    args_passed = cron_args_parser.parse_storage(kwargs)
    send_job_queue_message(
        job_ref_name=args_passed.definition.id,
        payload=queued_job_t.QueuedJobPayload(
            invocation_context=queued_job_t.InvocationContextCron()
        ),
        port=get_local_admin_server_port(),
    )
