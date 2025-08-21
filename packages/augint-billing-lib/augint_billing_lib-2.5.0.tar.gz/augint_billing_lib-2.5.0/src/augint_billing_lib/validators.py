from typing import Any


def require_keys(d: dict[str, Any], keys: list[str]) -> dict[str, Any]:
    missing = [k for k in keys if d.get(k) in (None, "", [])]
    if missing:
        raise ValueError(f"Missing required keys: {missing}")
    return d
