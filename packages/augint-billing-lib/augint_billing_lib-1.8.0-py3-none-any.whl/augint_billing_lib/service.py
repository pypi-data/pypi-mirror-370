from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .logging import log_event, log_metric
from .ports import CustomerRepoPort, PlanAdminPort, StripePort, UsageSourcePort


class BillingService:
    def __init__(
        self,
        repo: CustomerRepoPort,
        stripe: StripePort,
        usage: UsageSourcePort | None = None,
        plan_admin: PlanAdminPort | None = None,
    ):
        self.repo = repo
        self.stripe = stripe
        self.usage = usage
        self.plan_admin = plan_admin

    # --- Event handling ---
    def handle_stripe_event(self, evt: dict[str, Any]) -> dict[str, Any]:
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
        link = self.repo.get_by_api_key(api_key_id)
        sub_item_id = self.stripe.ensure_metered_subscription(link.stripe_customer_id)
        return {
            "target_plan": "metered",
            "stripe_customer_id": link.stripe_customer_id,
            "subscription_item_id": sub_item_id,
        }

    def demote(self, api_key_id: str) -> dict[str, Any]:
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
        if not self.plan_admin:
            return 0
        moved = 0
        for link in self.repo.get_by_customer(customer_id):
            target_plan_id = metered_plan_id if target == "metered" else free_plan_id
            self.plan_admin.move_key_to_plan(link.api_key_id, target_plan_id)
            link.plan = target
            link.usage_plan_id = "METERED" if target == "metered" else "FREE_10K"
            if sub_item_id and target == "metered":
                link.metered_subscription_item_id = sub_item_id
            self.repo.save(link)
            moved += 1
        return moved
