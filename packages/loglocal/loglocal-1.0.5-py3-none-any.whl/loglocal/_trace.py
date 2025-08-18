from opentelemetry.trace import Tracer
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from loglocal.models._config_models import LogLocalTraceOptions


def get_tracer(
    opts: LogLocalTraceOptions = LogLocalTraceOptions(),
    set_global_tracer_provider=False,
) -> Tracer:
    provider = TracerProvider(
        resource=Resource.create({"service.name": opts.service_name})
    )
    if opts.span_processor:
        provider.add_span_processor(opts.span_processor)
    # if set_global_tracer_provider:
    trace.set_tracer_provider(provider)
    if opts.inst_reg_callable:
        opts.inst_reg_callable(provider)
    return trace.get_tracer(__name__, opts.version)
