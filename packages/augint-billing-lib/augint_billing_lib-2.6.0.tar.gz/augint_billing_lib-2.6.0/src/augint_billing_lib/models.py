"""Data models for the billing system.

This module contains the core data structures used throughout the billing library.
The models are designed to be simple, immutable where possible, and focused on
representing the domain concepts clearly.

Example:
    Creating and working with a Link::

        from augint_billing_lib.models import Link
        from datetime import datetime

        # Create a new link for a free tier customer
        link = Link(
            api_key_id="key_abc123",
            stripe_customer_id="cus_xyz789",
            plan="free",
            usage_plan_id="FREE_10K"
        )

        # Upgrade to metered plan
        link.plan = "metered"
        link.usage_plan_id = "METERED"
        link.metered_subscription_item_id = "si_metered123"
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass
class Link:
    """Represents the link between an API key, Stripe customer, and usage plan.

    This is the core entity that maps API keys to Stripe customers and tracks
    their current plan status, usage reporting state, and subscription details.

    The Link model serves as the source of truth for:
        - Which usage plan an API key belongs to
        - Which Stripe customer owns the API key
        - Current billing state (free vs metered)
        - Usage reporting checkpoints

    Attributes:
        api_key_id: Unique identifier for the API key. This is the primary key
            used to look up customer information.

        stripe_customer_id: Stripe customer ID (e.g., 'cus_abc123'). Links the
            API key to a Stripe customer for billing.

        cognito_user_id: Optional AWS Cognito user ID for additional user context.
            May be None if the user hasn't authenticated via Cognito.

        plan: Current billing plan. Either 'free' for the limited free tier or
            'metered' for usage-based billing. Defaults to 'free'.

        usage_plan_id: API Gateway usage plan ID that controls rate limits and
            quotas. Typically 'FREE_10K' or 'METERED'. Defaults to 'FREE_10K'.

        metered_subscription_item_id: Stripe subscription item ID for metered billing.
            Required when plan='metered', None for free tier customers.

        last_reported_usage_ts: Timestamp of the last successful usage report to Stripe.
            Used to calculate incremental usage since last report. None if never reported.

        current_month_reported_units: Running total of units reported for the current
            billing month. Resets to 0 at month boundaries. Used to calculate deltas.

    Example:
        Free tier customer::

            link = Link(
                api_key_id="key_free123",
                stripe_customer_id="cus_free456",
                plan="free",
                usage_plan_id="FREE_10K"
            )

        Metered customer with usage history::

            link = Link(
                api_key_id="key_metered789",
                stripe_customer_id="cus_metered012",
                plan="metered",
                usage_plan_id="METERED",
                metered_subscription_item_id="si_abc123",
                last_reported_usage_ts=datetime(2024, 1, 15, 10, 0),
                current_month_reported_units=5000
            )

    Note:
        The Link model is persisted in DynamoDB with api_key_id as the partition key
        and stripe_customer_id indexed for reverse lookups.
    """

    api_key_id: str
    """Unique identifier for the API key (primary key)."""

    stripe_customer_id: str
    """Stripe customer ID for billing association."""

    cognito_user_id: str | None = None
    """Optional AWS Cognito user identifier."""

    plan: Literal["free", "metered"] = "free"
    """Current billing plan type."""

    usage_plan_id: str = "FREE_10K"
    """API Gateway usage plan ID for rate limiting."""

    metered_subscription_item_id: str | None = None
    """Stripe subscription item ID for usage reporting."""

    last_reported_usage_ts: datetime | None = None
    """Timestamp of last successful usage report."""

    current_month_reported_units: int = 0
    """Running total of reported units for current month."""

    def is_metered(self) -> bool:
        """Check if this link is on a metered plan.

        Returns:
            True if plan is 'metered', False otherwise.
        """
        return self.plan == "metered"

    def is_free(self) -> bool:
        """Check if this link is on the free plan.

        Returns:
            True if plan is 'free', False otherwise.
        """
        return self.plan == "free"

    def can_report_usage(self) -> bool:
        """Check if this link is ready for usage reporting.

        A link can report usage if it's on a metered plan and has
        a valid subscription item ID.

        Returns:
            True if usage can be reported, False otherwise.
        """
        return self.is_metered() and self.metered_subscription_item_id is not None

    def needs_month_reset(self, current_time: datetime) -> bool:
        """Check if the usage counter needs to be reset for a new month.

        Args:
            current_time: The current timestamp to check against.

        Returns:
            True if the month has changed since last report, False otherwise.
        """
        if self.last_reported_usage_ts is None:
            return False

        return (
            self.last_reported_usage_ts.year != current_time.year
            or self.last_reported_usage_ts.month != current_time.month
        )
