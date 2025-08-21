"""
CL Logger - A lightweight logging library for Content Lab projects with
distributed tracing support
"""

import logging

from . import http_utils, sqs_utils
from .logger import CLLogger, get_logger
from .trace_context import (
    SENTRY_TRACE_HEADER,
    TRACE_ID_HEADER,
    TraceContext,
    add_trace_metadata,
    generate_trace_id,
    get_trace_id,
    get_trace_metadata,
    set_trace_id,
    set_trace_metadata,
)

# Re-export logging level constants for convenience
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

__version__ = "0.6.2"
__all__ = [
    "CLLogger",
    "get_logger",
    "TraceContext",
    "get_trace_id",
    "set_trace_id",
    "generate_trace_id",
    "get_trace_metadata",
    "set_trace_metadata",
    "add_trace_metadata",
    "TRACE_ID_HEADER",
    "SENTRY_TRACE_HEADER",
    "http_utils",
    "sqs_utils",
    # Logging levels
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
]
