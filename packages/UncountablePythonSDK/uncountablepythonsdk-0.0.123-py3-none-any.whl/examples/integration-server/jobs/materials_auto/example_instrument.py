import time
from dataclasses import dataclass
from decimal import Decimal

from uncountable.integration.job import JobArguments, WebhookJob, register_job
from uncountable.types import (
    base_t,
    entity_t,
    identifier_t,
    integrations_t,
    job_definition_t,
    publish_realtime_data_t,
)
from uncountable.types.client_base import APIRequest


@dataclass(kw_only=True)
class InstrumentPayload:
    equipment_id: base_t.ObjectId


@register_job
class InstrumentExample(WebhookJob[InstrumentPayload]):
    def run(
        self, args: JobArguments, payload: InstrumentPayload
    ) -> job_definition_t.JobResult:
        equipment_data = args.client.get_entities_data(
            entity_type=entity_t.EntityType.EQUIPMENT,
            entity_ids=[payload.equipment_id],
        ).entity_details[0]

        # Load the instrument's connection details from the entity
        instrument_id = None
        for field in equipment_data.field_values:
            if field.field_ref_name == "ins_instrument_id":
                instrument_id = field.value

        if instrument_id is None:
            args.logger.log_error("Could not find instrument ID")
            return job_definition_t.JobResult(success=False)

        args.logger.log_info(f"Instrument ID: {instrument_id}")

        for i in range(10):
            req_args = publish_realtime_data_t.Arguments(
                data_package=integrations_t.DataPackageNumericReading(
                    value=Decimal(i * 15),
                    target_entity=entity_t.EntityIdentifier(
                        identifier_key=identifier_t.IdentifierKeyId(
                            id=payload.equipment_id
                        ),
                        type=entity_t.EntityType.EQUIPMENT,
                    ),
                ),
            )
            api_request = APIRequest(
                method=publish_realtime_data_t.ENDPOINT_METHOD,
                endpoint=publish_realtime_data_t.ENDPOINT_PATH,
                args=req_args,
            )
            args.client.do_request(
                api_request=api_request, return_type=publish_realtime_data_t.Data
            )
            time.sleep(0.75)

        return job_definition_t.JobResult(success=True)

    @property
    def webhook_payload_type(self) -> type:
        return InstrumentPayload
