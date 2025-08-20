"""API Gateway administration adapter implementation.

This module provides the concrete implementation of the PlanAdminPort interface,
managing API key assignments to usage plans in AWS API Gateway.

The adapter handles:
    - Moving API keys between usage plans
    - Removing keys from existing plans
    - Ensuring atomic plan transitions
    - Automatic retry logic for transient failures

Example:
    Basic plan administration::

        import boto3
        from augint_billing_lib.adapters.apigw_admin import ApiGwAdmin

        # Create adapter
        client = boto3.client('apigateway')
        admin = ApiGwAdmin(
            apigw_client=client,
            free_plan_id="plan_free_123",
            metered_plan_id="plan_metered_456"
        )

        # Move API key to metered plan
        admin.move_key_to_plan(
            api_key_id="key_abc",
            target_plan_id="plan_metered_456"
        )

Note:
    API keys can only belong to one usage plan at a time. This adapter
    ensures atomic transitions by removing from the old plan before
    adding to the new one.
"""

from __future__ import annotations

from typing import Any

import botocore  # type: ignore[import-untyped]

from ..utils_retry import retry


class ApiGwAdmin:
    """API Gateway usage plan administration adapter.

    Implements the PlanAdminPort interface for managing API key assignments
    to usage plans. This controls rate limiting and quota enforcement for
    API keys based on their billing tier.

    Attributes:
        apigw: Boto3 API Gateway client for AWS API calls
        free_plan_id: Usage plan ID for the free tier
        metered_plan_id: Usage plan ID for the metered/paid tier

    Note:
        All operations include automatic retry logic for handling
        transient AWS API errors.
    """

    def __init__(self, apigw_client: Any, free_plan_id: str, metered_plan_id: str) -> None:
        """Initialize the admin adapter with plan configuration.

        Args:
            apigw_client: Boto3 API Gateway client (from boto3.client('apigateway'))
            free_plan_id: Usage plan ID for free tier (e.g., 'plan_free_123')
            metered_plan_id: Usage plan ID for metered tier (e.g., 'plan_metered_456')

        Example:
            Create admin with discovered plan IDs::

                import boto3

                client = boto3.client('apigateway')

                # Discover plan IDs
                plans = client.get_usage_plans()
                free_id = None
                metered_id = None

                for plan in plans['items']:
                    if plan['name'] == 'FREE_10K':
                        free_id = plan['id']
                    elif plan['name'] == 'METERED':
                        metered_id = plan['id']

                # Create admin
                admin = ApiGwAdmin(client, free_id, metered_id)
        """
        self.apigw = apigw_client
        self.free_plan_id = free_plan_id
        self.metered_plan_id = metered_plan_id

    @retry((botocore.exceptions.ClientError,), tries=5)
    def _remove_from_plan(self, usage_plan_id: str, api_key_id: str) -> None:
        """Remove an API key from a usage plan.

        Internal method that searches for the API key in the specified
        usage plan and removes it if found. This is a no-op if the key
        is not in the plan.

        Args:
            usage_plan_id: The usage plan to remove from
            api_key_id: The API key value to remove

        Note:
            Uses pagination to handle plans with many keys.
            The key 'value' is matched, not the key 'id'.
        """
        pager = self.apigw.get_paginator("get_usage_plan_keys")
        for page in pager.paginate(usagePlanId=usage_plan_id, limit=500):
            for k in page.get("items", []):
                if k.get("value") == api_key_id:
                    self.apigw.delete_usage_plan_key(usagePlanId=usage_plan_id, keyId=k["id"])

    @retry((botocore.exceptions.ClientError,), tries=5)
    def move_key_to_plan(self, api_key_id: str, target_plan_id: str) -> None:
        """Move an API key to a different usage plan.

        Atomically moves an API key from its current usage plan (if any)
        to the target usage plan. This method ensures the key is removed
        from the other plan before adding to the target.

        Args:
            api_key_id: The API key value to move (e.g., 'abc123xyz')
            target_plan_id: The target usage plan ID

        Raises:
            botocore.exceptions.ClientError: If the operation fails after retries

        Example:
            Promote a key to metered plan::

                # Move from free to metered
                admin.move_key_to_plan(
                    api_key_id="key_abc123",
                    target_plan_id=admin.metered_plan_id
                )

            Demote a key to free plan::

                # Move from metered to free
                admin.move_key_to_plan(
                    api_key_id="key_abc123",
                    target_plan_id=admin.free_plan_id
                )

        Note:
            This method assumes the key is in one of the two configured
            plans (free or metered). It removes from the opposite plan
            before adding to the target.

        Warning:
            API Gateway has eventual consistency. There may be a brief
            moment where the key is not in any plan during the transition.
        """
        other = self.metered_plan_id if target_plan_id == self.free_plan_id else self.free_plan_id
        self._remove_from_plan(other, api_key_id)
        self.apigw.create_usage_plan_key(
            usagePlanId=target_plan_id, keyId=api_key_id, keyType="API_KEY"
        )
