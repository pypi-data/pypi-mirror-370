from io import BytesIO

from uncountable.core.file_upload import DataFileUpload, FileUpload
from uncountable.integration.job import JobArguments, RunsheetWebhookJob, register_job
from uncountable.types import entity_t


@register_job
class StandardRunsheetGenerator(RunsheetWebhookJob):
    def build_runsheet(
        self,
        *,
        args: JobArguments,
        entities: list[entity_t.Entity],
    ) -> FileUpload:
        args.logger.log_info(f"Generating runsheet for {len(entities)} entities")

        content = []
        content.append("STANDARD LAB RUNSHEET\n")
        content.append("=" * 30 + "\n\n")

        for entity in entities:
            content.append(f"Type: {entity.type}\n")
            content.append(f"ID: {entity.id}\n")

            if hasattr(entity, "field_values") and entity.field_values:
                content.append("Field Values:\n")
                for field in entity.field_values:
                    content.append(f"  - {field.name}: {field.value}\n")

            content.append("\n")

        runsheet_data = "".join(content).encode("utf-8")

        return DataFileUpload(name="lab_runsheet.txt", data=BytesIO(runsheet_data))
