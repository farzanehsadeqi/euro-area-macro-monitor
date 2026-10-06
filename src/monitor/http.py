"""Shared HTTP layer: one place for retries, timeouts, and error handling."""

import logging
import time

import requests

logger = logging.getLogger(__name__)

USER_AGENT = "euro-area-macro-monitor (academic portfolio project)"
RETRY_ON = {429, 500, 502, 503, 504}


def get(url, params=None, timeout=30, max_tries=3, backoff=2.0):
    """GET a URL, retrying transient failures with exponential backoff.

    Retries on connection errors and on the HTTP status codes in RETRY_ON.
    Does not retry client errors such as 404, which will not fix themselves.
    Raises requests.HTTPError if all attempts fail.
    """
    headers = {"User-Agent": USER_AGENT}

    for attempt in range(1, max_tries + 1):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=timeout)
        except requests.RequestException as exc:
            if attempt == max_tries:
                raise
            wait = backoff ** attempt
            logger.warning("Request failed (%s). Retry %d/%d in %.0fs",
                           exc, attempt, max_tries, wait)
            time.sleep(wait)
            continue

        if response.status_code == 200:
            return response

        if response.status_code in RETRY_ON and attempt < max_tries:
            wait = float(response.headers.get("Retry-After", backoff ** attempt))
            logger.warning("HTTP %d. Retry %d/%d in %.0fs",
                           response.status_code, attempt, max_tries, wait)
            time.sleep(wait)
            continue

        response.raise_for_status()

    raise RuntimeError("Unreachable")