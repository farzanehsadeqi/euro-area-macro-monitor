"""Shared HTTP helper: one place for timeouts and retries."""

import time

import requests

USER_AGENT = "euro-area-macro-monitor (academic portfolio project)"
RETRY_ON = {429, 500, 502, 503, 504}


def get(url, params=None, max_tries=3):
    """GET a URL, retrying transient failures.

    Returns the response object. Retries on network errors and on server-side
    status codes, but not on client errors like 400 or 404, which will not fix
    themselves and are handled by the caller.
    """
    headers = {"User-Agent": USER_AGENT}
    last_error = None

    for attempt in range(1, max_tries + 1):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
        except requests.RequestException as exc:
            last_error = exc
            if attempt < max_tries:
                time.sleep(2 ** attempt)
                continue
            raise

        if response.status_code in RETRY_ON and attempt < max_tries:
            time.sleep(2 ** attempt)
            continue

        return response

    raise last_error