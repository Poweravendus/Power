"""Fetch daily OHLCV for NSE mid/small/micro-cap universe from Yahoo Finance.

Universe = Nifty Midcap 150 + Smallcap 250 + Microcap 250 constituents
(current lists from NSE archives), plus Nifty 50 / Nifty Midcap 150 index
for environment analysis. Data cached as parquet, one file per symbol.

Note: using *current* constituents introduces survivorship bias — results
will overstate absolute returns. Relative comparisons (which conditions the
setup works in, shakeout behaviour) are far less affected.
"""
import io
import json
import sys
import time
from pathlib import Path

import pandas as pd
import requests

CACHE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data")
LIST_DIR = Path(sys.argv[2]) if len(sys.argv) > 2 else CACHE
CACHE.mkdir(parents=True, exist_ok=True)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

SEGMENTS = {
    "ind_niftymidcap150list.csv": "midcap",
    "ind_niftysmallcap250list.csv": "smallcap",
    "ind_niftymicrocap250_list.csv": "microcap",
}

INDICES = {"^NSEI": "NIFTY50", "^NSEMDCP50": "NIFTY_MIDCAP50", "^CNXSC": "NIFTY_SMALLCAP100"}


def load_universe():
    rows = []
    for fname, seg in SEGMENTS.items():
        df = pd.read_csv(LIST_DIR / fname)
        for sym in df["Symbol"]:
            rows.append({"symbol": sym, "segment": seg})
    uni = pd.DataFrame(rows).drop_duplicates("symbol")
    return uni


def fetch_chart(session, yahoo_symbol, rng="12y"):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_symbol}"
    r = session.get(url, params={"range": rng, "interval": "1d",
                                 "events": "div,split"}, timeout=30)
    if r.status_code == 429:
        raise RuntimeError("rate limited")
    r.raise_for_status()
    res = r.json()["chart"]["result"][0]
    ts = res.get("timestamp")
    if not ts:
        return None
    q = res["indicators"]["quote"][0]
    adj = res["indicators"].get("adjclose", [{}])[0].get("adjclose")
    df = pd.DataFrame({
        "date": pd.to_datetime(ts, unit="s", utc=True).tz_convert("Asia/Kolkata").normalize().tz_localize(None),
        "open": q["open"], "high": q["high"], "low": q["low"],
        "close": q["close"], "volume": q["volume"],
        "adjclose": adj if adj is not None else q["close"],
    }).dropna(subset=["close"])
    # adjust OHLC by the adjclose ratio so history is split/bonus-consistent
    ratio = df["adjclose"] / df["close"]
    for c in ("open", "high", "low", "close"):
        df[c] = df[c] * ratio
    df = df.drop(columns=["adjclose"]).drop_duplicates("date").set_index("date").sort_index()
    return df


def main():
    uni = load_universe()
    uni.to_csv(CACHE / "universe.csv", index=False)
    session = requests.Session()
    session.headers.update({"User-Agent": UA})

    targets = [(s, s.replace("&", "%26") + ".NS") for s in uni["symbol"]]
    targets += [(name, ysym) for ysym, name in INDICES.items()]

    ok, fail = 0, []
    for i, (name, ysym) in enumerate(targets):
        out = CACHE / f"{name.replace('&','_')}.parquet"
        if out.exists():
            ok += 1
            continue
        for attempt in range(4):
            try:
                df = fetch_chart(session, ysym)
                if df is None or len(df) < 260:
                    fail.append((name, "too short" if df is not None else "no data"))
                else:
                    df.to_parquet(out)
                    ok += 1
                break
            except Exception as e:  # noqa: BLE001
                if attempt == 3:
                    fail.append((name, str(e)[:80]))
                else:
                    time.sleep(3 * (attempt + 1))
        time.sleep(0.35)
        if (i + 1) % 50 == 0:
            print(f"{i+1}/{len(targets)} done, ok={ok}, fail={len(fail)}", flush=True)

    (CACHE / "fetch_failures.json").write_text(json.dumps(fail, indent=1))
    print(f"FINISHED ok={ok} fail={len(fail)}")
    for f in fail[:20]:
        print("  FAIL", f)


if __name__ == "__main__":
    main()
