"""NSE trading-holiday calendar.

Primary source is NSE's holiday-master API, which needs the www.nseindia.com cookie dance and
is blocked from some networks (it was blocked from the environment this was developed in).
The bundled nse_trading_holidays.csv is a hand-entered fallback; the validation report
compares it against the dates that actually have / lack files, so errors in it show up as
flags rather than being hidden.
"""
from __future__ import annotations

import datetime as dt
import logging

import pandas as pd

from . import config
from .nse_session import NSEClient

log = logging.getLogger(__name__)


def bundled_holidays() -> pd.DataFrame:
    df = pd.read_csv(config.HOLIDAYS_CSV, dtype=str).fillna("")
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df["source"] = "bundled"
    return df


def fetch_nse_holidays(client: NSEClient | None = None) -> pd.DataFrame | None:
    """Best effort: NSE's holiday API for the current year ('FO' segment). None on failure."""
    try:
        client = client or NSEClient(delay=1.0, max_retries=2, timeout=20)
        status, content = client.get(config.NSE_HOLIDAY_API)
        if status != 200 or not content:
            log.warning("holiday API returned %s", status)
            return None
        import json
        data = json.loads(content)
        rows = data.get("FO") or data.get("CM") or []
        out = pd.DataFrame([{"date": pd.to_datetime(r["tradingDate"]).date(),
                             "description": r.get("description", ""), "note": "", "source": "nse_api"}
                            for r in rows])
        return out if not out.empty else None
    except Exception as e:  # noqa: BLE001
        log.warning("holiday API fetch failed: %s", e)
        return None


def holiday_calendar(try_api: bool = True) -> pd.DataFrame:
    df = bundled_holidays()
    if try_api:
        api = fetch_nse_holidays()
        if api is not None:
            df = pd.concat([df[~df["date"].isin(api["date"])], api], ignore_index=True)
    return df.sort_values("date").reset_index(drop=True)
