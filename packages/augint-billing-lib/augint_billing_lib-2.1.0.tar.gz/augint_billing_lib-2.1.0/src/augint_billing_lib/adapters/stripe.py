"""Stripe API adapter implementation.

This module provides the concrete implementation of the StripePort interface,
handling all interactions with the Stripe payment processing API.

The adapter handles:
    - Payment method verification
    - Subscription management
    - Usage reporting for metered billing
    - Automatic retries for transient failures
    - Price discovery for products

Example:
    Basic adapter usage::

        from augint_billing_lib.adapters.stripe import StripeAdapter

        adapter = StripeAdapter(
            secret_key="sk_test_...",
            metered_price_id="price_metered123"
        )

        # Check if customer has payment method
        has_payment = adapter.has_default_payment_method("cus_abc")

        # Create or get metered subscription
        sub_item_id = adapter.ensure_metered_subscription("cus_abc")

        # Report usage
        adapter.report_usage(sub_item_id, 1000, timestamp, "unique_key")
"""

from __future__ import annotations

from typing import Any

import stripe

from ..utils_retry import retry


class StripeAdapter:
    """Concrete implementation of StripePort for Stripe API interactions.

    This adapter provides the actual Stripe API integration, implementing
    all methods required by the StripePort interface. It includes automatic
    retry logic for transient failures and price discovery capabilities.

    Attributes:
        price_id: The Stripe price ID for metered billing. Can be provided
            directly or discovered automatically from the product catalog.

    Note:
        All API calls include automatic retry logic for connection errors,
        rate limit errors, and general API errors.
    """

    def __init__(self, secret_key: str, metered_price_id: str | None = None):
        """Initialize the Stripe adapter with API credentials.

        Args:
            secret_key: Stripe API secret key (sk_test_... or sk_live_...)
            metered_price_id: Optional price ID for metered billing.
                If not provided, will attempt to discover it automatically.
        """
        stripe.api_key = secret_key
        self.price_id = metered_price_id

    @staticmethod
    @retry((stripe.error.APIConnectionError, stripe.error.RateLimitError, stripe.error.APIError))  # type: ignore[attr-defined]
    def _list_prices(**kw: Any) -> Any:
        return stripe.Price.list(**kw)

    @staticmethod
    @retry((stripe.error.APIConnectionError, stripe.error.RateLimitError, stripe.error.APIError))  # type: ignore[attr-defined]
    def _retrieve_customer(customer_id: str) -> Any:
        return stripe.Customer.retrieve(customer_id)

    @staticmethod
    @retry((stripe.error.APIConnectionError, stripe.error.RateLimitError, stripe.error.APIError))  # type: ignore[attr-defined]
    def _list_subs(**kw: Any) -> Any:
        return stripe.Subscription.list(**kw)

    @staticmethod
    @retry((stripe.error.APIConnectionError, stripe.error.RateLimitError, stripe.error.APIError))  # type: ignore[attr-defined]
    def _create_sub(**kw: Any) -> Any:
        return stripe.Subscription.create(**kw)

    @staticmethod
    @retry((stripe.error.APIConnectionError, stripe.error.RateLimitError, stripe.error.APIError))  # type: ignore[attr-defined]
    def _modify_sub(sub_id: str, **kw: Any) -> Any:
        return stripe.Subscription.modify(sub_id, **kw)

    @staticmethod
    @retry((stripe.error.APIConnectionError, stripe.error.RateLimitError, stripe.error.APIError))  # type: ignore[attr-defined]
    def _create_usage(**kw: Any) -> Any:
        return stripe.UsageRecord.create(**kw)  # type: ignore[no-untyped-call]

    def discover_metered_price_id(self, api_usage_product_id: str | None = None) -> str | None:
        """Discover the metered price ID from Stripe product catalog.

        Searches for an active metered price, either for a specific product
        or across all products. This is useful when the price ID isn't
        configured explicitly.

        Args:
            api_usage_product_id: Optional Stripe product ID to search within.
                If provided, only searches prices for this product.

        Returns:
            The first metered price ID found, or None if none exist.

        Example:
            Discover price for specific product::

                price_id = adapter.discover_metered_price_id("prod_api_usage")
                if price_id:
                    adapter.price_id = price_id
        """
        if api_usage_product_id:
            prices = self._list_prices(active=True, product=api_usage_product_id, limit=100)
            for pr in prices.auto_paging_iter():
                r = pr.get("recurring")
                if r and r.get("usage_type") == "metered":
                    return str(pr["id"])
        prices = self._list_prices(active=True, limit=100)
        for pr in prices.auto_paging_iter():
            r = pr.get("recurring")
            if r and r.get("usage_type") == "metered":
                return str(pr["id"])
        return None

    def has_default_payment_method(self, customer_id: str) -> bool:
        """Check if a customer has a default payment method configured.

        Retrieves the customer from Stripe and checks if they have a
        default payment method set in their invoice settings.

        Args:
            customer_id: Stripe customer ID (e.g., 'cus_abc123')

        Returns:
            True if customer has a default payment method, False otherwise.

        Raises:
            stripe.error.StripeError: If customer retrieval fails
        """
        cust = self._retrieve_customer(customer_id)
        return bool(cust.get("invoice_settings", {}).get("default_payment_method"))

    def ensure_metered_subscription(self, customer_id: str) -> str:
        """Ensure customer has an active metered subscription.

        Checks if the customer already has a metered subscription. If not,
        creates a new one. This method is idempotent - calling it multiple
        times will not create duplicate subscriptions.

        Args:
            customer_id: Stripe customer ID

        Returns:
            Subscription item ID for the metered price (e.g., 'si_xyz789')

        Raises:
            RuntimeError: If no metered price ID is configured or discoverable
            stripe.error.StripeError: If subscription creation fails

        Example:
            Ensure subscription exists::

                sub_item_id = adapter.ensure_metered_subscription("cus_123")
                # Can now report usage against sub_item_id
        """
        subs = self._list_subs(
            customer=customer_id, status="active", expand=["data.items.data.price"]
        )
        for s in subs.auto_paging_iter():
            for it in s["items"]["data"]:
                if it["price"]["recurring"]["usage_type"] == "metered":
                    return str(it["id"])
        if not self.price_id:
            raise RuntimeError(
                "No metered price available. Provide API_USAGE_PRODUCT_ID or set price explicitly."
            )
        sub = self._create_sub(
            customer=customer_id,
            items=[{"price": self.price_id}],
            payment_behavior="default_incomplete",
            expand=["items", "latest_invoice.payment_intent"],
        )
        return str(sub["items"]["data"][0]["id"])

    def cancel_subscription_if_any(self, customer_id: str) -> None:
        """Cancel all active subscriptions for a customer.

        Marks all active subscriptions to cancel at the end of the current
        billing period. This is typically called when a customer downgrades
        to the free tier or has payment issues.

        Args:
            customer_id: Stripe customer ID

        Note:
            Subscriptions are cancelled at period end to allow customers
            to use their remaining paid time.
        """
        subs = self._list_subs(customer=customer_id, status="active")
        for s in subs.auto_paging_iter():
            self._modify_sub(s["id"], cancel_at_period_end=True)

    def report_usage(
        self, subscription_item_id: str, units: int, timestamp: int, idempotency_key: str
    ) -> None:
        """Report usage for a metered subscription item.

        Reports incremental usage that will be aggregated and billed at the
        end of the billing period. Uses idempotency to prevent duplicate
        charges if the request is retried.

        Args:
            subscription_item_id: The subscription item to report usage for
            units: Number of units to report (e.g., API calls)
            timestamp: Unix timestamp when the usage occurred
            idempotency_key: Unique key to prevent duplicate reports

        Raises:
            stripe.error.StripeError: If usage reporting fails

        Example:
            Report 1000 API calls::

                import time

                adapter.report_usage(
                    subscription_item_id="si_123",
                    units=1000,
                    timestamp=int(time.time()),
                    idempotency_key="usage_2024-01-15T10:00_1000"
                )
        """
        self._create_usage(
            subscription_item=subscription_item_id,
            quantity=units,
            timestamp=timestamp,
            action="increment",
            idempotency_key=idempotency_key,
        )
