from __future__ import annotations

from typing import Any

import botocore  # type: ignore[import-untyped]

from ..utils_retry import retry


class ApiGwAdmin:
    def __init__(self, apigw_client: Any, free_plan_id: str, metered_plan_id: str) -> None:
        self.apigw = apigw_client
        self.free_plan_id = free_plan_id
        self.metered_plan_id = metered_plan_id

    @retry((botocore.exceptions.ClientError,), tries=5)
    def _remove_from_plan(self, usage_plan_id: str, api_key_id: str) -> None:
        pager = self.apigw.get_paginator("get_usage_plan_keys")
        for page in pager.paginate(usagePlanId=usage_plan_id, limit=500):
            for k in page.get("items", []):
                if k.get("value") == api_key_id:
                    self.apigw.delete_usage_plan_key(usagePlanId=usage_plan_id, keyId=k["id"])

    @retry((botocore.exceptions.ClientError,), tries=5)
    def move_key_to_plan(self, api_key_id: str, target_plan_id: str) -> None:
        other = self.metered_plan_id if target_plan_id == self.free_plan_id else self.free_plan_id
        self._remove_from_plan(other, api_key_id)
        self.apigw.create_usage_plan_key(
            usagePlanId=target_plan_id, keyId=api_key_id, keyType="API_KEY"
        )
