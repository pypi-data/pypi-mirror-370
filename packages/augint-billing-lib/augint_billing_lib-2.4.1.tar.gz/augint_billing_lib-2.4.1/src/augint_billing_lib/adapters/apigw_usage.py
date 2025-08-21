"""API Gateway usage data adapter implementation.

This module provides the concrete implementation of the UsageSourcePort interface,
fetching API usage metrics from AWS API Gateway for billing purposes.

The adapter handles:
    - Retrieving usage data for specific API keys
    - Aggregating usage across multiple stages and days
    - Automatic retry logic for transient failures
    - Date range queries for usage windows

Example:
    Basic usage retrieval::

        import boto3
        from datetime import datetime, timedelta
        from augint_billing_lib.adapters.apigw_usage import ApiGwUsage

        # Create adapter
        client = boto3.client('apigateway')
        usage_adapter = ApiGwUsage(client)

        # Get usage for last hour
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)

        usage = usage_adapter.get_usage(
            usage_plan_id="METERED",
            api_key_id="key_123",
            since=hour_ago,
            until=now
        )

        if usage:
            print(f"API calls in last hour: {usage}")

Note:
    API Gateway aggregates usage data at the day level, so queries
    for partial days will return the full day's usage. Plan your
    reporting windows accordingly.
"""

from __future__ import annotations

import contextlib
from datetime import datetime
from typing import Any

import botocore  # type: ignore[import-untyped]

from ..utils_retry import retry


class ApiGwUsage:
    """API Gateway usage data retrieval adapter.

    Implements the UsageSourcePort interface for fetching usage metrics
    from AWS API Gateway. This adapter is used to collect API call counts
    for usage-based billing.

    Attributes:
        apigw: Boto3 API Gateway client for AWS API calls

    Note:
        All operations include automatic retry logic for handling
        transient AWS API errors.
    """

    def __init__(self, apigw_client: Any) -> None:
        """Initialize the usage adapter with an API Gateway client.

        Args:
            apigw_client: Boto3 API Gateway client (from boto3.client('apigateway'))
        """
        self.apigw = apigw_client

    @retry((botocore.exceptions.ClientError,), tries=5)
    def get_usage(
        self, usage_plan_id: str, api_key_id: str, since: datetime, until: datetime
    ) -> int | None:
        """Get API usage for a specific key within a time window.

        Retrieves the total number of API calls made by a specific API key
        within the given time window. The API Gateway GetUsage API returns
        data aggregated by day, so this method sums all usage across the
        date range.

        Args:
            usage_plan_id: The usage plan ID (e.g., 'FREE_10K', 'METERED')
            api_key_id: The API key to get usage for
            since: Start of the time window (inclusive)
            until: End of the time window (exclusive)

        Returns:
            Total number of API calls, or None if no usage data available

        Raises:
            botocore.exceptions.ClientError: If API Gateway query fails after retries

        Example:
            Get usage for a specific time window::

                from datetime import datetime, timedelta

                # Get usage for the last 24 hours
                now = datetime.utcnow()
                yesterday = now - timedelta(days=1)

                usage = adapter.get_usage(
                    usage_plan_id="METERED",
                    api_key_id="key_abc123",
                    since=yesterday,
                    until=now
                )

                if usage is not None:
                    print(f"Total API calls: {usage}")
                else:
                    print("No usage data available")

        Note:
            The API Gateway GetUsage API has these characteristics:
            - Returns data aggregated by day
            - May have a delay of up to a few minutes for recent data
            - Returns data grouped by API stage
            - Includes all HTTP methods and resources

        Warning:
            Be aware that API Gateway aggregates at the day level. If you
            query for a partial day (e.g., 10:00 to 11:00), you'll get
            the entire day's usage. Design your billing windows accordingly.
        """
        start = since.date().isoformat()
        end = until.date().isoformat()
        resp = self.apigw.get_usage(
            usagePlanId=usage_plan_id, keyId=api_key_id, startDate=start, endDate=end
        )
        total = 0
        for _stage, days in (resp.get("values") or {}).items():
            for day in days:
                for _k, v in day.items():
                    with contextlib.suppress(Exception):
                        total += int(v)
        return total
