# augint-billing-lib (full library bundle)


**One package (`augint_billing_lib`) + one CLI (`augint`)**. All runtime logic lives here; IaC should be thin shims.

## What it contains
- Core: `BillingService` with Stripe/DynamoDB/API Gateway usage orchestration
- Adapters: Stripe, DynamoDB repo, API Gateway usage, API Gateway plan admin
- Bootstrap: env + Secrets Manager wiring, CFN output discovery, plan move dispatcher
- CLI: `augint` with `env-dump`, `handle-event`, `sync-usage`, `promote`, `demote`, and optional `deploy`/`delete` helpers

## Env (uses your names; no new required keys)
**Required:** `STACK_NAME`, `AWS_REGION`, `STRIPE_SECRET_KEY`  
**Optional:** `API_USAGE_PRODUCT_ID`, `STRIPE_SECRET_ARN`, `TABLE_NAME`, `FREE_USAGE_PLAN_ID`, `METERED_USAGE_PLAN_ID`

## Typical local flows
```bash
# 0) Install deps in your Poetry project: click, python-dotenv, boto3, stripe
# 1) Show env the CLI sees
poetry run augint env-dump

# 2) Simulate a Stripe event (and move keys between FREE_10K/METERED inside AWS)
poetry run augint handle-event --file ./fixtures/setup_intent.succeeded.json

# 3) Report last hour usage to Stripe (test mode)
poetry run augint sync-usage

# 4) Promote/demote a key (Stripe side)
poetry run augint promote --api-key ABC123
poetry run augint demote --api-key ABC123
```

## Deploy helpers (optional)
```bash
poetry run augint deploy --infra ../augint-billing-infra --params template-params.sample.json
poetry run augint delete
```

## Wire the CLI
Add to your `pyproject.toml`:
```toml
[project.scripts]
augint = "augint_billing_lib.cli:cli"
```
Install: `poetry install`
