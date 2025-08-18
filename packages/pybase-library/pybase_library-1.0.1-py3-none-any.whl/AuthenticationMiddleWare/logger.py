import logging
import os
from dotenv import load_dotenv
from AuthenticationMiddleWare.tracing_middleware import request_id_var

load_dotenv(override=True)

LOG_FORMAT = os.getenv(
    "LOG_FORMAT",
    "%(asctime)s - [%(otelTraceID)s] %(name)s:%(lineno)d - %(levelname)s - %(message)s",
)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


class TraceIdFilter(logging.Filter):
    def filter(self, record):
        trace_id = request_id_var.get() or ""
        record.trace_id = trace_id
        return True


def setup_logging(level=LOG_LEVEL):
    # Configure logging
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Add the custom filter to all handlers of the root logger
    for handler in logging.getLogger().handlers:
        handler.addFilter(TraceIdFilter())
