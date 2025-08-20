import functools
import hmac
import typing
from abc import ABC, abstractmethod
from dataclasses import dataclass

import simplejson

from pkgs.argument_parser import CachedParser
from pkgs.serialization_util import serialize_for_api
from uncountable.core.async_batch import AsyncBatchProcessor
from uncountable.core.client import Client
from uncountable.core.environment import get_local_admin_server_port
from uncountable.core.file_upload import FileUpload
from uncountable.core.types import AuthDetailsOAuth
from uncountable.integration.http_server import (
    GenericHttpRequest,
    GenericHttpResponse,
    HttpException,
)
from uncountable.integration.queue_runner.command_server.command_client import (
    send_job_queue_message,
)
from uncountable.integration.queue_runner.command_server.types import (
    CommandServerException,
)
from uncountable.integration.secret_retrieval.retrieve_secret import retrieve_secret
from uncountable.integration.telemetry import JobLogger
from uncountable.types import (
    base_t,
    entity_t,
    job_definition_t,
    queued_job_t,
    webhook_job_t,
)
from uncountable.types.job_definition_t import (
    HttpJobDefinitionBase,
    JobDefinition,
    JobResult,
    ProfileMetadata,
)


@dataclass(kw_only=True)
class JobArguments:
    job_definition: JobDefinition
    profile_metadata: ProfileMetadata
    client: Client
    batch_processor: AsyncBatchProcessor
    logger: JobLogger
    payload: base_t.JsonValue


# only for compatibility:
CronJobArguments = JobArguments


class Job[PT](ABC):
    _unc_job_registered: bool = False

    @property
    @abstractmethod
    def payload_type(self) -> type[PT]: ...

    @abstractmethod
    def run_outer(self, args: JobArguments) -> JobResult: ...

    @functools.cached_property
    def _cached_payload_parser(self) -> CachedParser[PT]:
        return CachedParser(self.payload_type)

    def get_payload(self, payload: base_t.JsonValue) -> PT:
        return self._cached_payload_parser.parse_storage(payload)


class CronJob(Job):
    @property
    def payload_type(self) -> type[None]:
        return type(None)

    def run_outer(self, args: JobArguments) -> JobResult:
        assert isinstance(args, CronJobArguments)
        return self.run(args)

    @abstractmethod
    def run(self, args: JobArguments) -> JobResult: ...


WPT = typing.TypeVar("WPT")


@dataclass(kw_only=True)
class WebhookResponse:
    pass


class _RequestValidatorClient(Client):
    def __init__(self, *, base_url: str, oauth_bearer_token: str):
        super().__init__(
            base_url=base_url,
            auth_details=AuthDetailsOAuth(refresh_token=""),
            config=None,
        )
        self._oauth_bearer_token = oauth_bearer_token

    def _get_oauth_bearer_token(self, *, oauth_details: AuthDetailsOAuth) -> str:
        return self._oauth_bearer_token


class CustomHttpJob(Job[GenericHttpRequest]):
    @property
    def payload_type(self) -> type[GenericHttpRequest]:
        return GenericHttpRequest

    @staticmethod
    @abstractmethod
    def validate_request(
        *,
        request: GenericHttpRequest,
        job_definition: HttpJobDefinitionBase,
        profile_meta: ProfileMetadata,
    ) -> None:
        """
        Validate that the request is valid. If the request is invalid, raise an
        exception.
        """
        ...

    @staticmethod
    def get_validated_oauth_request_user_id(
        *, profile_metadata: ProfileMetadata, request: GenericHttpRequest
    ) -> base_t.ObjectId:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if token == "":
            raise HttpException(
                message="unauthorized; no bearer token in request", error_code=401
            )
        return (
            _RequestValidatorClient(
                base_url=profile_metadata.base_url,
                oauth_bearer_token=token,
            )
            .get_current_user_info()
            .user_id
        )

    @staticmethod
    @abstractmethod
    def handle_request(
        *,
        request: GenericHttpRequest,
        job_definition: HttpJobDefinitionBase,
        profile_meta: ProfileMetadata,
    ) -> GenericHttpResponse:
        """
        Handle the request synchronously. Normally this should just enqueue a job
        and return immediately (see WebhookJob as an example).
        """
        ...

    def run_outer(self, args: JobArguments) -> JobResult:
        args.logger.log_warning(
            message=f"Unexpected call to run_outer for CustomHttpJob: {args.job_definition.id}"
        )
        return JobResult(success=False)


class WebhookJob[WPT](Job[webhook_job_t.WebhookEventPayload]):
    @property
    def payload_type(self) -> type[webhook_job_t.WebhookEventPayload]:
        return webhook_job_t.WebhookEventPayload

    @property
    @abstractmethod
    def webhook_payload_type(self) -> type[WPT]: ...

    @staticmethod
    def validate_request(
        *,
        request: GenericHttpRequest,
        job_definition: job_definition_t.HttpJobDefinitionBase,
        profile_meta: ProfileMetadata,
    ) -> None:
        assert isinstance(job_definition, job_definition_t.WebhookJobDefinition)
        signature_key = retrieve_secret(
            profile_metadata=profile_meta,
            secret_retrieval=job_definition.signature_key_secret,
        )
        passed_signature = request.headers.get("Uncountable-Webhook-Signature")
        if passed_signature is None:
            raise HttpException.no_signature_passed()

        request_body_signature = hmac.new(
            signature_key.encode("utf-8"), msg=request.body_bytes, digestmod="sha256"
        ).hexdigest()

        if request_body_signature != passed_signature:
            raise HttpException.payload_failed_signature()

    @staticmethod
    def handle_request(
        *,
        request: GenericHttpRequest,
        job_definition: job_definition_t.HttpJobDefinitionBase,
        profile_meta: ProfileMetadata,  # noqa: ARG004
    ) -> GenericHttpResponse:
        try:
            request_body = simplejson.loads(request.body_text)
            webhook_payload = typing.cast(base_t.JsonValue, request_body)
        except (simplejson.JSONDecodeError, ValueError) as e:
            raise HttpException.body_parse_error() from e

        try:
            send_job_queue_message(
                job_ref_name=job_definition.id,
                payload=queued_job_t.QueuedJobPayload(
                    invocation_context=queued_job_t.InvocationContextWebhook(
                        webhook_payload=webhook_payload
                    )
                ),
                port=get_local_admin_server_port(),
            )
        except CommandServerException as e:
            raise HttpException.unknown_error() from e

        return GenericHttpResponse(
            response=simplejson.dumps(serialize_for_api(WebhookResponse())),
            status_code=200,
        )

    def run_outer(self, args: JobArguments) -> JobResult:
        webhook_body = self.get_payload(args.payload)
        inner_payload = CachedParser(self.webhook_payload_type).parse_api(
            webhook_body.data
        )
        return self.run(args, inner_payload)

    @abstractmethod
    def run(self, args: JobArguments, payload: WPT) -> JobResult: ...


def register_job(cls: type[Job]) -> type[Job]:
    cls._unc_job_registered = True
    return cls


class RunsheetWebhookJob(WebhookJob[webhook_job_t.RunsheetWebhookPayload]):
    @property
    def webhook_payload_type(self) -> type:
        return webhook_job_t.RunsheetWebhookPayload

    @abstractmethod
    def build_runsheet(
        self,
        *,
        args: JobArguments,
        entities: list[entity_t.Entity],
    ) -> FileUpload: ...

    def run(
        self, args: JobArguments, payload: webhook_job_t.RunsheetWebhookPayload
    ) -> JobResult:
        runsheet = self.build_runsheet(args=args, entities=payload.entities)

        files = args.client.upload_files(file_uploads=[runsheet])
        args.client.complete_async_upload(
            async_job_id=payload.async_job_id, file_id=files[0].file_id
        )

        return JobResult(
            success=True,
        )
