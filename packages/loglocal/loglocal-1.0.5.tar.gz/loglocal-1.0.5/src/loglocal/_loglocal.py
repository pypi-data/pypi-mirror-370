import sys
import time
import asyncio
from contextlib import nullcontext
from functools import wraps
from typing import Callable

from loguru._logger import Logger as LoguruLogger
from opentelemetry.trace import Tracer

from loglocal._trace import get_tracer
from loglocal.models._config_models import LogLocalConfig


class LogLocal(LoguruLogger):
    _tracer: Tracer = None

    @property
    def tracer(self) -> Tracer:
        """
        Property to access the tracer instance.
        """
        return self._tracer

    @tracer.setter
    def tracer(self, value: Tracer):
        """
        Setter to assign a tracer instance.
        """
        self._tracer = value

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _config_logger(self, _config: LogLocalConfig):
        self.add(
            sys.stderr,
            level=_config.log_config.level,
            format=_config.log_format,
            colorize=True,
            backtrace=True,
            diagnose=_config.log_config.diagnose,
        )
        self.add(
            _config.log_path,
            level=_config.log_config.level,
            format=_config.log_format,
            rotation=_config.log_config.file_rotation,
            retention=_config.log_config.file_retention,
            compression="zip",
            serialize=_config.log_config.serialize,
            enqueue=_config.log_config.enqueue,
            backtrace=True,
            diagnose=_config.log_config.diagnose,
        )
        if _config.sinks:
            for sink in _config.sinks:
                self.add(
                    sink,
                    serialize=_config.log_config.serialize,
                )

    def wrap(
        self, func=None, start_span: bool = False, span_name: str = None
    ) -> Callable:
        """
        Decorator to wrap sync or async functions for logging:
        :param span_name:
        :param start_span:
        :param func:
        :return:
        """

        def decorator(fn):
            _log = self.patch(
                lambda r: r.update(
                    function=fn.__name__,
                    name=fn.__module__,
                    line=fn.__code__.co_firstlineno,
                )
            )

            def log_binder(time_offset=0.0, is_error=False, *args, **kwargs) -> float:
                """
                Log the start and end of a function call with duration and error handling.
                :param time_offset:
                :param is_error:
                :param args:
                :param kwargs:
                :return float: Duration of the function call or the start time if not finished
                """
                _t = time.monotonic() - time_offset
                is_end = is_error or time_offset != 0.0
                extra = {
                    "duration": f"{_t if is_end else 0.0:.3f}s",
                    "result": f"{repr(kwargs.get('result', None))[:200]}",
                    "exception": f"{repr(kwargs.get('exception', None))}",
                    "args": repr(args)[:200],
                    "kwargs": repr(kwargs)[:200],
                }
                _log_msg = (
                    "❌ ←→ error"
                    if is_error
                    else "← finished"
                    if is_end
                    else "→ started"
                )
                if is_error:
                    _log.bind(**extra).error(_log_msg)
                else:
                    _log.bind(**extra).info(_log_msg)
                return _t

            def _start_as_current_span(_start_span: bool, _span_name: str):
                if _start_span:
                    return self._tracer.start_as_current_span(_span_name)
                return nullcontext()

            @wraps(fn)
            async def async_wrapper(*args, **kwargs):
                start = log_binder(*args, **kwargs)
                try:
                    with _start_as_current_span(start_span, span_name or fn.__name__):
                        result = await fn(*args, **kwargs)
                        # if result is a StreamingResponse
                        if hasattr(result, "body_iterator"):
                            log_binder(time_offset=start, result="StreamingResponse")
                        else:
                            log_binder(time_offset=start, result=result)
                        return result
                except Exception as e:
                    log_binder(time_offset=start, is_error=True, exception=str(e))
                    raise e

            @wraps(fn)
            def sync_wrapper(*args, **kwargs):
                start = log_binder(*args, **kwargs)
                try:
                    with _start_as_current_span(start_span, span_name or fn.__name__):
                        result = fn(*args, **kwargs)
                    log_binder(time_offset=start, result=result)
                    return result
                except Exception as e:
                    log_binder(time_offset=start, is_error=True, exception=str(e))
                    raise e

            return async_wrapper if asyncio.iscoroutinefunction(fn) else sync_wrapper

        return decorator(func) if func else decorator

    def get_tracer(self) -> Tracer:
        """
        Get the tracer instance.
        """
        return self._tracer

    @classmethod
    def from_config(
        cls,
        config: LogLocalConfig = LogLocalConfig(),
        set_global_tracer_provider=False,
        **kwargs,
    ) -> "LogLocal":
        """
        Create a logger instance from a LogLocalConfig object.
        """
        _instance = cls(**config.log_opt.model_dump(), **kwargs)
        _instance.remove()
        _instance._config_logger(config)
        _instance._tracer = get_tracer(
            opts=config.trace_opt, set_global_tracer_provider=set_global_tracer_provider
        )

        return _instance

    @classmethod
    def default(cls) -> "LogLocal":
        return cls.from_config(LogLocalConfig())
