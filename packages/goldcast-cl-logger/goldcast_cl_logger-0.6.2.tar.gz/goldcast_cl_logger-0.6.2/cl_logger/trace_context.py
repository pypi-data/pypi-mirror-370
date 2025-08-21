"""
Trace context management for distributed tracing
"""
import contextvars
import uuid
from typing import Any, Dict, Optional

# Context variable to store the current trace ID
_trace_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "trace_id", default=None
)

# Context variable to store additional trace metadata
_trace_metadata_var: contextvars.ContextVar[Dict[str, Any]] = contextvars.ContextVar(
    "trace_metadata", default={}
)

TRACE_ID_HEADER = "X-Trace-Id"
SENTRY_TRACE_HEADER = "sentry-trace"


def generate_trace_id() -> str:
    """Generate a new trace ID"""
    return str(uuid.uuid4())


def get_trace_id() -> Optional[str]:
    """Get the current trace ID from context"""
    return _trace_id_var.get()


def set_trace_id(trace_id: str) -> None:
    """Set the trace ID in context"""
    _trace_id_var.set(trace_id)


def get_trace_metadata() -> Dict[str, Any]:
    """Get additional trace metadata"""
    return _trace_metadata_var.get().copy()


def set_trace_metadata(metadata: Dict[str, Any]) -> None:
    """Set additional trace metadata"""
    _trace_metadata_var.set(metadata)


def add_trace_metadata(key: str, value: Any) -> None:
    """Add a single metadata item to trace context"""
    metadata = get_trace_metadata()
    metadata[key] = value
    set_trace_metadata(metadata)


class TraceContext:
    """Context manager for trace ID handling"""

    def __init__(self, trace_id: Optional[str] = None):
        self.trace_id = trace_id or generate_trace_id()
        self.token = None
        self.metadata_token = None

    def __enter__(self):
        self.token = _trace_id_var.set(self.trace_id)
        self.metadata_token = _trace_metadata_var.set({})
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.token:
            _trace_id_var.reset(self.token)
        if self.metadata_token:
            _trace_metadata_var.reset(self.metadata_token)
