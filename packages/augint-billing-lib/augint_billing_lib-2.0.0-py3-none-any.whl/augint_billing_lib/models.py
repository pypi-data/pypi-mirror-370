from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Link:
    api_key_id: str
    stripe_customer_id: str
    cognito_user_id: str | None = None
    plan: str = "free"  # "free" | "metered"
    usage_plan_id: str = "FREE_10K"
    metered_subscription_item_id: str | None = None
    last_reported_usage_ts: datetime | None = None
    current_month_reported_units: int = 0
