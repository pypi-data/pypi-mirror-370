"""Abstract interfaces (ports) for external dependencies.

This module defines the abstract interfaces that the core business logic depends on,
following the Ports & Adapters (Hexagonal) architecture pattern. These interfaces
allow the core domain to remain independent of specific implementations.

The ports define contracts that adapters must implement, enabling:
    - Testability through mock implementations
    - Flexibility to swap implementations
    - Clear separation of concerns
    - Dependency inversion

Example:
    Implementing a custom Stripe adapter::

        class MyStripeAdapter:
            def has_default_payment_method(self, customer_id: str) -> bool:
                # Custom implementation
                customer = stripe.Customer.retrieve(customer_id)
                return customer.invoice_settings.default_payment_method is not None

            def ensure_metered_subscription(self, customer_id: str) -> str:
                # Custom subscription logic
                ...
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from .models import Link


class StripePort(Protocol):
    """Interface for Stripe payment processing operations.

    This port defines the contract for interacting with Stripe's API,
    abstracting away the specific implementation details.

    Implementations should handle:
        - API authentication and connection management
        - Error handling and retries
        - Idempotency for critical operations
        - Test/live mode switching
    """

    def has_default_payment_method(self, customer_id: str) -> bool:
        """Check if a customer has a default payment method configured.

        Args:
            customer_id: Stripe customer ID (e.g., 'cus_abc123')

        Returns:
            True if the customer has a default payment method, False otherwise

        Raises:
            Exception: If Stripe API call fails
        """
        ...

    def ensure_metered_subscription(self, customer_id: str) -> str:
        """Ensure a customer has an active metered subscription.

        Creates a new metered subscription if none exists, or returns the
        subscription item ID of the existing one. This is idempotent and
        safe to call multiple times.

        Args:
            customer_id: Stripe customer ID

        Returns:
            Subscription item ID for the metered price (e.g., 'si_xyz789')

        Raises:
            Exception: If subscription creation fails
        """
        ...

    def cancel_subscription_if_any(self, customer_id: str) -> None:
        """Cancel any active subscriptions for a customer.

        Cancels all active subscriptions immediately. This is typically
        called when a payment fails or a customer downgrades to free tier.

        Args:
            customer_id: Stripe customer ID

        Raises:
            Exception: If cancellation fails
        """
        ...

    def report_usage(
        self, subscription_item_id: str, units: int, timestamp: int, idempotency_key: str
    ) -> None:
        """Report usage for a metered subscription item.

        Reports incremental usage that will be aggregated and billed at the
        end of the billing period. Uses idempotency to prevent duplicate charges.

        Args:
            subscription_item_id: The subscription item to report usage for
            units: Number of units to report (e.g., API calls)
            timestamp: Unix timestamp for the usage event
            idempotency_key: Unique key to prevent duplicate reports

        Raises:
            Exception: If usage reporting fails
        """
        ...


class UsageSourcePort(Protocol):
    """Interface for retrieving API usage data.

    This port defines how to fetch usage metrics from the API Gateway
    or other usage tracking systems.
    """

    def get_usage(
        self, usage_plan_id: str, api_key_id: str, since: datetime, until: datetime
    ) -> int | None:
        """Get API usage for a specific key within a time window.

        Retrieves the total number of API calls made by a specific API key
        within the given time window. Returns None if no usage data is available.

        Args:
            usage_plan_id: The usage plan ID (e.g., 'FREE_10K', 'METERED')
            api_key_id: The API key to get usage for
            since: Start of the time window (inclusive)
            until: End of the time window (exclusive)

        Returns:
            Total number of API calls, or None if no data available

        Raises:
            Exception: If API Gateway query fails
        """
        ...


class PlanAdminPort(Protocol):
    """Interface for managing API Gateway usage plan assignments.

    This port handles the administrative operations for moving API keys
    between different usage plans based on payment status.
    """

    def move_key_to_plan(self, api_key_id: str, target_plan_id: str) -> None:
        """Move an API key to a different usage plan.

        Removes the API key from its current usage plan (if any) and
        associates it with the target usage plan. This controls the
        rate limiting and quota for the API key.

        Args:
            api_key_id: The API key to move
            target_plan_id: The target usage plan ID (e.g., 'FREE_10K', 'METERED')

        Raises:
            Exception: If the move operation fails
        """
        ...


class CustomerRepoPort(Protocol):
    """Interface for customer data persistence.

    This port defines operations for storing and retrieving customer
    link data that maps API keys to Stripe customers and usage plans.

    Implementations should ensure:
        - Atomic operations for consistency
        - Efficient queries for batch operations
        - Proper indexing for lookups
    """

    def get_by_api_key(self, api_key_id: str) -> Link:
        """Retrieve customer link data by API key.

        Args:
            api_key_id: The API key to look up

        Returns:
            Link object containing customer mapping data

        Raises:
            KeyError: If the API key is not found
            Exception: If database query fails
        """
        ...

    def get_by_customer(self, customer_id: str) -> list[Link]:
        """Retrieve all links for a Stripe customer.

        A customer may have multiple API keys, this returns all of them.

        Args:
            customer_id: Stripe customer ID

        Returns:
            List of Link objects for the customer (may be empty)

        Raises:
            Exception: If database query fails
        """
        ...

    def save(self, link: Link) -> None:
        """Save or update a customer link.

        Creates a new link or updates an existing one. This should be
        an atomic operation to prevent race conditions.

        Args:
            link: Link object to persist

        Raises:
            Exception: If save operation fails
        """
        ...

    def scan_metered(self) -> list[Link]:
        """Retrieve all customers on metered plans.

        Returns all links where the plan is 'metered', typically used
        for batch usage reporting operations.

        Returns:
            List of Link objects with plan='metered'

        Raises:
            Exception: If database scan fails
        """
        ...
