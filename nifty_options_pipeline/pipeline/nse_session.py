"""HTTP client for NSE archives: browser-like headers, cookie warm-up, retry with backoff,
and a polite fixed delay between requests."""
from __future__ import annotations

import logging
import random
import time

import requests

from . import config

log = logging.getLogger(__name__)

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Referer": "https://www.nseindia.com/",
}

RETRYABLE = {403, 429, 500, 502, 503, 504}


class DownloadError(RuntimeError):
    pass


class NSEClient:
    """requests.Session wrapper.

    get() returns (status_code, content). 404 is returned (not raised) because NSE answers
    404 for weekends/holidays and the caller treats that as a normal outcome.
    """

    def __init__(self, delay: float = 1.0, max_retries: int = 5, timeout: int = 60):
        self.delay = delay
        self.max_retries = max_retries
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(BROWSER_HEADERS)
        self._last_request = 0.0
        self.warm_up()

    def warm_up(self) -> None:
        """Visit the NSE home page to pick up cookies. Failure is logged, not fatal: the
        archive hosts have served files without cookies in every probe so far."""
        try:
            r = self.session.get(config.NSE_HOME, timeout=self.timeout)
            log.info("warm-up %s -> %s (%d cookies)", config.NSE_HOME, r.status_code,
                     len(self.session.cookies))
        except requests.RequestException as e:  # noqa: BLE001
            log.warning("warm-up failed: %s", e)

    def _throttle(self) -> None:
        wait = self.delay - (time.monotonic() - self._last_request)
        if wait > 0:
            time.sleep(wait)
        self._last_request = time.monotonic()

    def get(self, url: str) -> tuple[int, bytes | None]:
        last_err: str = ""
        for attempt in range(self.max_retries):
            self._throttle()
            try:
                r = self.session.get(url, timeout=self.timeout)
            except requests.RequestException as e:  # noqa: BLE001
                last_err = f"{type(e).__name__}: {e}"
                log.warning("attempt %d %s -> %s", attempt + 1, url, last_err)
            else:
                if r.status_code == 200:
                    return 200, r.content
                if r.status_code == 404:
                    return 404, None
                last_err = f"HTTP {r.status_code}"
                log.warning("attempt %d %s -> %s", attempt + 1, url, last_err)
                if r.status_code not in RETRYABLE:
                    return r.status_code, None
                if r.status_code in (403, 429):
                    self.warm_up()
            backoff = min(60.0, (2 ** attempt) + random.uniform(0, 1))
            time.sleep(backoff)
        raise DownloadError(f"giving up on {url} after {self.max_retries} attempts: {last_err}")
