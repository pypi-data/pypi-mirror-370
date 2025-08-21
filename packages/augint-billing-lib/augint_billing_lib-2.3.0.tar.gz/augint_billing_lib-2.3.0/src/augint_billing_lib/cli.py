#!/usr/bin/env python3
"""Command-line interface for the billing system.

This module provides CLI commands for testing and administering the billing
system. It includes commands for processing events, reporting usage, and
managing customer plans.

The CLI is designed for:
    - Local testing and development
    - Emergency production operations
    - Integration testing
    - Debugging and troubleshooting

Commands:
    - env-dump: Display current environment configuration
    - handle-event: Process a Stripe event locally
    - sync-usage: Report usage to Stripe
    - promote: Upgrade an API key to metered plan
    - demote: Downgrade an API key to free plan

Example:
    Basic CLI usage::

        # Show environment configuration
        $ ai-billing env-dump
        {
          "STACK_NAME": "billing-prod",
          "AWS_REGION": "us-east-1",
          "STRIPE_SECRET_KEY": "sk_test_..."
        }

        # Process a Stripe event
        $ ai-billing handle-event --file events/payment.json

        # Report usage for the last hour
        $ ai-billing sync-usage

        # Promote a customer
        $ ai-billing promote --api-key key_abc123

Environment:
    The CLI automatically loads .env files from the current directory
    or parent directory if present. All AWS and Stripe configuration
    is read from environment variables.
"""

from __future__ import annotations

import json
import os
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import click

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover

    def load_dotenv(*_a: Any, **_k: Any) -> bool:  # type: ignore[misc]
        return False


from .bootstrap import build_service, process_event_and_apply_plan_moves


def _load_env_if_present() -> None:
    """Load environment variables from .env file if present.

    Searches for .env file in current directory or parent directory
    and loads environment variables from it. Does not override
    existing environment variables.
    """
    for p in [Path.cwd() / ".env", Path.cwd().parent / ".env"]:
        if p.exists():
            load_dotenv(p, override=False)
            break


def _pick(cli_value: str | None, env_key: str, default: str | None = None) -> str | None:
    """Pick value from CLI argument, environment, or default.

    Args:
        cli_value: Value provided via CLI argument
        env_key: Environment variable key to check
        default: Default value if neither CLI nor env is set

    Returns:
        First non-empty value from: CLI, environment, default
    """
    if cli_value not in (None, ""):
        return cli_value
    val = os.environ.get(env_key)
    return val if val not in (None, "") else default


def _run(cmd: list[str], cwd: Path | None = None) -> int:
    """Run a shell command and display it.

    Args:
        cmd: Command and arguments to run
        cwd: Working directory for command

    Returns:
        Command exit code
    """
    click.echo(click.style("+ " + " ".join(cmd), fg="cyan"))
    return subprocess.run(cmd, check=False, cwd=str(cwd) if cwd else None).returncode  # noqa: S603


@click.group(help="AugInt Billing CLI (single tool). Local E2E + deploy/delete/tests.")
def cli() -> None:
    """Main CLI entry point.

    Loads environment variables and provides command grouping.
    """
    _load_env_if_present()


@cli.command("env-dump")
def env_dump() -> None:
    """Display current environment configuration.

    Shows all billing-related environment variables in JSON format.
    Useful for debugging configuration issues.

    Example:
        $ ai-billing env-dump
        {
          "STACK_NAME": "billing-prod",
          "AWS_REGION": "us-east-1",
          "STRIPE_SECRET_KEY": "sk_test_...",
          "TABLE_NAME": "customer-links",
          "FREE_USAGE_PLAN_ID": "plan_free",
          "METERED_USAGE_PLAN_ID": "plan_metered"
        }
    """
    keys = [
        "STACK_NAME",
        "AWS_REGION",
        "STRIPE_SECRET_KEY",
        "STRIPE_SECRET_ARN",
        "TABLE_NAME",
        "FREE_USAGE_PLAN_ID",
        "METERED_USAGE_PLAN_ID",
        "API_USAGE_PRODUCT_ID",
    ]
    click.echo(json.dumps({k: os.environ.get(k, "") for k in keys}, indent=2))


@cli.command("handle-event")
@click.option(
    "--file",
    "file_path",
    type=click.Path(exists=True, dir_okay=False),
    help="JSON file containing Stripe event",
)
def handle_event(file_path: str | None) -> None:
    """Process a Stripe event and apply plan changes.

    Reads a Stripe event from file or stdin, processes it to determine
    the target plan, and applies the changes to affected API keys.

    Args:
        file_path: Path to JSON file containing event (or stdin if not provided)

    Example:
        From file::

            $ ai-billing handle-event --file events/payment_method.attached.json
            {
              "target_plan": "metered",
              "moved": 2,
              "stripe_customer_id": "cus_123"
            }

        From stdin::

            $ cat event.json | ai-billing handle-event
    """
    payload = (
        json.loads(Path(file_path).read_text())
        if file_path
        else json.loads(click.get_text_stream("stdin").read())
    )
    click.echo(json.dumps(process_event_and_apply_plan_moves(payload), indent=2))


@cli.command("sync-usage")
@click.option("--since", help="Start of usage window (ISO format)")
@click.option("--until", help="End of usage window (ISO format)")
def sync_usage(since: str | None, until: str | None) -> None:
    """Report API usage to Stripe for billing.

    Fetches usage data from API Gateway and reports it to Stripe
    for all metered customers. By default, reports the last hour.

    Args:
        since: Start time in ISO format (defaults to 1 hour ago)
        until: End time in ISO format (defaults to current hour)

    Example:
        Report last hour::

            $ ai-billing sync-usage
            {
              "reported": 5,
              "window": {
                "since": "2024-01-15T09:00:00+00:00",
                "until": "2024-01-15T10:00:00+00:00"
              }
            }

        Report specific window::

            $ ai-billing sync-usage --since 2024-01-15T00:00:00Z --until 2024-01-15T12:00:00Z
    """
    now = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
    u = datetime.fromisoformat(until.replace("Z", "+00:00")) if until else now
    s = datetime.fromisoformat(since.replace("Z", "+00:00")) if since else (u - timedelta(hours=1))
    svc = build_service(include_usage=True)
    click.echo(
        json.dumps(
            {
                "reported": len(svc.reconcile_usage_window(s, u)),
                "window": {"since": s.isoformat(), "until": u.isoformat()},
            },
            indent=2,
        )
    )


@cli.command("promote")
@click.option("--api-key", "api_key_id", required=True, help="API key to promote")
def promote(api_key_id: str) -> None:
    """Promote an API key to metered plan.

    Creates a metered subscription for the customer and updates
    their plan status. This bypasses payment method checks.

    Args:
        api_key_id: The API key to promote

    Example:
        $ ai-billing promote --api-key key_abc123
        {
          "target_plan": "metered",
          "stripe_customer_id": "cus_456",
          "subscription_item_id": "si_789"
        }
    """
    svc = build_service(include_usage=False)
    click.echo(json.dumps(svc.promote(api_key_id), indent=2))


@cli.command("demote")
@click.option("--api-key", "api_key_id", required=True, help="API key to demote")
def demote(api_key_id: str) -> None:
    """Demote an API key to free plan.

    Cancels any active subscriptions for the customer and updates
    their plan status to free tier.

    Args:
        api_key_id: The API key to demote

    Example:
        $ ai-billing demote --api-key key_abc123
        {
          "target_plan": "free",
          "stripe_customer_id": "cus_456",
          "subscription_item_id": null
        }
    """
    svc = build_service(include_usage=False)
    click.echo(json.dumps(svc.demote(api_key_id), indent=2))


if __name__ == "__main__":
    cli()
