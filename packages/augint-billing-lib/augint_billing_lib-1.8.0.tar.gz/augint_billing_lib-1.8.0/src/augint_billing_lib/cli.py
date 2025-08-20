#!/usr/bin/env python3
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
    for p in [Path.cwd() / ".env", Path.cwd().parent / ".env"]:
        if p.exists():
            load_dotenv(p, override=False)
            break


def _pick(cli_value: str | None, env_key: str, default: str | None = None) -> str | None:
    if cli_value not in (None, ""):
        return cli_value
    val = os.environ.get(env_key)
    return val if val not in (None, "") else default


def _run(cmd: list[str], cwd: Path | None = None) -> int:
    click.echo(click.style("+ " + " ".join(cmd), fg="cyan"))
    return subprocess.run(cmd, check=False, cwd=str(cwd) if cwd else None).returncode  # noqa: S603


@click.group(help="AugInt Billing CLI (single tool). Local E2E + deploy/delete/tests.")
def cli() -> None:
    _load_env_if_present()


@cli.command("env-dump")
def env_dump() -> None:
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
@click.option("--file", "file_path", type=click.Path(exists=True, dir_okay=False))
def handle_event(file_path: str | None) -> None:
    payload = (
        json.loads(Path(file_path).read_text())
        if file_path
        else json.loads(click.get_text_stream("stdin").read())
    )
    click.echo(json.dumps(process_event_and_apply_plan_moves(payload), indent=2))


@cli.command("sync-usage")
@click.option("--since")
@click.option("--until")
def sync_usage(since: str | None, until: str | None) -> None:
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
@click.option("--api-key", "api_key_id", required=True)
def promote(api_key_id: str) -> None:
    svc = build_service(include_usage=False)
    click.echo(json.dumps(svc.promote(api_key_id), indent=2))


@cli.command("demote")
@click.option("--api-key", "api_key_id", required=True)
def demote(api_key_id: str) -> None:
    svc = build_service(include_usage=False)
    click.echo(json.dumps(svc.demote(api_key_id), indent=2))


if __name__ == "__main__":
    cli()
