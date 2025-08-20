import time

from uncountable.integration.job import CronJob, JobArguments, register_job
from uncountable.types import entity_t
from uncountable.types.job_definition_t import JobResult


@register_job
class MyCronJob(CronJob):
    def run(self, args: JobArguments) -> JobResult:
        matfam = args.client.get_entities_data(
            entity_ids=[1],
            entity_type=entity_t.EntityType.MATERIAL_FAMILY,
        ).entity_details[0]
        name = None
        for field_val in matfam.field_values:
            if field_val.field_ref_name == "name":
                name = field_val.value
        args.logger.log_info(f"material family found with name: {name}")
        time.sleep(1.5)
        return JobResult(success=True)
