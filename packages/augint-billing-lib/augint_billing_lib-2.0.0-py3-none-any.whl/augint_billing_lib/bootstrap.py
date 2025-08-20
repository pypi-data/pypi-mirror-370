from __future__ import annotations

import json
import os
from typing import Any

import boto3  # type: ignore[import-untyped]
import stripe

from .adapters.apigw_admin import ApiGwAdmin
from .adapters.apigw_usage import ApiGwUsage
from .adapters.ddb_repo import DdbRepo
from .adapters.stripe import StripeAdapter
from .logging import log_event
from .service import BillingService


def _cfn_outputs(stack_name: str, region: str) -> dict[str, str]:
    cfn = boto3.client("cloudformation", region_name=region)
    try:
        resp = cfn.describe_stacks(StackName=stack_name)
        stacks = resp.get("Stacks", [])
        outputs = stacks[0].get("Outputs", []) if stacks else []
        return {
            o["OutputKey"]: o["OutputValue"]
            for o in outputs
            if "OutputKey" in o and "OutputValue" in o
        }
    except Exception:
        return {}


def _discover_table_name(stack_name: str, region: str) -> str:
    out = _cfn_outputs(stack_name, region)
    table_name = out.get("TableName") or os.getenv("TABLE_NAME", "customer_links")
    assert table_name is not None
    return table_name


def _discover_usage_plan_ids(region: str) -> dict[str, str]:
    apigw = boto3.client("apigateway", region_name=region)
    plans = apigw.get_usage_plans(limit=500).get("items", [])
    found = {}
    for p in plans:
        n = p.get("name", "")
        if n == "FREE_10K":
            found["FREE_10K"] = p.get("id")
        if n == "METERED":
            found["METERED"] = p.get("id")
    free_override = os.getenv("FREE_USAGE_PLAN_ID")
    meter_override = os.getenv("METERED_USAGE_PLAN_ID")
    if free_override:
        found["FREE_10K"] = free_override
    if meter_override:
        found["METERED"] = meter_override
    return found


def _stripe_from_env_or_secret() -> tuple[str, str | None]:
    arn = os.getenv("STRIPE_SECRET_ARN")
    region = os.getenv("AWS_REGION")
    if arn and region:
        sm = boto3.client("secretsmanager", region_name=region)
        blob = sm.get_secret_value(SecretId=arn).get("SecretString") or "{}"
        cfg = json.loads(blob)
        return cfg["STRIPE_SECRET_KEY"], cfg.get("STRIPE_PRICE_ID_METERED")
    return os.environ["STRIPE_SECRET_KEY"], os.getenv("STRIPE_PRICE_ID_METERED")


def build_service(include_usage: bool = True) -> BillingService:
    region = os.environ["AWS_REGION"]
    stack = os.environ["STACK_NAME"]
    table = _discover_table_name(stack, region)

    ddb = boto3.resource("dynamodb", region_name=region)
    repo = DdbRepo(ddb.Table(table))
    usage = ApiGwUsage(boto3.client("apigateway", region_name=region)) if include_usage else None

    sk, price = _stripe_from_env_or_secret()
    stripe.api_key = sk
    stripe_adapter = StripeAdapter(
        secret_key=sk,
        metered_price_id=price
        or StripeAdapter(secret_key=sk).discover_metered_price_id(
            os.getenv("API_USAGE_PRODUCT_ID")
        ),
    )

    # Wire optional plan_admin
    plans = _discover_usage_plan_ids(region)
    plan_admin = None
    if plans.get("FREE_10K") and plans.get("METERED"):
        plan_admin = ApiGwAdmin(
            boto3.client("apigateway", region_name=region),
            free_plan_id=plans["FREE_10K"],
            metered_plan_id=plans["METERED"],
        )

    return BillingService(repo=repo, stripe=stripe_adapter, usage=usage, plan_admin=plan_admin)


def process_event_and_apply_plan_moves(evt: dict[str, Any]) -> dict[str, Any]:
    region = os.environ["AWS_REGION"]
    svc = build_service(include_usage=False)
    action = svc.handle_stripe_event(evt)

    target = action.get("target_plan")
    customer_id = action.get("stripe_customer_id")
    subitem = action.get("subscription_item_id")

    if not target or not customer_id:
        return {"ignored": True, "reason": action.get("reason")}

    plan_ids = _discover_usage_plan_ids(region)
    free_id = plan_ids.get("FREE_10K")
    meter_id = plan_ids.get("METERED")
    if not (free_id and meter_id):
        log_event("error", "missing_usage_plans", details=plan_ids)
        return {"error": "missing_usage_plans", "details": plan_ids}

    moved = svc.apply_plan_move_for_customer(customer_id, target, subitem, free_id, meter_id)
    return {"target_plan": target, "moved": moved, "stripe_customer_id": customer_id}
