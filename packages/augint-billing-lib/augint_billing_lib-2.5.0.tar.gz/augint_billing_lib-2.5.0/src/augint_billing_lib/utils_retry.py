"""Retry utilities with exponential backoff and jitter.

This module provides a decorator for adding retry logic to functions that
may fail due to transient errors. It implements exponential backoff with
jitter to avoid thundering herd problems.

The retry mechanism is particularly useful for:
    - Network API calls that may fail temporarily
    - Database operations during brief outages
    - Rate-limited operations that need backoff
    - Any operation with transient failure modes

Example:
    Basic retry usage::

        from augint_billing_lib.utils_retry import retry
        import requests

        @retry((requests.RequestException,), tries=3)
        def fetch_data(url):
            response = requests.get(url)
            response.raise_for_status()
            return response.json()

        # Will retry up to 3 times on request errors
        data = fetch_data("https://api.example.com/data")

    Custom retry parameters::

        @retry(
            (ConnectionError, TimeoutError),
            tries=5,
            base=0.5,   # Start with 0.5 second delay
            cap=10.0,   # Max 10 second delay
            jitter=0.2  # Add up to 0.2 seconds random jitter
        )
        def connect_to_service():
            # Connection logic here
            pass

Note:
    Uses cryptographically secure random number generation for jitter
    to ensure unpredictable retry patterns in security-sensitive contexts.
"""

import secrets
import time
from collections.abc import Callable
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def retry(
    exceptions: tuple[type[BaseException], ...],
    tries: int = 3,
    base: float = 0.2,
    cap: float = 2.0,
    jitter: float = 0.1,
) -> Callable[[F], F]:
    """Decorator to add retry logic with exponential backoff and jitter.

    Wraps a function to automatically retry on specified exceptions using
    exponential backoff with random jitter. This helps avoid thundering
    herd problems and provides resilience against transient failures.

    Args:
        exceptions: Tuple of exception types to catch and retry on
        tries: Maximum number of attempts (including the first call)
        base: Initial delay in seconds before first retry
        cap: Maximum delay in seconds (caps exponential growth)
        jitter: Maximum random jitter to add to delay (in seconds)

    Returns:
        Decorated function that implements retry logic

    Raises:
        The last exception if all retry attempts fail

    Example:
        Retry on specific AWS errors::

            import botocore.exceptions

            @retry(
                (botocore.exceptions.ClientError,),
                tries=5,
                base=0.5
            )
            def write_to_dynamodb(table, item):
                table.put_item(Item=item)

        Retry with custom backoff for rate limiting::

            @retry(
                (RateLimitError,),
                tries=10,
                base=1.0,   # Start with 1 second
                cap=30.0,   # Max 30 seconds between retries
                jitter=0.5  # Add 0-0.5 seconds randomness
            )
            def call_rate_limited_api():
                # API call logic
                pass

    Algorithm:
        The delay between retries follows this pattern:
        1. First retry: base + random(0, jitter)
        2. Second retry: min(cap, base * 2) + random(0, jitter)
        3. Third retry: min(cap, base * 4) + random(0, jitter)
        ... and so on with exponential growth

    Note:
        The function uses secrets.SystemRandom() for cryptographically
        secure random jitter, which is important in security-sensitive
        contexts to prevent timing attacks.

    Warning:
        Be careful with the exceptions tuple - catching too broad
        exceptions (like Exception) can mask programming errors.
        Only catch exceptions that represent transient failures.
    """

    def deco(fn: F) -> F:
        def wrapper(*a: Any, **k: Any) -> Any:
            t = tries
            delay = base
            while True:
                try:
                    return fn(*a, **k)
                except exceptions:
                    t -= 1
                    if t <= 0:
                        raise
                    time.sleep(min(cap, delay + secrets.SystemRandom().uniform(0, jitter)))
                    delay *= 2

        return wrapper  # type: ignore[return-value]

    return deco
