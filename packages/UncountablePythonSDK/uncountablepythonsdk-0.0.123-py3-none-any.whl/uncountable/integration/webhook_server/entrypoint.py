import base64

import flask
from flask.typing import ResponseReturnValue
from opentelemetry.trace import get_current_span
from uncountable.core.environment import (
    get_http_server_port,
    get_server_env,
)
from uncountable.integration.executors.script_executor import resolve_script_executor
from uncountable.integration.http_server import GenericHttpRequest, HttpException
from uncountable.integration.job import CustomHttpJob, WebhookJob
from uncountable.integration.scan_profiles import load_profiles
from uncountable.integration.telemetry import Logger
from uncountable.types import job_definition_t

app = flask.Flask(__name__)


def register_route(
    *,
    server_logger: Logger,
    profile_meta: job_definition_t.ProfileMetadata,
    job: job_definition_t.HttpJobDefinitionBase,
) -> None:
    route = f"/{profile_meta.name}/{job.id}"

    def handle_request() -> ResponseReturnValue:
        with server_logger.push_scope(route):
            try:
                if not isinstance(job.executor, job_definition_t.JobExecutorScript):
                    raise HttpException.configuration_error(
                        message="[internal] http job must use a script executor"
                    )
                job_instance = resolve_script_executor(
                    executor=job.executor, profile_metadata=profile_meta
                )
                if not isinstance(job_instance, (CustomHttpJob, WebhookJob)):
                    raise HttpException.configuration_error(
                        message="[internal] http job must descend from CustomHttpJob"
                    )
                http_request = GenericHttpRequest(
                    body_base64=base64.b64encode(flask.request.get_data()).decode(),
                    headers=dict(flask.request.headers),
                )
                job_instance.validate_request(
                    request=http_request, job_definition=job, profile_meta=profile_meta
                )
                http_response = job_instance.handle_request(
                    request=http_request, job_definition=job, profile_meta=profile_meta
                )

                return flask.make_response(
                    http_response.response,
                    http_response.status_code,
                    http_response.headers,
                )
            except HttpException as e:
                server_logger.log_exception(e)
                return e.make_error_response()
            except Exception as e:
                server_logger.log_exception(e)
                return HttpException.unknown_error().make_error_response()

    app.add_url_rule(
        route,
        endpoint=f"handle_request_{job.id}",
        view_func=handle_request,
        methods=["POST"],
    )

    server_logger.log_info(f"job {job.id} webhook registered at: {route}")


def main() -> None:
    profiles = load_profiles()
    for profile_metadata in profiles:
        server_logger = Logger(get_current_span())
        for job in profile_metadata.jobs:
            if isinstance(job, job_definition_t.HttpJobDefinitionBase):
                register_route(
                    server_logger=server_logger, profile_meta=profile_metadata, job=job
                )


main()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=get_http_server_port(),
        debug=get_server_env() == "playground",
        exclude_patterns=[],
    )
