"""Prometheus metrics instrumentation for the Bookshelf API."""

from prometheus_client import Counter, Histogram, generate_latest
from starlette.requests import Request
from starlette.responses import Response

# ---------------------------------------------------------------------------
# Metric definitions
# ---------------------------------------------------------------------------

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"],
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

BOOKS_TOTAL = Counter(
    "books_created_total",
    "Total number of books created",
)


# ---------------------------------------------------------------------------
# Metrics endpoint
# ---------------------------------------------------------------------------


async def metrics_endpoint(_request: Request) -> Response:
    """Expose Prometheus metrics at /metrics."""
    return Response(
        content=generate_latest(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )
