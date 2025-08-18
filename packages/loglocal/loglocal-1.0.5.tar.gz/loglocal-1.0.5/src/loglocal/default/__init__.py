from dotenv import load_dotenv

from loglocal import LogLocal

load_dotenv()


logger = LogLocal.default()
tracer = logger.get_tracer()

__all__ = [
    "logger",
    "tracer",
]
