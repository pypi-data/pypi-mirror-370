"""
HTTP utilities for trace ID propagation
"""
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import requests

from .logger import get_logger
from .trace_context import SENTRY_TRACE_HEADER, TRACE_ID_HEADER, get_trace_id

logger = get_logger(__name__)


def add_trace_headers(headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """
    Add trace ID headers to existing headers dict.

    Args:
        headers: Existing headers dict (optional)

    Returns:
        Headers dict with trace ID headers added
    """
    if headers is None:
        headers = {}
    else:
        headers = headers.copy()

    trace_id = get_trace_id()
    if trace_id:
        headers[TRACE_ID_HEADER] = trace_id
        # Add Sentry trace format if needed
        # Format: {trace_id}-{span_id}-{sampled}
        headers[SENTRY_TRACE_HEADER] = f"{trace_id}-{trace_id[:16]}-1"

    return headers


class TracedSession(requests.Session):
    """
    A requests Session that automatically adds trace headers to all requests.
    """

    def request(self, method, url, **kwargs):
        """Override request to add trace headers"""
        kwargs["headers"] = add_trace_headers(kwargs.get("headers"))

        trace_id = get_trace_id()
        logger.debug(
            "Making HTTP request",
            extra={
                "method": method,
                "url": url,
                "trace_id": trace_id,
                "host": urlparse(url).netloc,
            },
        )

        return super().request(method, url, **kwargs)


def traced_request(method: str, url: str, **kwargs) -> requests.Response:
    """
    Make an HTTP request with trace headers automatically added.

    This is a drop-in replacement for requests.request() that adds trace headers.

    Args:
        method: HTTP method (GET, POST, etc.)
        url: URL to request
        **kwargs: Additional arguments passed to requests.request()

    Returns:
        requests.Response object
    """
    kwargs["headers"] = add_trace_headers(kwargs.get("headers"))

    trace_id = get_trace_id()
    logger.debug(
        "Making traced HTTP request",
        extra={
            "method": method,
            "url": url,
            "trace_id": trace_id,
            "host": urlparse(url).netloc,
        },
    )

    return requests.request(method, url, **kwargs)


# Convenience methods that mirror requests API
def get(url: str, **kwargs) -> requests.Response:
    """GET request with trace headers"""
    return traced_request("GET", url, **kwargs)


def post(url: str, **kwargs) -> requests.Response:
    """POST request with trace headers"""
    return traced_request("POST", url, **kwargs)


def put(url: str, **kwargs) -> requests.Response:
    """PUT request with trace headers"""
    return traced_request("PUT", url, **kwargs)


def patch(url: str, **kwargs) -> requests.Response:
    """PATCH request with trace headers"""
    return traced_request("PATCH", url, **kwargs)


def delete(url: str, **kwargs) -> requests.Response:
    """DELETE request with trace headers"""
    return traced_request("DELETE", url, **kwargs)


def head(url: str, **kwargs) -> requests.Response:
    """HEAD request with trace headers"""
    return traced_request("HEAD", url, **kwargs)
