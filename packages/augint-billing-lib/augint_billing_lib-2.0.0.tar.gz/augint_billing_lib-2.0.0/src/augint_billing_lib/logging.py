import json
import logging
import os
from typing import Any

_logger = logging.getLogger("augint.billing")
if not _logger.handlers:
    h = logging.StreamHandler()
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    h.setFormatter(fmt)
    _logger.addHandler(h)
    _logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))


def log_event(level: str, msg: str, **kv: Any) -> None:
    rec = {"msg": msg, **kv}
    getattr(_logger, level.lower(), _logger.info)(json.dumps(rec))


def log_metric(name: str, value: float, dims: dict[str, str] | None = None) -> None:
    # AWS EMF-compatible payload
    payload = {
        "_aws": {
            "Timestamp": int(__import__("time").time() * 1000),
            "CloudWatchMetrics": [
                {
                    "Namespace": "AugInt/Billing",
                    "Dimensions": [list((dims or {}).keys())],
                    "Metrics": [{"Name": name, "Unit": "Count"}],
                }
            ],
        },
        name: value,
    }
    if dims:
        payload.update(dims)
    _logger.info(json.dumps(payload))
