from __future__ import annotations

import contextlib
from datetime import datetime
from typing import Any

import botocore  # type: ignore[import-untyped]

from ..utils_retry import retry


class ApiGwUsage:
    def __init__(self, apigw_client: Any) -> None:
        self.apigw = apigw_client

    @retry((botocore.exceptions.ClientError,), tries=5)
    def get_usage(
        self, usage_plan_id: str, api_key_id: str, since: datetime, until: datetime
    ) -> int | None:
        start = since.date().isoformat()
        end = until.date().isoformat()
        resp = self.apigw.get_usage(
            usagePlanId=usage_plan_id, keyId=api_key_id, startDate=start, endDate=end
        )
        total = 0
        for _stage, days in (resp.get("values") or {}).items():
            for day in days:
                for _k, v in day.items():
                    with contextlib.suppress(Exception):
                        total += int(v)
        return total
