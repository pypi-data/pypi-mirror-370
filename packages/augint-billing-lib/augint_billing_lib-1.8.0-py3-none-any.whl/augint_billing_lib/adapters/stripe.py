from __future__ import annotations

from typing import Any

import stripe

from ..utils_retry import retry


class StripeAdapter:
    def __init__(self, secret_key: str, metered_price_id: str | None = None):
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
        cust = self._retrieve_customer(customer_id)
        return bool(cust.get("invoice_settings", {}).get("default_payment_method"))

    def ensure_metered_subscription(self, customer_id: str) -> str:
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
        subs = self._list_subs(customer=customer_id, status="active")
        for s in subs.auto_paging_iter():
            self._modify_sub(s["id"], cancel_at_period_end=True)

    def report_usage(
        self, subscription_item_id: str, units: int, timestamp: int, idempotency_key: str
    ) -> None:
        self._create_usage(
            subscription_item=subscription_item_id,
            quantity=units,
            timestamp=timestamp,
            action="increment",
            idempotency_key=idempotency_key,
        )
