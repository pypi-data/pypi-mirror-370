"""DynamoDB repository adapter implementation.

This module provides the concrete implementation of the CustomerRepoPort interface,
handling all persistence operations with DynamoDB for customer link data.

The adapter manages:
    - CRUD operations for Link objects
    - Query operations by API key and customer ID
    - Scanning for metered customers
    - Automatic retry logic for transient failures
    - DateTime serialization/deserialization

Example:
    Basic repository usage::

        import boto3
        from augint_billing_lib.adapters.ddb_repo import DdbRepo
        from augint_billing_lib.models import Link

        # Create repository
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('customer-links')
        repo = DdbRepo(table)

        # Save a link
        link = Link(
            api_key_id="key_123",
            stripe_customer_id="cus_456",
            plan="free"
        )
        repo.save(link)

        # Retrieve by API key
        link = repo.get_by_api_key("key_123")

        # Find all links for a customer
        links = repo.get_by_customer("cus_456")

Table Schema:
    The DynamoDB table should have:
        - Primary Key: api_key_id (String)
        - Global Secondary Index: gsi_stripe_customer
            - Partition Key: stripe_customer_id (String)
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime
from typing import Any

import botocore  # type: ignore[import-untyped]
from boto3.dynamodb.conditions import Key  # type: ignore[import-untyped]

from ..models import Link
from ..utils_retry import retry


class DdbRepo:
    """DynamoDB repository for customer link persistence.

    Implements the CustomerRepoPort interface using DynamoDB as the
    backing store. Handles all CRUD operations with automatic retry
    logic and proper serialization of datetime fields.

    Attributes:
        table: Boto3 DynamoDB Table resource

    Note:
        All operations include automatic retry logic with exponential
        backoff for handling transient DynamoDB errors.
    """

    def __init__(self, table: Any) -> None:
        """Initialize the repository with a DynamoDB table.

        Args:
            table: Boto3 DynamoDB Table resource (from boto3.resource('dynamodb').Table())
        """
        self.table = table

    def _coerce(self, item: dict[str, Any]) -> Link:
        """Convert DynamoDB item to Link object.

        Handles deserialization of datetime fields from ISO format strings
        stored in DynamoDB. Gracefully handles malformed timestamps.

        Args:
            item: Raw item dictionary from DynamoDB

        Returns:
            Link object with properly typed fields
        """
        ts = item.get("last_reported_usage_ts")
        if isinstance(ts, str):
            try:
                item["last_reported_usage_ts"] = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except Exception:
                item["last_reported_usage_ts"] = None
        return Link(**item)

    @retry((botocore.exceptions.ClientError,), tries=5)
    def get_by_api_key(self, api_key_id: str) -> Link:
        """Retrieve a link by API key ID.

        Performs a direct get operation using the primary key.
        This is the most efficient way to retrieve a single link.

        Args:
            api_key_id: The API key to look up

        Returns:
            Link object for the given API key

        Raises:
            KeyError: If the API key is not found in the table
            botocore.exceptions.ClientError: If DynamoDB operation fails after retries

        Example:
            Retrieve and update a link::

                try:
                    link = repo.get_by_api_key("key_abc123")
                    link.plan = "metered"
                    repo.save(link)
                except KeyError:
                    print("API key not found")
        """
        resp = self.table.get_item(Key={"api_key_id": api_key_id})
        if "Item" not in resp:
            raise KeyError(api_key_id)
        return self._coerce(resp["Item"])

    @retry((botocore.exceptions.ClientError,), tries=5)
    def get_by_customer(self, customer_id: str) -> list[Link]:
        """Retrieve all links for a Stripe customer.

        Uses the global secondary index to query all API keys
        belonging to a specific Stripe customer. A customer may
        have multiple API keys.

        Args:
            customer_id: Stripe customer ID (e.g., 'cus_abc123')

        Returns:
            List of Link objects for the customer (may be empty)

        Raises:
            botocore.exceptions.ClientError: If DynamoDB operation fails after retries

        Example:
            Process all API keys for a customer::

                links = repo.get_by_customer("cus_456")
                for link in links:
                    print(f"API Key: {link.api_key_id}, Plan: {link.plan}")
        """
        resp = self.table.query(
            IndexName="gsi_stripe_customer",
            KeyConditionExpression=Key("stripe_customer_id").eq(customer_id),
        )
        return [self._coerce(it) for it in resp.get("Items", [])]

    @retry((botocore.exceptions.ClientError,), tries=5)
    def save(self, link: Link) -> None:
        """Save or update a link in the repository.

        Performs a put operation which will create a new item or
        overwrite an existing one. Handles serialization of datetime
        fields to ISO format strings for DynamoDB storage.

        Args:
            link: Link object to persist

        Raises:
            botocore.exceptions.ClientError: If DynamoDB operation fails after retries

        Example:
            Create or update a link::

                link = Link(
                    api_key_id="key_new",
                    stripe_customer_id="cus_789",
                    plan="metered",
                    metered_subscription_item_id="si_abc"
                )
                repo.save(link)

        Note:
            This operation is not atomic with reads. Use conditional
            expressions if you need optimistic locking.
        """
        item = asdict(link)
        ts = item.get("last_reported_usage_ts")
        if isinstance(ts, datetime):
            item["last_reported_usage_ts"] = ts.astimezone(UTC).isoformat()
        self.table.put_item(Item=item)

    @retry((botocore.exceptions.ClientError,), tries=5)
    def scan_metered(self) -> list[Link]:
        """Retrieve all customers on metered plans.

        Performs a full table scan to find all links where the plan
        is 'metered' and a subscription item ID is present. This is
        used for batch usage reporting operations.

        Returns:
            List of Link objects with plan='metered' and valid subscription item IDs

        Raises:
            botocore.exceptions.ClientError: If DynamoDB operation fails after retries

        Warning:
            This performs a full table scan which can be expensive for
            large tables. Consider using a GSI if this becomes a bottleneck.

        Example:
            Report usage for all metered customers::

                metered_links = repo.scan_metered()
                for link in metered_links:
                    # Process usage for each metered customer
                    usage = get_usage(link.api_key_id)
                    report_to_stripe(link.metered_subscription_item_id, usage)
        """
        resp = self.table.scan()
        out = []
        for it in resp.get("Items", []):
            if it.get("plan") == "metered" and it.get("metered_subscription_item_id"):
                out.append(self._coerce(it))
        return out
