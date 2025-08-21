"""Logging and metrics utilities for the billing system.

This module provides structured logging and CloudWatch metrics support for
the billing library. It uses JSON formatting for structured logs and supports
AWS Embedded Metrics Format (EMF) for CloudWatch metrics.

The logging system provides:
    - Structured JSON logging for better searchability
    - CloudWatch EMF metrics for monitoring
    - Configurable log levels via environment variables
    - Automatic timestamp and namespace handling

Example:
    Basic logging and metrics::

        from augint_billing_lib.logging import log_event, log_metric

        # Log a billing event
        log_event(
            "info",
            "payment_processed",
            customer_id="cus_123",
            amount=50.00,
            currency="USD"
        )

        # Record a metric
        log_metric(
            "UsageReported",
            1500,
            dims={"CustomerTier": "metered", "Region": "us-east-1"}
        )

Environment Variables:
    LOG_LEVEL: Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
               Defaults to INFO if not set.

Note:
    This module is designed for use in AWS Lambda environments where
    stdout is captured and processed by CloudWatch Logs.
"""

import json
import logging
import os
from typing import Any

# Configure module logger
_logger = logging.getLogger("augint.billing")
if not _logger.handlers:
    h = logging.StreamHandler()
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    h.setFormatter(fmt)
    _logger.addHandler(h)
    _logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))


def log_event(level: str, msg: str, **kv: Any) -> None:
    """Log a structured event with optional key-value pairs.

    Creates a JSON-formatted log entry with a message and arbitrary
    key-value pairs for structured logging. This format is ideal for
    log aggregation and searching in CloudWatch Logs Insights.

    Args:
        level: Log level (debug, info, warning, error, critical)
        msg: Primary message describing the event
        **kv: Additional key-value pairs to include in the log entry

    Example:
        Log a payment event::

            log_event(
                "info",
                "stripe_payment_succeeded",
                customer_id="cus_123",
                amount=99.99,
                subscription_id="sub_456",
                timestamp="2024-01-15T10:30:00Z"
            )

        Log an error with context::

            log_event(
                "error",
                "usage_reporting_failed",
                customer_id="cus_789",
                error_type="RateLimitError",
                retry_count=3,
                will_retry=True
            )

    Note:
        The entire log entry is JSON-encoded for structured logging.
        This makes it easy to query in CloudWatch Logs Insights:

        fields @timestamp, msg, customer_id, amount
        | filter msg = "stripe_payment_succeeded"
        | stats sum(amount) by customer_id
    """
    rec = {"msg": msg, **kv}
    getattr(_logger, level.lower(), _logger.info)(json.dumps(rec))


def log_metric(name: str, value: float, dims: dict[str, str] | None = None) -> None:
    """Log a CloudWatch metric using Embedded Metrics Format (EMF).

    Creates a metric that will be automatically extracted by CloudWatch
    when running in AWS Lambda or ECS environments. The metric appears
    in CloudWatch Metrics under the "AugInt/Billing" namespace.

    Args:
        name: Metric name (e.g., "UsageReported", "PaymentProcessed")
        value: Numeric value for the metric
        dims: Optional dimensions for metric filtering and aggregation

    Example:
        Log usage reporting metrics::

            # Simple counter metric
            log_metric("UsageReportsProcessed", 5)

            # Metric with dimensions for filtering
            log_metric(
                "APICallsReported",
                10000,
                dims={
                    "CustomerTier": "metered",
                    "Region": "us-east-1",
                    "ReportingWindow": "hourly"
                }
            )

            # Track payment amounts
            log_metric(
                "PaymentAmount",
                99.99,
                dims={"Currency": "USD", "PaymentMethod": "card"}
            )

    CloudWatch Queries:
        Once logged, metrics can be queried in CloudWatch:

        - View in CloudWatch Metrics under "AugInt/Billing" namespace
        - Create alarms on metric thresholds
        - Build dashboards for monitoring
        - Use CloudWatch Insights for analysis

    Note:
        EMF metrics are extracted asynchronously by CloudWatch and may
        take a few minutes to appear in the Metrics console. The raw
        EMF JSON is immediately available in CloudWatch Logs.

    Warning:
        Keep dimension cardinality reasonable. High cardinality dimensions
        (like customer_id with thousands of values) can increase CloudWatch
        costs significantly.
    """
    # AWS EMF-compatible payload
    payload = {
        "_aws": {
            "Timestamp": int(__import__("time").time() * 1000),
            "CloudWatchMetrics": [
                {
                    "Namespace": "AugInt/Billing",
                    "Dimensions": [list((dims or {}).keys())],
                    "Metrics": [{"Name": name, "Unit": "Count"}],
                }
            ],
        },
        name: value,
    }
    if dims:
        payload.update(dims)
    _logger.info(json.dumps(payload))
