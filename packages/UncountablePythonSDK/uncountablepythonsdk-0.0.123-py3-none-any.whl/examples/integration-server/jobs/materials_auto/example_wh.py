from dataclasses import dataclass

from uncountable.integration.job import JobArguments, WebhookJob, register_job
from uncountable.types import job_definition_t


@dataclass(kw_only=True)
class ExampleWebhookPayload:
    id: int
    message: str


@register_job
class WebhookExample(WebhookJob[ExampleWebhookPayload]):
    def run(
        self, args: JobArguments, payload: ExampleWebhookPayload
    ) -> job_definition_t.JobResult:
        args.logger.log_info(f"webhook invoked with payload: {payload}")
        return job_definition_t.JobResult(success=True)

    @property
    def webhook_payload_type(self) -> type:
        return ExampleWebhookPayload
