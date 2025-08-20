import argparse

from dateutil import tz
from opentelemetry.trace import get_current_span
from tabulate import tabulate

from uncountable.core.environment import get_local_admin_server_port
from uncountable.integration.queue_runner.command_server.command_client import (
    send_job_queue_message,
    send_list_queued_jobs_message,
)
from uncountable.integration.telemetry import Logger
from uncountable.types import queued_job_t


def register_enqueue_job_parser(
    sub_parser_manager: argparse._SubParsersAction,
    parents: list[argparse.ArgumentParser],
) -> None:
    run_parser = sub_parser_manager.add_parser(
        "run",
        parents=parents,
        help="Process a job with a given host and job ID",
        description="Process a job with a given host and job ID",
    )
    run_parser.add_argument("job_id", type=str, help="The ID of the job to process")

    def _handle_enqueue_job(args: argparse.Namespace) -> None:
        send_job_queue_message(
            job_ref_name=args.job_id,
            payload=queued_job_t.QueuedJobPayload(
                invocation_context=queued_job_t.InvocationContextManual()
            ),
            host=args.host,
            port=get_local_admin_server_port(),
        )

    run_parser.set_defaults(func=_handle_enqueue_job)


def register_list_queued_jobs(
    sub_parser_manager: argparse._SubParsersAction,
    parents: list[argparse.ArgumentParser],
) -> None:
    list_queued_jobs_parser = sub_parser_manager.add_parser(
        "list-queued-jobs",
        parents=parents,
        help="List all jobs queued on the integration server",
        description="List all jobs queued on the integration server",
    )

    list_queued_jobs_parser.add_argument(
        "--offset",
        type=int,
        default=0,
        help="Number of jobs to skip. Should be non-negative.",
    )
    list_queued_jobs_parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="A number between 1 and 100 specifying the number of jobs to return in the result set.",
    )

    def _handle_list_queued_jobs(args: argparse.Namespace) -> None:
        queued_jobs = send_list_queued_jobs_message(
            offset=args.offset,
            limit=args.limit,
            host=args.host,
            port=get_local_admin_server_port(),
        )

        headers = ["UUID", "Job Ref Name", "Attempts", "Submitted At"]
        rows = [
            [
                job.uuid,
                job.job_ref_name,
                job.num_attempts,
                job.submitted_at.ToDatetime(tz.UTC).astimezone(tz.tzlocal()),
            ]
            for job in queued_jobs
        ]
        print(tabulate(rows, headers=headers, tablefmt="grid"))

    list_queued_jobs_parser.set_defaults(func=_handle_list_queued_jobs)


def main() -> None:
    logger = Logger(get_current_span())

    main_parser = argparse.ArgumentParser(
        description="Execute a given integrations server command."
    )

    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument(
        "--host", type=str, default="localhost", nargs="?", help="The host to run on"
    )

    subparser_action = main_parser.add_subparsers(
        dest="command",
        required=True,
        help="The command to execute (e.g., 'run')",
    )

    register_enqueue_job_parser(subparser_action, parents=[base_parser])
    register_list_queued_jobs(subparser_action, parents=[base_parser])

    args = main_parser.parse_args()
    with logger.push_scope(args.command):
        args.func(args)


main()
