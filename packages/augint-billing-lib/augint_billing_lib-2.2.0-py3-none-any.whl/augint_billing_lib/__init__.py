"""Augint Billing Library.

A production-ready Python library for Stripe-powered usage-based billing with AWS integration.
This library provides seamless integration between Stripe payment processing and AWS API Gateway
usage tracking, designed for SaaS applications with tiered pricing models.

Key Features:
    - Usage-based billing with automatic Stripe synchronization
    - Tiered pricing with free and metered plans
    - Automatic plan transitions based on payment status
    - Real-time usage reporting with hourly synchronization
    - Clean architecture using ports & adapters pattern
    - Production-ready with retry logic and circuit breakers

Example:
    Basic usage with the high-level API::

        from augint_billing_lib import bootstrap

        # Process a Stripe webhook event
        result = bootstrap.process_event_and_apply_plan_moves({
            "type": "payment_method.attached",
            "data": {"object": {"customer": "cus_123"}}
        })

        # Report usage to Stripe
        reports = bootstrap.report_current_hour_usage()

    Using the service directly::

        from augint_billing_lib import BillingService, build_service

        # Build service with dependencies
        service = build_service()

        # Handle Stripe events
        action = service.handle_stripe_event(event)

        # Report usage for a time window
        reports = service.reconcile_usage_window(since, until)

Modules:
    bootstrap: Dependency injection and Lambda handler setup
    service: Core business logic and orchestration
    models: Data models and validation
    ports: Abstract interfaces for external dependencies
    adapters: Concrete implementations for AWS and Stripe
    cli: Command-line interface for testing and administration
"""

from .bootstrap import build_service as build_service
from .bootstrap import process_event_and_apply_plan_moves as process_event_and_apply_plan_moves
from .bootstrap import report_current_hour_usage as report_current_hour_usage
from .bootstrap import report_usage_window as report_usage_window
from .models import Link as Link
from .service import BillingService as BillingService

__version__ = "2.2.0"

__all__ = [
    "BillingService",
    "Link",
    "build_service",
    "process_event_and_apply_plan_moves",
    "report_current_hour_usage",
    "report_usage_window",
]
