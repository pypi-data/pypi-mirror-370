from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime
from typing import Any

import botocore  # type: ignore[import-untyped]
from boto3.dynamodb.conditions import Key  # type: ignore[import-untyped]

from ..models import Link
from ..utils_retry import retry


class DdbRepo:
    def __init__(self, table: Any) -> None:
        self.table = table

    def _coerce(self, item: dict[str, Any]) -> Link:
        ts = item.get("last_reported_usage_ts")
        if isinstance(ts, str):
            try:
                item["last_reported_usage_ts"] = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except Exception:
                item["last_reported_usage_ts"] = None
        return Link(**item)

    @retry((botocore.exceptions.ClientError,), tries=5)
    def get_by_api_key(self, api_key_id: str) -> Link:
        resp = self.table.get_item(Key={"api_key_id": api_key_id})
        if "Item" not in resp:
            raise KeyError(api_key_id)
        return self._coerce(resp["Item"])

    @retry((botocore.exceptions.ClientError,), tries=5)
    def get_by_customer(self, customer_id: str) -> list[Link]:
        resp = self.table.query(
            IndexName="gsi_stripe_customer",
            KeyConditionExpression=Key("stripe_customer_id").eq(customer_id),
        )
        return [self._coerce(it) for it in resp.get("Items", [])]

    @retry((botocore.exceptions.ClientError,), tries=5)
    def save(self, link: Link) -> None:
        item = asdict(link)
        ts = item.get("last_reported_usage_ts")
        if isinstance(ts, datetime):
            item["last_reported_usage_ts"] = ts.astimezone(UTC).isoformat()
        self.table.put_item(Item=item)

    @retry((botocore.exceptions.ClientError,), tries=5)
    def scan_metered(self) -> list[Link]:
        resp = self.table.scan()
        out = []
        for it in resp.get("Items", []):
            if it.get("plan") == "metered" and it.get("metered_subscription_item_id"):
                out.append(self._coerce(it))
        return out
