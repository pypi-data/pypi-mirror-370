import functools
import json
import os
import time
import traceback
import typing
from contextlib import contextmanager
from enum import StrEnum
from typing import Generator, assert_never, cast

from opentelemetry import _logs, trace
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import Logger as OTELLogger
from opentelemetry.sdk._logs import LoggerProvider, LogRecord
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, ConsoleLogExporter
from opentelemetry.sdk.resources import Attributes, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    SimpleSpanProcessor,
)
from opentelemetry.trace import DEFAULT_TRACE_OPTIONS, Span, Tracer

from uncountable.core.environment import (
    get_otel_enabled,
    get_server_env,
    get_version,
)
from uncountable.types import base_t, job_definition_t


def _cast_attributes(attributes: dict[str, base_t.JsonValue]) -> Attributes:
    return cast(Attributes, attributes)


def one_line_formatter(record: LogRecord) -> str:
    return json.dumps(record.to_json(), separators=(",", ":"))


@functools.cache
def get_otel_resource() -> Resource:
    attributes: dict[str, base_t.JsonValue] = {
        "service.name": "integration-server",
        "sdk.version": get_version(),
    }
    unc_version = os.environ.get("UNC_VERSION")
    if unc_version is not None:
        attributes["service.version"] = unc_version
    unc_env = get_server_env()
    if unc_env is not None:
        attributes["deployment.environment"] = unc_env
    resource = Resource.create(attributes=_cast_attributes(attributes))
    return resource


@functools.cache
def get_otel_tracer() -> Tracer:
    provider = TracerProvider(resource=get_otel_resource())
    if get_otel_enabled():
        provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(provider)
    return provider.get_tracer("integration.telemetry")


@functools.cache
def get_otel_logger() -> OTELLogger:
    provider = LoggerProvider(resource=get_otel_resource())
    provider.add_log_record_processor(
        BatchLogRecordProcessor(ConsoleLogExporter(formatter=one_line_formatter))
    )
    if get_otel_enabled():
        provider.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter()))
    _logs.set_logger_provider(provider)
    return provider.get_logger("integration.telemetry")


class LogSeverity(StrEnum):
    INFO = "Info"
    WARN = "Warn"
    ERROR = "Error"


class Logger:
    current_span: Span

    def __init__(self, base_span: Span) -> None:
        self.current_span = base_span

    @property
    def current_span_id(self) -> int:
        return self.current_span.get_span_context().span_id

    @property
    def current_trace_id(self) -> int | None:
        return self.current_span.get_span_context().trace_id

    def _patch_attributes(self, attributes: Attributes | None) -> Attributes:
        return attributes or {}

    def _emit_log(
        self, message: str, *, severity: LogSeverity, attributes: Attributes | None
    ) -> None:
        otel_logger = get_otel_logger()
        log_record = LogRecord(
            body=message,
            severity_text=severity,
            timestamp=time.time_ns(),
            attributes=self._patch_attributes(attributes),
            span_id=self.current_span_id,
            trace_id=self.current_trace_id,
            trace_flags=DEFAULT_TRACE_OPTIONS,
            severity_number=_logs.SeverityNumber.UNSPECIFIED,
            resource=get_otel_resource(),
        )
        otel_logger.emit(log_record)

    def log_info(self, message: str, *, attributes: Attributes | None = None) -> None:
        self._emit_log(
            message=message, severity=LogSeverity.INFO, attributes=attributes
        )

    def log_warning(
        self, message: str, *, attributes: Attributes | None = None
    ) -> None:
        self._emit_log(
            message=message, severity=LogSeverity.WARN, attributes=attributes
        )

    def log_error(self, message: str, *, attributes: Attributes | None = None) -> None:
        self._emit_log(
            message=message, severity=LogSeverity.ERROR, attributes=attributes
        )

    def log_exception(
        self,
        exception: BaseException,
        *,
        message: str | None = None,
        attributes: Attributes | None = None,
    ) -> None:
        traceback_str = "".join(traceback.format_exception(exception))
        patched_attributes = self._patch_attributes(attributes)
        self.current_span.record_exception(
            exception=exception, attributes=patched_attributes
        )
        self.log_error(
            message=f"error: {message}\nexception: {exception}{traceback_str}",
            attributes=patched_attributes,
        )

    @contextmanager
    def push_scope(
        self, scope_name: str, *, attributes: Attributes | None = None
    ) -> Generator[typing.Self, None, None]:
        with get_otel_tracer().start_as_current_span(
            scope_name, attributes=self._patch_attributes(attributes)
        ):
            yield self


class JobLogger(Logger):
    def __init__(
        self,
        *,
        base_span: Span,
        profile_metadata: job_definition_t.ProfileMetadata,
        job_definition: job_definition_t.JobDefinition,
    ) -> None:
        self.profile_metadata = profile_metadata
        self.job_definition = job_definition
        super().__init__(base_span)

    def _patch_attributes(self, attributes: Attributes | None) -> Attributes:
        patched_attributes: dict[str, base_t.JsonValue] = {
            **(attributes if attributes is not None else {})
        }
        patched_attributes["profile.name"] = self.profile_metadata.name
        patched_attributes["profile.base_url"] = self.profile_metadata.base_url
        patched_attributes["job.name"] = self.job_definition.name
        patched_attributes["job.id"] = self.job_definition.id
        patched_attributes["job.definition_type"] = self.job_definition.type
        match self.job_definition:
            case job_definition_t.CronJobDefinition():
                patched_attributes["job.definition.cron_spec"] = (
                    self.job_definition.cron_spec
                )
            case job_definition_t.HttpJobDefinitionBase():
                pass
            case _:
                assert_never(self.job_definition)
        patched_attributes["job.definition.executor.type"] = (
            self.job_definition.executor.type
        )
        match self.job_definition.executor:
            case job_definition_t.JobExecutorScript():
                patched_attributes["job.definition.executor.import_path"] = (
                    self.job_definition.executor.import_path
                )
            case job_definition_t.JobExecutorGenericUpload():
                patched_attributes["job.definition.executor.data_source.type"] = (
                    self.job_definition.executor.data_source.type
                )
            case _:
                assert_never(self.job_definition.executor)
        return _cast_attributes(patched_attributes)


@contextmanager
def push_scope_optional(
    logger: Logger | None, scope_name: str, *, attributes: Attributes | None = None
) -> Generator[None, None, None]:
    if logger is None:
        yield
    else:
        with logger.push_scope(scope_name, attributes=attributes):
            yield
