import logging
import sys

from ddtrace import tracer
from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def format(self, record):
        span = tracer.current_span()
        record.dd = (
            record.dd if hasattr(record, "dd") and isinstance(record.dd, dict) else {}
        )

        if span:
            record.dd["trace_id"] = (
                str(span.trace_id & 0xFFFFFFFFFFFFFFFF) if span.trace_id else "0"
            )
            record.dd["span_id"] = str(span.span_id) if span.span_id else "0"
        else:
            record.dd["trace_id"] = "0"
            record.dd["span_id"] = "0"
        return super().format(record)


def setup_initial_logging() -> None:
    formatter = CustomJsonFormatter("%(asctime)s %(levelname)s - %(message)s")

    h_stdout = logging.StreamHandler(sys.stdout)
    h_stdout.setLevel(logging.INFO)
    h_stdout.addFilter(lambda record: record.levelno < logging.ERROR)
    h_stdout.setFormatter(formatter)

    h_stderr = logging.StreamHandler(sys.stderr)
    h_stderr.setLevel(logging.ERROR)
    h_stderr.setFormatter(formatter)
    handlers = [h_stdout, h_stderr]

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # ✅ Ensure handlers are added only once
    if not root_logger.handlers:
        root_logger.handlers = handlers

    # ✅ Enable propagation so all module loggers inherit settings
    root_logger.propagate = True


def setup_logging_with_excluded_endpoints(params: dict) -> None:
    """
    Set up logging to exclude specific endpoints.

    Args:
        params: A dictionary containing configuration parameters, including 'excluded_endpoints'.
    """

    class EndpointFilter(logging.Filter):
        """Filter class to exclude specific endpoints from log entries."""

        def __init__(self, excluded_endpoints: list[str]) -> None:
            """
            Initialize the EndpointFilter class.

            Args:
                excluded_endpoints: A list of endpoints to be excluded from log entries.
            """
            super().__init__()
            self.excluded_endpoints = excluded_endpoints

        def filter(self, record: logging.LogRecord) -> bool:
            """
            Filter out log entries for excluded endpoints.

            Args:
                record: The log record to be filtered.

            Returns:
                bool: True if the log entry should be included, False otherwise.
            """
            return (
                record.args
                and len(record.args) >= 3
                and record.args[2] not in self.excluded_endpoints
            )

    # Get excluded_endpoints from params
    excluded_endpoints = params.get("excluded_endpoints", [])

    # Add filter to the logger
    logging.getLogger("uvicorn.access").addFilter(EndpointFilter(excluded_endpoints))
