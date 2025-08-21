"""Dependency injection and Lambda handler setup.

This module provides the bootstrap layer that wires together all the components
of the billing system. It handles environment configuration, AWS resource discovery,
and provides high-level entry points for Lambda handlers.

The bootstrap module is responsible for:
    - Discovering AWS resources (DynamoDB tables, API Gateway plans)
    - Loading configuration from environment variables and Secrets Manager
    - Building the BillingService with all required dependencies
    - Providing Lambda-ready handler functions

Example:
    Lambda handler for Stripe events::

        import json
        from augint_billing_lib import bootstrap

        def lambda_handler(event, context):
            # Process Stripe event from EventBridge
            result = bootstrap.process_event_and_apply_plan_moves(event)
            return {
                'statusCode': 200,
                'body': json.dumps(result)
            }

    Lambda handler for usage reporting::

        from augint_billing_lib import bootstrap

        def lambda_handler(event, context):
            # Report usage for the current hour
            reports = bootstrap.report_current_hour_usage()
            return {
                'statusCode': 200,
                'body': json.dumps({'reported': len(reports)})
            }

Environment Variables:
    Required:
        - AWS_REGION: AWS region for resources
        - STACK_NAME: CloudFormation stack name
        - STRIPE_SECRET_KEY or STRIPE_SECRET_ARN: Stripe authentication

    Optional:
        - TABLE_NAME: DynamoDB table name (defaults to discovery)
        - FREE_USAGE_PLAN_ID: Override for free tier plan ID
        - METERED_USAGE_PLAN_ID: Override for metered tier plan ID
        - API_USAGE_PRODUCT_ID: Stripe product ID for usage
        - STRIPE_PRICE_ID_METERED: Stripe price ID for metered billing
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from typing import Any

import boto3  # type: ignore[import-untyped]
import stripe

from .adapters.apigw_admin import ApiGwAdmin
from .adapters.apigw_usage import ApiGwUsage
from .adapters.ddb_repo import DdbRepo
from .adapters.stripe import StripeAdapter
from .logging import log_event
from .service import BillingService


def _cfn_outputs(stack_name: str, region: str) -> dict[str, str]:
    """Retrieve CloudFormation stack outputs.

    Fetches all outputs from a CloudFormation stack, which may contain
    resource IDs and configuration values needed by the billing system.

    Args:
        stack_name: Name of the CloudFormation stack
        region: AWS region where the stack is deployed

    Returns:
        Dictionary mapping output keys to their values

    Note:
        Returns empty dict if stack doesn't exist or has no outputs
    """
    cfn = boto3.client("cloudformation", region_name=region)
    try:
        resp = cfn.describe_stacks(StackName=stack_name)
        stacks = resp.get("Stacks", [])
        outputs = stacks[0].get("Outputs", []) if stacks else []
        return {
            o["OutputKey"]: o["OutputValue"]
            for o in outputs
            if "OutputKey" in o and "OutputValue" in o
        }
    except Exception:
        return {}


def _discover_table_name(stack_name: str, region: str) -> str:
    """Discover or retrieve the DynamoDB table name.

    Attempts to find the table name from (in order):
        1. CloudFormation stack outputs
        2. TABLE_NAME environment variable
        3. Default value 'customer_links'

    Args:
        stack_name: CloudFormation stack name to check for outputs
        region: AWS region for the stack

    Returns:
        DynamoDB table name

    Raises:
        AssertionError: If no table name can be determined
    """
    out = _cfn_outputs(stack_name, region)
    table_name = out.get("TableName") or os.getenv("TABLE_NAME", "customer_links")
    assert table_name is not None
    return table_name


def _discover_usage_plan_ids(region: str) -> dict[str, str]:
    """Discover API Gateway usage plan IDs.

    Searches for usage plans named 'FREE_10K' and 'METERED' in API Gateway.
    Can be overridden with environment variables FREE_USAGE_PLAN_ID and
    METERED_USAGE_PLAN_ID.

    Args:
        region: AWS region to search for usage plans

    Returns:
        Dictionary with keys 'FREE_10K' and 'METERED' mapping to plan IDs

    Note:
        May return partial results if only some plans are found
    """
    apigw = boto3.client("apigateway", region_name=region)
    plans = apigw.get_usage_plans(limit=500).get("items", [])
    found = {}
    for p in plans:
        n = p.get("name", "")
        if n == "FREE_10K":
            found["FREE_10K"] = p.get("id")
        if n == "METERED":
            found["METERED"] = p.get("id")
    free_override = os.getenv("FREE_USAGE_PLAN_ID")
    meter_override = os.getenv("METERED_USAGE_PLAN_ID")
    if free_override:
        found["FREE_10K"] = free_override
    if meter_override:
        found["METERED"] = meter_override
    return found


def _stripe_from_env_or_secret() -> tuple[str, str | None]:
    """Load Stripe configuration from environment or Secrets Manager.

    Attempts to load Stripe API key and price ID from:
        1. AWS Secrets Manager (if STRIPE_SECRET_ARN is set)
        2. Environment variables (STRIPE_SECRET_KEY, STRIPE_PRICE_ID_METERED)

    Returns:
        Tuple of (secret_key, metered_price_id)
        Price ID may be None if not configured

    Raises:
        KeyError: If STRIPE_SECRET_KEY is not found in environment
    """
    arn = os.getenv("STRIPE_SECRET_ARN")
    region = os.getenv("AWS_REGION")
    if arn and region:
        sm = boto3.client("secretsmanager", region_name=region)
        blob = sm.get_secret_value(SecretId=arn).get("SecretString") or "{}"
        cfg = json.loads(blob)
        return cfg["STRIPE_SECRET_KEY"], cfg.get("STRIPE_PRICE_ID_METERED")
    return os.environ["STRIPE_SECRET_KEY"], os.getenv("STRIPE_PRICE_ID_METERED")


def build_service(include_usage: bool = True) -> BillingService:
    """Build a fully configured BillingService instance.

    This is the main factory function that creates a BillingService with
    all dependencies wired based on the environment configuration. It:
        1. Discovers AWS resources (DynamoDB table, API Gateway plans)
        2. Loads Stripe configuration
        3. Creates all adapter instances
        4. Wires everything into a BillingService

    Args:
        include_usage: Whether to include the usage source port.
            Set to False for event processing (doesn't need usage data).
            Set to True for usage reporting workflows.

    Returns:
        Configured BillingService ready for use

    Raises:
        KeyError: If required environment variables are missing
        AssertionError: If required resources cannot be found

    Example:
        Build service for event processing::

            service = build_service(include_usage=False)
            result = service.handle_stripe_event(event)

        Build service for usage reporting::

            service = build_service(include_usage=True)
            reports = service.reconcile_usage_window(since, until)
    """
    region = os.environ["AWS_REGION"]
    stack = os.environ["STACK_NAME"]
    table = _discover_table_name(stack, region)

    ddb = boto3.resource("dynamodb", region_name=region)
    repo = DdbRepo(ddb.Table(table))
    usage = ApiGwUsage(boto3.client("apigateway", region_name=region)) if include_usage else None

    sk, price = _stripe_from_env_or_secret()
    stripe.api_key = sk
    stripe_adapter = StripeAdapter(
        secret_key=sk,
        metered_price_id=price
        or StripeAdapter(secret_key=sk).discover_metered_price_id(
            os.getenv("API_USAGE_PRODUCT_ID")
        ),
    )

    # Wire optional plan_admin
    plans = _discover_usage_plan_ids(region)
    plan_admin = None
    if plans.get("FREE_10K") and plans.get("METERED"):
        plan_admin = ApiGwAdmin(
            boto3.client("apigateway", region_name=region),
            free_plan_id=plans["FREE_10K"],
            metered_plan_id=plans["METERED"],
        )

    return BillingService(repo=repo, stripe=stripe_adapter, usage=usage, plan_admin=plan_admin)


def process_event_and_apply_plan_moves(evt: dict[str, Any]) -> dict[str, Any]:
    """Process a Stripe event and apply resulting plan changes.

    This is the main Lambda handler entry point for processing Stripe events.
    It combines event processing with plan moves in a single operation:
        1. Processes the Stripe event to determine target plan
        2. Applies the plan change to all affected API keys
        3. Updates the database with new plan status

    Args:
        evt: Stripe event, either raw or wrapped in EventBridge format

    Returns:
        Dictionary containing:
            - target_plan: The plan customers were moved to ('free' or 'metered')
            - moved: Number of API keys that were moved
            - stripe_customer_id: The affected customer
            - ignored: True if event was ignored
            - reason: Reason for ignoring (if ignored)
            - error: Error type (if failed)

    Example:
        Lambda handler implementation::

            def lambda_handler(event, context):
                result = bootstrap.process_event_and_apply_plan_moves(event)

                if result.get('error'):
                    return {
                        'statusCode': 500,
                        'body': json.dumps({'error': result['error']})
                    }

                return {
                    'statusCode': 200,
                    'body': json.dumps(result)
                }
    """
    region = os.environ["AWS_REGION"]
    svc = build_service(include_usage=False)
    action = svc.handle_stripe_event(evt)

    target = action.get("target_plan")
    customer_id = action.get("stripe_customer_id")
    subitem = action.get("subscription_item_id")

    if not target or not customer_id:
        return {"ignored": True, "reason": action.get("reason")}

    plan_ids = _discover_usage_plan_ids(region)
    free_id = plan_ids.get("FREE_10K")
    meter_id = plan_ids.get("METERED")
    if not (free_id and meter_id):
        log_event("error", "missing_usage_plans", details=plan_ids)
        return {"error": "missing_usage_plans", "details": plan_ids}

    moved = svc.apply_plan_move_for_customer(customer_id, target, subitem, free_id, meter_id)
    return {"target_plan": target, "moved": moved, "stripe_customer_id": customer_id}


def report_current_hour_usage() -> list[dict[str, Any]]:
    """Report usage for the current hour to Stripe.

    Convenience function that reports usage from the start of the current
    hour until now. Typically called by a scheduled Lambda function.

    Returns:
        List of usage reports created, each containing:
            - api_key_id: The API key that generated usage
            - customer_id: Stripe customer ID
            - units: Number of units reported
            - until: End timestamp of the reporting window

    Example:
        Scheduled Lambda handler::

            def lambda_handler(event, context):
                reports = bootstrap.report_current_hour_usage()

                print(f"Reported usage for {len(reports)} customers")

                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'reported': len(reports),
                        'reports': reports
                    })
                }
    """
    now = datetime.now(UTC)
    hour_start = now.replace(minute=0, second=0, microsecond=0)

    service = build_service(include_usage=True)
    return service.reconcile_usage_window(hour_start, now)


def report_usage_window(since: datetime, until: datetime) -> list[dict[str, Any]]:
    """Report usage for a specific time window to Stripe.

    Reports API usage for all metered customers within the specified
    time window. This is useful for backfilling or custom reporting periods.

    Args:
        since: Start of the usage window (inclusive)
        until: End of the usage window (exclusive)

    Returns:
        List of usage reports created

    Example:
        Report usage for the last 24 hours::

            from datetime import datetime, timedelta, timezone

            now = datetime.now(timezone.utc)
            yesterday = now - timedelta(days=1)

            reports = bootstrap.report_usage_window(yesterday, now)
            print(f"Reported {sum(r['units'] for r in reports)} total units")
    """
    service = build_service(include_usage=True)
    return service.reconcile_usage_window(since, until)
