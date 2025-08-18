import os
from typing import Any, Optional, Callable
from loguru._logger import Core
from opentelemetry.context import Context
from opentelemetry.sdk.trace import ReadableSpan, SpanProcessor
from opentelemetry.trace import TracerProvider
from pydantic import BaseModel, Field, ConfigDict


class LogConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    level: str = Field(default="INFO")
    file_rotation: str = Field(default="30 days")
    file_retention: str = Field(default="90 days")
    serialize: bool = Field(default=True)
    enqueue: bool = Field(default=True)
    diagnose: bool = Field(default=False)  # avoid leaking vars in production


class LogLocalOptions(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    core: Core = Field(default_factory=Core)
    exception: Any = None
    depth: int = 0
    record: bool = False
    lazy: bool = False
    colors: bool = True
    raw: bool = False
    capture: bool = True
    patchers: list[Any] = []
    extra: dict[str, Any] = {}


class DefaultSpanProcessor(SpanProcessor):
    def on_start(
        self,
        span: ReadableSpan,
        parent_context: Optional[Context] = None,
    ):
        print(f"Span started: {span.name} at {span.start_time}")

    def on_end(self, span: ReadableSpan):
        print(
            f"Span ended: {span.name} with status {span.status.status_code.name} at {span.end_time}"
        )


class LogLocalTraceOptions(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    service_name: str = Field(
        default=os.environ.get("LOGLOCAL_TRACE_SERVICE_NAME", "app")
    )
    version: Optional[str] = Field(
        default=os.environ.get("LOGLOCAL_TRACE_VERSION", None)
    )
    span_processor: Optional[SpanProcessor] = None
    inst_reg_callable: Optional[
        Callable[
            [
                TracerProvider,
            ],
            None,
        ]
    ] = Field(
        default=lambda provider: None,
        description="Callable to register instruments with the tracer provider.",
    )


class LogLocalConfig(BaseModel):
    log_path: str = os.environ.get("LOGLOCAL_PATH", os.path.join("logs", "app.log"))
    log_format: str = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} | {message} | {extra}"
    trace_opt: LogLocalTraceOptions = LogLocalTraceOptions()
    log_opt: LogLocalOptions = LogLocalOptions()
    log_config: LogConfig = LogConfig()
    sinks: list[
        Any
    ] = []  # List of additional sinks to be added to the logger, can be used for custom sinks or handlers.
