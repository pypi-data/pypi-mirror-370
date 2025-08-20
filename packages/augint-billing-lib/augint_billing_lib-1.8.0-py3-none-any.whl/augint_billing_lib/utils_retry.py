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
