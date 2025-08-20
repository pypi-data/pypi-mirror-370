from dataclasses import dataclass

from uncountable.integration.http_server import (
    GenericHttpRequest,
    GenericHttpResponse,
)
from uncountable.integration.http_server.types import HttpException
from uncountable.integration.job import CustomHttpJob, register_job
from uncountable.types import job_definition_t


@dataclass(kw_only=True)
class ExampleWebhookPayload:
    id: int
    message: str


_EXPECTED_USER_ID = 1


@register_job
class HttpExample(CustomHttpJob):
    @staticmethod
    def validate_request(
        *,
        request: GenericHttpRequest,  # noqa: ARG004
        job_definition: job_definition_t.HttpJobDefinitionBase,  # noqa: ARG004
        profile_meta: job_definition_t.ProfileMetadata,  # noqa: ARG004
    ) -> None:
        if (
            CustomHttpJob.get_validated_oauth_request_user_id(
                request=request, profile_metadata=profile_meta
            )
            != _EXPECTED_USER_ID
        ):
            raise HttpException(
                message="unauthorized; invalid oauth token", error_code=401
            )

    @staticmethod
    def handle_request(
        *,
        request: GenericHttpRequest,  # noqa: ARG004
        job_definition: job_definition_t.HttpJobDefinitionBase,  # noqa: ARG004
        profile_meta: job_definition_t.ProfileMetadata,  # noqa: ARG004
    ) -> GenericHttpResponse:
        return GenericHttpResponse(response="OK", status_code=200)
