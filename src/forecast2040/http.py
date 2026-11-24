"""HTTP access.

One session per run, retries with backoff on transient failures, and a user
agent that identifies the project. Public statistical APIs block anonymous
bulk clients, so the agent string is not decoration.
"""

from __future__ import annotations

import json
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import Settings


class FetchError(RuntimeError):
    """Raised when a source cannot be retrieved after retries."""


def build_session(settings: Settings) -> requests.Session:
    """Create a session with retries on 429, 500, 502, 503 and 504."""
    retry = Retry(
        total=settings.max_retries,
        backoff_factor=settings.backoff_s,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_maxsize=8)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update(
        {
            "User-Agent": settings.user_agent,
            "Accept": "application/json, text/csv, text/plain, */*",
        }
    )
    return session


def get_text(
    session: requests.Session,
    url: str,
    params: dict[str, Any] | None = None,
    timeout: int = 30,
) -> str:
    """Fetch a URL and return the body as text, raising on a non-200 status."""
    try:
        response = session.get(url, params=params, timeout=timeout)
    except requests.RequestException as exc:
        raise FetchError(f"request failed for {url}: {exc}") from exc
    if response.status_code != 200:
        raise FetchError(f"{url} returned HTTP {response.status_code}")
    return response.text


def get_json(
    session: requests.Session,
    url: str,
    params: dict[str, Any] | None = None,
    timeout: int = 30,
) -> Any:
    """Fetch a URL and decode JSON."""
    text = get_text(session, url, params, timeout)
    try:
        return json.loads(text)
    except ValueError as exc:
        raise FetchError(f"{url} did not return valid JSON") from exc
