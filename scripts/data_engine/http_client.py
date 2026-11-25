"""Reliable HTTP client with timeouts, retries, backoff, and rate-limit handling."""

from __future__ import annotations

import json
import logging
import time
import urllib.error
import urllib.request
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger("linacre.data_engine.http")

DEFAULT_TIMEOUT = 15
DEFAULT_RETRIES = 3
DEFAULT_BACKOFF = 1.5
USER_AGENT = "Linacre-LLM-Hub/5.0 (+https://github.com/DLinacre/Linacre-LLM-Benchmarks)"


class HttpFetchError(Exception):
    """Raised when an HTTP request fails after retries."""

    def __init__(self, message: str, status_code: Optional[int] = None, url: str = ""):
        super().__init__(message)
        self.status_code = status_code
        self.url = url


def fetch_json(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
    backoff: float = DEFAULT_BACKOFF,
) -> Tuple[Any, Dict[str, str]]:
    """Fetch JSON from an official API endpoint with retry and rate-limit handling."""
    req_headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }
    if headers:
        req_headers.update(headers)

    last_error: Optional[Exception] = None

    for attempt in range(1, retries + 1):
        req = urllib.request.Request(url, headers=req_headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8")
                resp_headers = {k.lower(): v for k, v in resp.headers.items()}
                return json.loads(raw), resp_headers
        except urllib.error.HTTPError as exc:
            last_error = HttpFetchError(
                f"HTTP {exc.code} fetching {url}: {exc.reason}",
                status_code=exc.code,
                url=url,
            )
            # Do not retry permanent client errors except 429 rate-limit
            if exc.code in (400, 401, 403, 404):
                raise last_error from exc
            retry_after = exc.headers.get("Retry-After") if exc.headers else None
            sleep_for = float(retry_after) if retry_after and retry_after.isdigit() else backoff * attempt
            logger.warning("HTTP %s on %s (attempt %d/%d), retrying in %.1fs", exc.code, url, attempt, retries, sleep_for)
            if attempt < retries:
                time.sleep(min(sleep_for, 10.0))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = HttpFetchError(f"Network/parse error fetching {url}: {exc}", url=url)
            logger.warning("Error on %s (attempt %d/%d): %s", url, attempt, retries, exc)
            if attempt < retries:
                time.sleep(min(backoff * attempt, 10.0))

    assert last_error is not None
    raise last_error
