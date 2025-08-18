from typing import Callable

from dotenv import load_dotenv

from loglocal._loglocal import LogLocal
from opentelemetry.trace import Tracer as _Tracer
from loglocal._trace import get_tracer as _get_tracer

load_dotenv()
Logger: Callable[..., LogLocal] = LogLocal.from_config
Tracer: Callable[..., _Tracer] = _get_tracer
__all__ = [
    "Logger",
    "Tracer",
    "LogLocal",
]
