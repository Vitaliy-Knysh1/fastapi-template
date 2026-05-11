from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram

HTTP_REQUESTS_TOTAL = Counter(
    "luckygames_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "luckygames_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
)

PURCHASE_TOTAL_UAH_SUM = Gauge(
    "luckygames_purchase_total_uah_sum",
    "Sum of totals (UAH) across all completed purchases",
)

PURCHASES_TOTAL = Counter(
    "luckygames_purchases_total",
    "Number of completed purchases",
)


def record_purchase_total(*, total_cents: int) -> None:
    PURCHASES_TOTAL.inc()
    PURCHASE_TOTAL_UAH_SUM.inc(total_cents / 100.0)
