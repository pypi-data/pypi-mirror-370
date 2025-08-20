import time

from uncountable.integration.job import CronJob, JobArguments, register_job
from uncountable.types.job_definition_t import JobResult


@register_job
class MyConcurrentCronJob(CronJob):
    def run(self, args: JobArguments) -> JobResult:
        time.sleep(10)
        return JobResult(success=True)
