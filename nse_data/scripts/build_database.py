"""
Build a consolidated OHLCV database + Excel workbook from the downloaded
NSE full bhavcopy files.

Outputs (in nse_data/output/):
  * nse_ohlcv.db                -- SQLite database (table `ohlcv`, view `v_symbol_summary`)
  * NSE_OHLCV_Database.xlsx     -- one workbook: README, Master_Data, Summary, one sheet per symbol
  * nse_ohlcv_master.csv        -- flat CSV of the same master table
"""

import datetime as dt
import glob
import os
import sqlite3
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(ROOT, "raw_bhavcopy")
OUT_DIR = os.path.join(ROOT, "output")
SYMBOLS_FILE = os.path.join(ROOT, "scripts", "symbols.txt")
ALIASES_FILE = os.path.join(ROOT, "scripts", "aliases.txt")

DB_PATH = os.path.join(OUT_DIR, "nse_ohlcv.db")
XLSX_PATH = os.path.join(OUT_DIR, "NSE_OHLCV_Database.xlsx")
CSV_PATH = os.path.join(OUT_DIR, "nse_ohlcv_master.csv")

NUM_COLS = [
    "PREV_CLOSE", "OPEN_PRICE", "HIGH_PRICE", "LOW_PRICE", "LAST_PRICE",
    "CLOSE_PRICE", "AVG_PRICE", "TTL_TRD_QNTY", "TURNOVER_LACS",
    "NO_OF_TRADES", "DELIV_QTY", "DELIV_PER",
]

RENAME = {
    "SYMBOL": "Symbol",
    "SERIES": "Series",
    "DATE1": "Date",
    "PREV_CLOSE": "Prev_Close",
    "OPEN_PRICE": "Open",
    "HIGH_PRICE": "High",
    "LOW_PRICE": "Low",
    "LAST_PRICE": "Last",
    "CLOSE_PRICE": "Close",
    "AVG_PRICE": "VWAP",
    "TTL_TRD_QNTY": "Volume",
    "TURNOVER_LACS": "Turnover_Lacs",
    "NO_OF_TRADES": "No_of_Trades",
    "DELIV_QTY": "Delivery_Qty",
    "DELIV_PER": "Delivery_Pct",
}

FINAL_COLS = [
    "Symbol", "NSE_Ticker", "Traded_As", "Series", "Date", "Prev_Close", "Open",
    "High", "Low", "Last", "Close", "VWAP", "Volume", "Turnover_Lacs",
    "No_of_Trades", "Delivery_Qty", "Delivery_Pct",
]


def load_symbols():
    with open(SYMBOLS_FILE) as fh:
        return [ln.strip().upper() for ln in fh if ln.strip()]


def load_aliases():
    """CURRENT_SYMBOL -> [old tickers]; returns old->current lookup."""
    old_to_new = {}
    if not os.path.exists(ALIASES_FILE):
        return old_to_new
    with open(ALIASES_FILE) as fh:
        for ln in fh:
            ln = ln.split("#", 1)[0].strip()
            if not ln or "=" not in ln:
                continue
            new, olds = ln.split("=", 1)
            for old in olds.split(","):
                old = old.strip().upper()
                if old:
                    old_to_new[old] = new.strip().upper()
    return old_to_new


def read_bhavcopy(path, wanted):
    df = pd.read_csv(path, skipinitialspace=True, dtype=str)
    df.columns = [c.strip().upper() for c in df.columns]
    for c in df.columns:
        df[c] = df[c].astype(str).str.strip()
    df = df[df["SYMBOL"].isin(wanted)]
    # Keep the regular rolling-settlement equity series only.
    df = df[df["SERIES"].isin(["EQ", "BE", "BZ", "SM", "ST"])]
    return df


def build_master(symbols, old_to_new):
    files = sorted(glob.glob(os.path.join(RAW_DIR, "sec_bhavdata_full_*.csv")))
    if not files:
        sys.exit("No bhavcopy files found -- run download_bhavcopy.py first.")
    wanted = set(symbols) | set(old_to_new)
    frames = [read_bhavcopy(p, wanted) for p in files]
    df = pd.concat(frames, ignore_index=True)

    for c in NUM_COLS:
        df[c] = pd.to_numeric(df[c].replace({"-": None, "": None, "nan": None}), errors="coerce")

    df["DATE1"] = pd.to_datetime(df["DATE1"], format="%d-%b-%Y")
    df = df.rename(columns=RENAME)
    df["Traded_As"] = df["Symbol"]
    df["Symbol"] = df["Symbol"].replace(old_to_new)
    df["NSE_Ticker"] = "NSE:" + df["Symbol"]
    df = df[FINAL_COLS]
    df = df.sort_values(["Symbol", "Date"]).drop_duplicates(["Symbol", "Series", "Date"])
    return df.reset_index(drop=True)


def check_session_continuity(df):
    """Every row's PREV_CLOSE should equal the previous row's CLOSE.

    A market-wide mismatch on one date means a whole session is missing from
    the download (NSE runs occasional live weekend sessions). A mismatch on a
    single symbol means a corporate action -- prices in bhavcopy are NOT
    split/bonus adjusted, but NSE does restate PREV_CLOSE across an ex-date.
    """
    d = df.sort_values(["Symbol", "Date"]).copy()
    d["prior_close"] = d.groupby("Symbol")["Close"].shift(1)
    d["gap"] = (d["Prev_Close"] / d["prior_close"] - 1).abs()
    breaks = d[d["gap"] > 0.01].dropna(subset=["gap"])

    per_date = breaks.groupby("Date").size()
    symbols_live = d.groupby("Date")["Symbol"].nunique()
    missing_sessions = [dte for dte, n in per_date.items() if n >= 0.8 * symbols_live[dte]]
    corp_actions = breaks[~breaks["Date"].isin(missing_sessions)]
    return missing_sessions, corp_actions[["Symbol", "Date", "prior_close", "Prev_Close"]]


def build_summary(df):
    rows = []
    for sym, g in df.groupby("Symbol", sort=True):
        g = g.sort_values("Date")
        first, last = g.iloc[0], g.iloc[-1]
        hi_row = g.loc[g["High"].idxmax()]
        lo_row = g.loc[g["Low"].idxmin()]
        first_close, last_close = first["Close"], last["Close"]
        ret = (last_close / first_close - 1) * 100 if first_close else np.nan
        rows.append({
            "Symbol": sym,
            "NSE_Ticker": "NSE:" + sym,
            "Series": ", ".join(sorted(g["Series"].unique())),
            "Traded_As": ", ".join(sorted(g["Traded_As"].unique())),
            "Records": len(g),
            "First_Date": first["Date"],
            "Last_Date": last["Date"],
            "First_Close": first_close,
            "Last_Close": last_close,
            "Period_Return_Pct": ret,
            "52W_High": hi_row["High"],
            "52W_High_Date": hi_row["Date"],
            "52W_Low": lo_row["Low"],
            "52W_Low_Date": lo_row["Date"],
            "Pct_Below_52W_High": (last_close / hi_row["High"] - 1) * 100 if hi_row["High"] else np.nan,
            "Pct_Above_52W_Low": (last_close / lo_row["Low"] - 1) * 100 if lo_row["Low"] else np.nan,
            "Avg_Daily_Volume": g["Volume"].mean(),
            "Median_Daily_Volume": g["Volume"].median(),
            "Avg_Daily_Turnover_Lacs": g["Turnover_Lacs"].mean(),
            "Total_Turnover_Cr": g["Turnover_Lacs"].sum() / 100.0,
            "Avg_Delivery_Pct": g["Delivery_Pct"].mean(),
            "Ann_Volatility_Pct": g["Close"].pct_change().std() * np.sqrt(252) * 100,
        })
    return pd.DataFrame(rows)


def write_sqlite(df, summary):
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    out = df.copy()
    out["Date"] = out["Date"].dt.strftime("%Y-%m-%d")
    s = summary.copy()
    for c in ("First_Date", "Last_Date", "52W_High_Date", "52W_Low_Date"):
        s[c] = pd.to_datetime(s[c]).dt.strftime("%Y-%m-%d")
    s.columns = [c.replace("52W", "W52") for c in s.columns]

    con = sqlite3.connect(DB_PATH)
    out.to_sql("ohlcv", con, index=False)
    s.to_sql("symbol_summary", con, index=False)
    cur = con.cursor()
    cur.execute("CREATE UNIQUE INDEX idx_ohlcv_sym_ser_date ON ohlcv(Symbol, Series, Date)")
    cur.execute("CREATE INDEX idx_ohlcv_date ON ohlcv(Date)")
    cur.execute("CREATE INDEX idx_ohlcv_symbol ON ohlcv(Symbol)")
    cur.execute("""
        CREATE VIEW v_latest AS
        SELECT o.* FROM ohlcv o
        JOIN (SELECT Symbol, MAX(Date) AS d FROM ohlcv GROUP BY Symbol) m
          ON o.Symbol = m.Symbol AND o.Date = m.d
    """)
    con.commit()
    con.close()


def autofit(ws, df, writer, date_cols=(), pct_cols=(), num_cols=(), int_cols=()):
    book = writer.book
    fmt_date = book.add_format({"num_format": "yyyy-mm-dd"})
    fmt_num = book.add_format({"num_format": "#,##0.00"})
    fmt_pct = book.add_format({"num_format": "0.00"})
    fmt_int = book.add_format({"num_format": "#,##0"})
    for i, col in enumerate(df.columns):
        width = max(len(str(col)) + 2, 11)
        if col in date_cols:
            ws.set_column(i, i, 12, fmt_date)
        elif col in int_cols:
            ws.set_column(i, i, max(width, 14), fmt_int)
        elif col in pct_cols:
            ws.set_column(i, i, width, fmt_pct)
        elif col in num_cols:
            ws.set_column(i, i, width, fmt_num)
        else:
            ws.set_column(i, i, min(max(width, int(df[col].astype(str).str.len().max() or 0) + 2), 24))


def write_excel(df, summary, symbols, stats):
    price_cols = {"Prev_Close", "Open", "High", "Low", "Last", "Close", "VWAP"}
    int_cols = {"Volume", "No_of_Trades", "Delivery_Qty"}
    pct_cols = {"Delivery_Pct"}
    num_cols = price_cols | {"Turnover_Lacs"}

    with pd.ExcelWriter(XLSX_PATH, engine="xlsxwriter",
                        datetime_format="yyyy-mm-dd", date_format="yyyy-mm-dd") as writer:
        book = writer.book
        head = book.add_format({"bold": True, "bg_color": "#1F3864", "font_color": "white",
                                "border": 1, "align": "center", "valign": "vcenter"})
        title = book.add_format({"bold": True, "font_size": 14})
        wrap = book.add_format({"text_wrap": True, "valign": "top"})

        # ---- README -------------------------------------------------------
        ws = book.add_worksheet("README")
        writer.sheets["README"] = ws
        ws.set_column(0, 0, 26)
        ws.set_column(1, 1, 95, wrap)
        ws.write(0, 0, "NSE Equity OHLCV Database", title)
        notes = [
            ("Generated on", stats["generated"]),
            ("Source", "NSE India - Security-wise Price Volume & Deliverable Position (full bhavcopy)"),
            ("Report page", "https://www.nseindia.com/report-detail/eq_security"),
            ("Data files", "https://archives.nseindia.com/products/content/sec_bhavdata_full_DDMMYYYY.csv"),
            ("Date range", f"{stats['start']} to {stats['end']}"),
            ("Trading days", str(stats["days"])),
            ("Symbols", str(len(symbols))),
            ("Total rows", f"{len(df):,}"),
            ("", ""),
            ("Sheet: Master_Data", "Every symbol x every trading day, one row each. Full OHLCV plus VWAP, "
                                   "turnover, trade count and delivery data."),
            ("Sheet: Summary", "Per-symbol statistics: 52-week high/low with dates, period return, average "
                               "volume/turnover, average delivery percentage and annualised volatility."),
            ("Per-symbol sheets", "One sheet per symbol with its own daily time series, sorted oldest to newest."),
            ("", ""),
            ("Column notes", ""),
            ("Prev_Close", "Previous trading day's close (NSE adjusts this for corporate actions)."),
            ("Open / High / Low / Close", "Official NSE end-of-day prices in INR."),
            ("Last", "Last traded price of the session (can differ from Close, which is a weighted average "
                     "of the last 30 minutes)."),
            ("VWAP", "Volume weighted average price for the session (NSE 'AVG_PRICE')."),
            ("Volume", "Total traded quantity (shares)."),
            ("Turnover_Lacs", "Traded value in INR lakhs (1 lakh = 100,000). Divide by 100 for INR crore."),
            ("Delivery_Qty / Delivery_Pct", "Shares taken to delivery and their share of total volume. Blank "
                                            "where NSE did not publish the figure."),
            ("Series", "EQ = rolling settlement equity. BE/BZ = trade-for-trade. SM/ST = SME board."),
            ("Traded_As", "The ticker the row actually traded under. Differs from Symbol only where a "
                          "company was renamed inside the window (see scripts/aliases.txt); history under "
                          "the old ticker is folded into the current symbol."),
            ("", ""),
            ("Prices are NOT split/bonus adjusted", "Bhavcopy carries the prices as traded on each date. "
                                                    "Check for corporate actions before computing long-run returns."),
            ("Companion database", "nse_ohlcv.db (SQLite): table `ohlcv`, table `symbol_summary`, view `v_latest`."),
        ]
        for r, (k, v) in enumerate(notes, start=2):
            ws.write(r, 0, k, book.add_format({"bold": True, "valign": "top"}) if k else None)
            ws.write(r, 1, v, wrap)

        # ---- Master_Data --------------------------------------------------
        df.to_excel(writer, sheet_name="Master_Data", index=False)
        ws = writer.sheets["Master_Data"]
        for i, c in enumerate(df.columns):
            ws.write(0, i, c, head)
        autofit(ws, df, writer, date_cols={"Date"}, pct_cols=pct_cols,
                num_cols=num_cols, int_cols=int_cols)
        ws.freeze_panes(1, 2)
        ws.autofilter(0, 0, len(df), len(df.columns) - 1)

        # ---- Summary ------------------------------------------------------
        summary.to_excel(writer, sheet_name="Summary", index=False)
        ws = writer.sheets["Summary"]
        for i, c in enumerate(summary.columns):
            ws.write(0, i, c, head)
        autofit(ws, summary, writer,
                date_cols={"First_Date", "Last_Date", "52W_High_Date", "52W_Low_Date"},
                pct_cols={"Period_Return_Pct", "Pct_Below_52W_High", "Pct_Above_52W_Low",
                          "Avg_Delivery_Pct", "Ann_Volatility_Pct"},
                num_cols={"First_Close", "Last_Close", "52W_High", "52W_Low",
                          "Avg_Daily_Turnover_Lacs", "Total_Turnover_Cr"},
                int_cols={"Records", "Avg_Daily_Volume", "Median_Daily_Volume"})
        ws.freeze_panes(1, 1)
        ws.autofilter(0, 0, len(summary), len(summary.columns) - 1)

        # ---- one sheet per symbol ----------------------------------------
        per_cols = [c for c in FINAL_COLS if c not in ("Symbol", "NSE_Ticker")]
        for sym in symbols:
            g = df[df["Symbol"] == sym][per_cols].sort_values("Date")
            if g.empty:
                continue
            name = sym[:31]
            g.to_excel(writer, sheet_name=name, index=False)
            ws = writer.sheets[name]
            for i, c in enumerate(g.columns):
                ws.write(0, i, c, head)
            autofit(ws, g, writer, date_cols={"Date"}, pct_cols=pct_cols,
                    num_cols=num_cols, int_cols=int_cols)
            ws.freeze_panes(1, 2)
            ws.autofilter(0, 0, len(g), len(g.columns) - 1)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    symbols = load_symbols()
    old_to_new = load_aliases()
    df = build_master(symbols, old_to_new)
    summary = build_summary(df)

    stats = {
        "generated": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "start": df["Date"].min().strftime("%Y-%m-%d"),
        "end": df["Date"].max().strftime("%Y-%m-%d"),
        "days": df["Date"].nunique(),
    }

    missing_sessions, corp_actions = check_session_continuity(df)

    df.to_csv(CSV_PATH, index=False, date_format="%Y-%m-%d")
    write_sqlite(df, summary)
    write_excel(df, summary, symbols, stats)

    missing = sorted(set(symbols) - set(df["Symbol"].unique()))
    print(f"Rows          : {len(df):,}")
    print(f"Symbols       : {df['Symbol'].nunique()} / {len(symbols)}")
    print(f"Trading days  : {stats['days']}  ({stats['start']} -> {stats['end']})")
    if missing:
        print(f"NOT FOUND     : {', '.join(missing)}")
    if missing_sessions:
        print("WARNING: a trading session appears to be missing just before: "
              + ", ".join(d.strftime("%Y-%m-%d") for d in missing_sessions))
        print("         (market-wide PREV_CLOSE break -- re-run the downloader)")
    else:
        print("Continuity    : OK, no missing sessions")
    if len(corp_actions):
        print(f"Corporate actions flagged ({len(corp_actions)}) -- prices are unadjusted:")
        for _, r in corp_actions.iterrows():
            print(f"  {r['Symbol']:<12} {r['Date']:%Y-%m-%d}  close {r['prior_close']:.2f}"
                  f" -> restated prev_close {r['Prev_Close']:.2f}")
    else:
        print("Corp actions  : none detected in window")
    print(f"Excel         : {XLSX_PATH}")
    print(f"SQLite        : {DB_PATH}")
    print(f"CSV           : {CSV_PATH}")


if __name__ == "__main__":
    main()
