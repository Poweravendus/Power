"""Paths, date ranges and URL templates for the NIFTY options pipeline.

Facts below were verified by probing NSE archives on 2026-11-21:
  * Old-format F&O bhavcopy (foDDMMMYYYYbhav.csv.zip) exists up to and including 2024-07-05.
    From 2024-07-08 onward NSE only publishes the UDiFF file.
  * UDiFF F&O bhavcopy (BhavCopy_NSE_FO_0_0_0_YYYYMMDD_F_0000.csv.zip) exists from 2024-01-01
    onward (NSE back-filled January-July 2024), so there is an overlap window used for
    cross-format reconciliation in the validation report.
  * Daily index close file ind_close_all_DDMMYYYY.csv contains both "Nifty 50" and "India VIX".
  * Both archive hosts (archives.nseindia.com and nsearchives.nseindia.com) serve both the
    historical and the new paths; one is used as a fallback for the other.
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
RAW_FO_DIR = RAW_DIR / "fo"
RAW_INDEX_DIR = RAW_DIR / "indices"
PROCESSED_DIR = DATA_DIR / "processed"
FO_PARQUET_DIR = PROCESSED_DIR / "nifty_fo"
SPOT_VIX_PARQUET = PROCESSED_DIR / "nifty_spot_vix.parquet"
EXPIRY_CALENDAR_CSV = PROCESSED_DIR / "expiry_calendar.csv"
SAMPLE_DIR = DATA_DIR / "sample"
MANIFEST_CSV = RAW_DIR / "download_manifest.csv"
HOLIDAYS_CSV = ROOT / "nse_trading_holidays.csv"
REPORT_MD = ROOT / "reports" / "validation_report.md"
LOG_DIR = ROOT / "logs"

START_DATE = dt.date(2019, 1, 1)

# Format cutover (verified from the archives, see module docstring).
OLD_FORMAT_LAST_DATE = dt.date(2024, 7, 5)
UDIFF_FIRST_DATE = dt.date(2024, 7, 8)
UDIFF_BACKFILL_START = dt.date(2024, 1, 1)   # UDiFF also exists from here (overlap window)
# Between these two dates both formats are tried so the cutover is confirmed from the data
# on every run rather than hard-coded only.
CUTOVER_PROBE_START = dt.date(2024, 6, 1)
CUTOVER_PROBE_END = dt.date(2024, 8, 31)

SYMBOL = "NIFTY"
INDEX_NAME_SPOT = "Nifty 50"
INDEX_NAME_VIX = "India VIX"

HOSTS = ["https://archives.nseindia.com", "https://nsearchives.nseindia.com"]
NSE_HOME = "https://www.nseindia.com/"
NSE_HOLIDAY_API = "https://www.nseindia.com/api/holiday-master?type=trading"

MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


def old_fo_path(d: dt.date) -> str:
    return f"/content/historical/DERIVATIVES/{d.year}/{MONTHS[d.month - 1]}/fo{d:%d}{MONTHS[d.month - 1]}{d.year}bhav.csv.zip"


def udiff_fo_path(d: dt.date) -> str:
    return f"/content/fo/BhavCopy_NSE_FO_0_0_0_{d:%Y%m%d}_F_0000.csv.zip"


def mkt_report_path(d: dt.date) -> str:
    """F&O 'market activity report' zip: per-contract OHLC/OI/volume but NO settlement price.
    Only used to fill weekdays where the bhavcopy is missing from NSE's archive (e.g. 2021-03-30)."""
    return f"/archives/fo/mkt/fo{d:%d%m%Y}.zip"


def index_close_path(d: dt.date) -> str:
    return f"/content/indices/ind_close_all_{d:%d%m%Y}.csv"


# Standard output schema (column order of the Parquet files).
SCHEMA_COLUMNS = [
    "trade_date", "symbol", "instrument", "expiry", "strike", "option_type",
    "open", "high", "low", "close", "settle", "contracts_traded", "open_interest",
    "underlying", "vix_close", "is_monthly_expiry", "dte",
    # helper columns (not in the requested schema, kept because they are cheap and useful)
    "is_last_expiry_in_month", "underlying_source", "source_format",
]
