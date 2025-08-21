"""Core billing service orchestration.

This module contains the main business logic for the billing system, orchestrating
interactions between Stripe, AWS API Gateway, and the customer repository. The
BillingService class is the central coordinator that implements the billing workflows.

The service handles three main workflows:
    1. Stripe event processing - React to payment events and update plan status
    2. Usage reporting - Report API usage to Stripe for metered billing
    3. Plan management - Direct promotion/demotion of customers

Example:
    Basic service usage::

        from augint_billing_lib.service import BillingService
        from augint_billing_lib.adapters import (
            StripeAdapter, DynamoDBRepoAdapter,
            APIGatewayUsageAdapter, APIGatewayAdminAdapter
        )

        # Create service with all dependencies
        service = BillingService(
            repo=DynamoDBRepoAdapter(table_name="billing-links"),
            stripe=StripeAdapter(api_key="sk_test_..."),
            usage=APIGatewayUsageAdapter(),
            plan_admin=APIGatewayAdminAdapter()
        )

        # Handle a Stripe webhook event
        result = service.handle_stripe_event({
            "type": "payment_method.attached",
            "data": {"object": {"customer": "cus_123"}}
        })

        # Report usage for the last hour
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        reports = service.reconcile_usage_window(hour_ago, now)
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .logging import log_event, log_metric
from .ports import CustomerRepoPort, PlanAdminPort, StripePort, UsageSourcePort


class BillingService:
    """Orchestrates billing operations between Stripe and AWS services.

    The BillingService is the core business logic component that coordinates
    all billing operations. It processes Stripe events, manages plan transitions,
    reports usage, and handles customer promotions/demotions.

    The service is designed to be:
        - Stateless - All state is stored in the repository
        - Idempotent - Safe to retry operations
        - Testable - Dependencies injected via ports
        - Cloud-agnostic - No direct AWS/Stripe dependencies

    Attributes:
        repo: Customer repository for persisting link data
        stripe: Stripe operations port for payment processing
        usage: Optional usage source for API Gateway metrics
        plan_admin: Optional plan administration for moving API keys
    """

    def __init__(
        self,
        repo: CustomerRepoPort,
        stripe: StripePort,
        usage: UsageSourcePort | None = None,
        plan_admin: PlanAdminPort | None = None,
    ):
        """Initialize the billing service with required dependencies.

        Args:
            repo: Customer repository for data persistence
            stripe: Stripe port for payment operations
            usage: Optional port for fetching usage data (required for reconcile_usage_window)
            plan_admin: Optional port for API key plan management
                (required for apply_plan_move_for_customer)
        """
        self.repo = repo
        self.stripe = stripe
        self.usage = usage
        self.plan_admin = plan_admin

    # --- Event handling ---
    def handle_stripe_event(self, evt: dict[str, Any]) -> dict[str, Any]:
        """Process a Stripe webhook event and determine the target plan.

        This method is the main entry point for processing Stripe events. It analyzes
        the event type and customer payment status to determine whether the customer
        should be on the free or metered plan.

        Supported events:
            - payment_method.attached: Customer adds a payment method
            - setup_intent.succeeded: Payment setup completed
            - customer.subscription.created/updated: Subscription changes
            - invoice.payment_failed: Payment failure

        Args:
            evt: Stripe event dictionary, either raw or wrapped in EventBridge format

        Returns:
            Dictionary containing:
                - target_plan: 'free', 'metered', or None if no action needed
                - stripe_customer_id: Customer ID from the event
                - subscription_item_id: ID for usage reporting (metered plan only)
                - reason: Event type or reason for the decision

        Example:
            Processing a payment method attachment::

                result = service.handle_stripe_event({
                    "type": "payment_method.attached",
                    "data": {
                        "object": {
                            "customer": "cus_123",
                            "type": "card"
                        }
                    }
                })
                # Returns: {
                #     "target_plan": "metered",
                #     "stripe_customer_id": "cus_123",
                #     "subscription_item_id": "si_abc",
                #     "reason": "payment_method.attached"
                # }
        """
        detail = evt.get("detail", evt)
        etype = detail.get("type")
        data = detail.get("data") or {}
        obj = data.get("object") or {}
        customer_id = obj.get("customer") or data.get("object", {}).get("customer")

        if not customer_id:
            log_event("warning", "stripe_event_missing_customer", event_type=etype or "unknown")
            return {"target_plan": None, "reason": "no_customer_in_event"}

        if etype in (
            "payment_method.attached",
            "setup_intent.succeeded",
            "customer.subscription.created",
            "customer.subscription.updated",
        ):
            if self.stripe.has_default_payment_method(customer_id):
                sub_item_id = self.stripe.ensure_metered_subscription(customer_id)
                log_event(
                    "info",
                    "promote_to_metered",
                    customer_id=customer_id,
                    sub_item=sub_item_id,
                    reason=etype,
                )
                return {
                    "target_plan": "metered",
                    "stripe_customer_id": customer_id,
                    "subscription_item_id": sub_item_id,
                    "reason": etype,
                }
            log_event("info", "stay_free_no_default_pm", customer_id=customer_id, reason=etype)
            return {
                "target_plan": "free",
                "stripe_customer_id": customer_id,
                "subscription_item_id": None,
                "reason": "no_default_pm",
            }

        if etype == "invoice.payment_failed":
            log_event("warning", "demote_to_free_payment_failed", customer_id=customer_id)
            return {
                "target_plan": "free",
                "stripe_customer_id": customer_id,
                "subscription_item_id": None,
                "reason": etype,
            }

        log_event("info", "event_ignored", event_type=etype)
        return {"target_plan": None, "reason": f"ignored:{etype}"}

    # --- Usage reporting ---
    def reconcile_usage_window(self, since: datetime, until: datetime) -> list[dict[str, Any]]:
        """Report usage to Stripe for all metered customers within a time window.

        This method fetches API usage data for all customers on metered plans and
        reports it to Stripe for billing. It's designed to be called periodically
        (typically hourly) to sync usage data.

        The method:
            1. Scans for all customers on metered plans
            2. Fetches their API usage from API Gateway
            3. Reports non-zero usage to Stripe with idempotency
            4. Returns a summary of all reports made

        Args:
            since: Start of the usage window (inclusive)
            until: End of the usage window (exclusive)

        Returns:
            List of usage reports, each containing:
                - api_key_id: The API key that generated usage
                - customer_id: Stripe customer ID
                - units: Number of units reported
                - until: End timestamp of the reporting window

        Raises:
            AssertionError: If usage port is not configured

        Example:
            Report usage for the last hour::

                from datetime import datetime, timedelta

                now = datetime.utcnow()
                hour_ago = now - timedelta(hours=1)

                reports = service.reconcile_usage_window(hour_ago, now)
                # Returns: [
                #     {
                #         "api_key_id": "key_123",
                #         "customer_id": "cus_456",
                #         "units": 1500,
                #         "until": "2024-01-15T10:00:00"
                #     }
                # ]
        """
        assert self.usage is not None, "UsageSourcePort required"
        reports = []
        for link in self.repo.scan_metered():
            used = self.usage.get_usage(link.usage_plan_id, link.api_key_id, since, until)
            if used is None:
                continue
            delta = max(0, used)  # MVP: assume non-overlapping windows
            if delta > 0 and link.metered_subscription_item_id:
                ts = int(until.replace(tzinfo=UTC).timestamp())
                idem = f"{link.metered_subscription_item_id}:{until.isoformat()}:{delta}"
                self.stripe.report_usage(link.metered_subscription_item_id, delta, ts, idem)
                reports.append(
                    {
                        "api_key_id": link.api_key_id,
                        "customer_id": link.stripe_customer_id,
                        "units": delta,
                        "until": until.isoformat(),
                    }
                )
        log_metric("UsageReports", len(reports), dims={"WindowHours": "1"})
        return reports

    # --- Direct controls ---
    def promote(self, api_key_id: str) -> dict[str, Any]:
        """Manually promote an API key to the metered plan.

        This method allows direct promotion of a customer to the metered plan,
        bypassing the normal payment method checks. Useful for testing or
        special customer arrangements.

        Args:
            api_key_id: The API key to promote

        Returns:
            Dictionary containing:
                - target_plan: Always 'metered'
                - stripe_customer_id: Customer ID
                - subscription_item_id: Created subscription item ID

        Raises:
            KeyError: If the API key is not found

        Example:
            Promote a specific API key::

                result = service.promote("key_abc123")
                # Returns: {
                #     "target_plan": "metered",
                #     "stripe_customer_id": "cus_456",
                #     "subscription_item_id": "si_789"
                # }
        """
        link = self.repo.get_by_api_key(api_key_id)
        sub_item_id = self.stripe.ensure_metered_subscription(link.stripe_customer_id)
        return {
            "target_plan": "metered",
            "stripe_customer_id": link.stripe_customer_id,
            "subscription_item_id": sub_item_id,
        }

    def demote(self, api_key_id: str) -> dict[str, Any]:
        """Manually demote an API key to the free plan.

        This method forces a customer back to the free plan by canceling
        their subscription. Useful for handling special cases or testing.

        Args:
            api_key_id: The API key to demote

        Returns:
            Dictionary containing:
                - target_plan: Always 'free'
                - stripe_customer_id: Customer ID
                - subscription_item_id: Always None

        Raises:
            KeyError: If the API key is not found

        Example:
            Demote a specific API key::

                result = service.demote("key_abc123")
                # Returns: {
                #     "target_plan": "free",
                #     "stripe_customer_id": "cus_456",
                #     "subscription_item_id": None
                # }
        """
        link = self.repo.get_by_api_key(api_key_id)
        self.stripe.cancel_subscription_if_any(link.stripe_customer_id)
        return {
            "target_plan": "free",
            "stripe_customer_id": link.stripe_customer_id,
            "subscription_item_id": None,
        }

    # Optional in-lib plan move if admin is wired
    def apply_plan_move_for_customer(
        self,
        customer_id: str,
        target: str,
        sub_item_id: str | None,
        free_plan_id: str,
        metered_plan_id: str,
    ) -> int:
        """Apply a plan change for all API keys belonging to a customer.

        This method moves all of a customer's API keys between usage plans
        and updates their link records. It's typically called after processing
        a Stripe event to apply the plan change in API Gateway.

        Args:
            customer_id: Stripe customer ID
            target: Target plan ('free' or 'metered')
            sub_item_id: Subscription item ID for metered plan, None for free
            free_plan_id: API Gateway usage plan ID for free tier
            metered_plan_id: API Gateway usage plan ID for metered tier

        Returns:
            Number of API keys moved

        Note:
            Requires plan_admin port to be configured. Returns 0 if not available.

        Example:
            Apply a promotion to metered plan::

                moved = service.apply_plan_move_for_customer(
                    customer_id="cus_123",
                    target="metered",
                    sub_item_id="si_456",
                    free_plan_id="FREE_10K",
                    metered_plan_id="METERED"
                )
                # Returns: 2 (if customer has 2 API keys)
        """
        if not self.plan_admin:
            return 0
        moved = 0
        for link in self.repo.get_by_customer(customer_id):
            target_plan_id = metered_plan_id if target == "metered" else free_plan_id
            self.plan_admin.move_key_to_plan(link.api_key_id, target_plan_id)
            link.plan = "metered" if target == "metered" else "free"
            link.usage_plan_id = "METERED" if target == "metered" else "FREE_10K"
            if sub_item_id and target == "metered":
                link.metered_subscription_item_id = sub_item_id
            self.repo.save(link)
            moved += 1
        return moved
