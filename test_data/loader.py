import json
from functools import lru_cache
from pathlib import Path

_ROOT = Path(__file__).resolve().parent


@lru_cache
def _load(env: str) -> dict:
    path = _ROOT / f"{env}.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_negative_auth_payloads(env: str) -> list:
    return _load(env)["auth"]["negative_payloads"]


def load_negative_create_booking_payloads(env: str) -> list:
    return _load(env)["booking"]["negative_create_payloads"]
