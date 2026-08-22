"""
Download NSE full security bhavcopy (sec_bhavdata_full) for the last N days.

Source: https://archives.nseindia.com/products/content/sec_bhavdata_full_DDMMYYYY.csv
This is NSE's official end-of-day "Security-wise Price Volume & Deliverable
Position" report -- the same dataset served behind
https://www.nseindia.com/report-detail/eq_security

Two quirks of that archive are handled here:

1. The host answers 403 both for "no such file" (weekend / trading holiday)
   AND for throttling. They are only distinguishable by retrying, so every 403
   is retried with backoff and a date is declared unavailable only after the
   full retry budget is spent.
2. On some trading holidays the archive serves the PREVIOUS session's file
   under the holiday's filename. Each download is therefore checked against
   the date inside the file and discarded when it does not match.
"""

import argparse
import concurrent.futures as cf
import datetime as dt
import os
import random
import sys
import time

import requests

BASE_URL = "https://archives.nseindia.com/products/content/sec_bhavdata_full_{d}.csv"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "text/csv,text/plain,*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/report-detail/eq_security",
}

RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "raw_bhavcopy")


def weekdays(start, end):
    days, d = [], start
    while d <= end:
        if d.weekday() < 5:
            days.append(d)
        d += dt.timedelta(days=1)
    return days


def file_date(text):
    """Read DATE1 out of the first data row, e.g. '21-Aug-2026'."""
    try:
        row = text.splitlines()[1]
        return dt.datetime.strptime(row.split(",")[2].strip(), "%d-%b-%Y").date()
    except (IndexError, ValueError):
        return None


def fetch_one(day, retries=6):
    stamp = day.strftime("%d%m%Y")
    path = os.path.join(RAW_DIR, f"sec_bhavdata_full_{stamp}.csv")
    if os.path.exists(path) and os.path.getsize(path) > 50_000:
        return day, "cached"

    url = BASE_URL.format(d=stamp)
    for attempt in range(retries):
        if attempt:
            time.sleep(min(2 ** attempt, 30) + random.uniform(0, 1.5))
        try:
            r = requests.get(url, headers=HEADERS, timeout=45)
        except requests.RequestException:
            continue
        if r.status_code != 200 or not r.text.lstrip().upper().startswith("SYMBOL"):
            continue  # 403 == throttled OR no file; only retries tell them apart
        if file_date(r.text) != day:
            # Archive served a stale copy of an earlier session -> holiday.
            return day, "holiday"
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(r.text)
        return day, "downloaded"
    return day, "unavailable"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=366, help="lookback window in calendar days")
    ap.add_argument("--end", default=None, help="end date YYYY-MM-DD (default: today)")
    ap.add_argument("--workers", type=int, default=3)
    args = ap.parse_args()

    os.makedirs(RAW_DIR, exist_ok=True)
    end = dt.date.fromisoformat(args.end) if args.end else dt.date.today()
    start = end - dt.timedelta(days=args.days)
    days = weekdays(start, end)
    print(f"Window {start} -> {end}: {len(days)} weekday candidates", flush=True)

    counts = {"downloaded": 0, "cached": 0, "holiday": 0, "unavailable": 0}
    unavailable = []
    with cf.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(fetch_one, d) for d in days]
        for i, fut in enumerate(cf.as_completed(futures), 1):
            day, status = fut.result()
            counts[status] += 1
            if status == "unavailable":
                unavailable.append(day)
            if i % 25 == 0:
                print(f"  {i}/{len(days)} ... {counts}", flush=True)

    print(f"DONE {counts}", flush=True)
    if unavailable:
        print("UNAVAILABLE (holiday or archive gap): "
              + ", ".join(d.isoformat() for d in sorted(unavailable)), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
