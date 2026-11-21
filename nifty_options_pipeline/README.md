# NIFTY index options history pipeline

Downloads NSE's daily F&O bhavcopies and index close files from 2019-01-01 to the latest
trading day, keeps NIFTY index options and futures, maps both NSE file formats to one schema,
joins NIFTY 50 spot and India VIX closes, and writes Parquet partitioned by year plus a
markdown validation report. Every stage is resumable.

## Quick start

```bash
pip install -r requirements.txt
python run_pipeline.py download --what fo        # ~1 request/second, ~1 h first time, seconds on re-run
python run_pipeline.py download --what indices   # can run in parallel with the above
python run_pipeline.py build
python run_pipeline.py validate                  # -> reports/validation_report.md
```

`python run_pipeline.py all` does the four steps sequentially. `download --start/--end` limits
the date range; `build --years 2025 2026` rebuilds selected years; `--recheck-404` re-requests
dates previously recorded as 404 (dates in the last 7 days are always re-checked).

## Sources (verified 2026-11-21)

| What | URL pattern | Range |
|---|---|---|
| F&O bhavcopy, old format | `archives.nseindia.com/content/historical/DERIVATIVES/YYYY/MMM/foDDMMMYYYYbhav.csv.zip` | .. 2024-07-05 (last file) |
| F&O bhavcopy, UDiFF | `nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_YYYYMMDD_F_0000.csv.zip` | 2024-01-01 .. (NSE back-filled Jan-Jul 2024; only format from 2024-07-08) |
| Index closes (Nifty 50 + India VIX) | `archives.nseindia.com/content/indices/ind_close_all_DDMMYYYY.csv` | whole range |
| Trading holidays | `www.nseindia.com/api/holiday-master?type=trading` (current year only) + bundled `nse_trading_holidays.csv` | 2019 .. |
| Gap filler | `archives.nseindia.com/archives/fo/mkt/foDDMMYYYY.zip` (F&O market-activity report: OHLC, OI, volume, **no settle**) | only weekdays whose bhavcopy is missing from the archive (2021-03-30) |

Both archive hosts serve both path families; the downloader falls back to the other host on
errors (not on 404). The main site `www.nseindia.com` is behind Akamai and often answers 403
to scripts; the archive hosts have not needed cookies, so a failed warm-up is logged, not fatal.
Do not request `br` encoding: `requests` cannot decode brotli without an extra package and
NSE's API will honour it, giving undecodable bytes.

The cutover is observed from the data on every run: both formats are requested for
2024-01-01..2024-08-31, and the report states the last old-format date and the first UDiFF-only
weekday. The overlap window is also used to reconcile the two formats contract by contract.

## Layout

```
run_pipeline.py                CLI
pipeline/config.py             paths, dates, URL templates, schema
pipeline/nse_session.py        requests.Session with browser headers, warm-up, retry/backoff, 1 s delay
pipeline/manifest.py           append-only CSV manifest => resumability
pipeline/download.py           raw file download + cache (data/raw/, git-ignored)
pipeline/parse.py              old / UDiFF / market-report / index-file parsers -> standard columns
pipeline/build.py              join, derived columns, Parquet by year, CSV sample, expiry calendar
pipeline/holidays.py           NSE holiday API (best effort) + bundled list
pipeline/validate.py           markdown validation report
nse_trading_holidays.csv       hand-entered holiday list (2026 refreshed from the NSE API)
data/processed/nifty_fo/year=YYYY/nifty_fo.parquet
data/processed/nifty_spot_vix.parquet   daily Nifty 50 OHLC + India VIX OHLC
data/processed/expiry_calendar.csv      every option expiry seen, first/last listing date, monthly flag
data/sample/nifty_fo_sample_2024-07.csv one month spanning the format cutover
reports/validation_report.md
```

## Schema (one row per contract per trading day)

| column | notes |
|---|---|
| trade_date | date |
| symbol | NIFTY |
| instrument | OPT or FUT |
| expiry | date |
| strike | float; 0 for futures |
| option_type | CE / PE / '' for futures |
| open, high, low, close, settle | close = last traded price (stale when volume is 0); settle = exchange settlement price |
| contracts_traded | contracts (lots). Old `CONTRACTS` = UDiFF `TtlTradgVol`, verified equal on overlap dates |
| open_interest | **units of underlying** (lots x lot size) in both formats; lot size changed 75 -> 50 -> 25 -> 75 -> 65 (from Jan 2026) over the period |
| value | option value for marking: `settle` when dte > 0; on expiry day (dte == 0) intrinsic against `underlying`, because NSE's settle column there holds the index final settlement price (from Feb 2020) or 0 (before). Futures: always `settle`. |
| traded | contracts_traded > 0 |
| underlying | UDiFF `UndrlygPric` when present (from 2024), else Nifty 50 close joined from the index file |
| vix_close | India VIX close joined from the index file |
| is_monthly_expiry | TRUE when a NIFTY future expires on the same date (NSE lists futures only for monthlies). Beyond the horizon of listed futures (long-dated options) it falls back to "last expiry seen in the calendar month". No weekday assumption. |
| is_last_expiry_in_month | helper: the literal "last expiry date in its calendar month" rule, kept for comparison. It is wrong when a next-month weekly is pulled back across the month boundary by a holiday (30 Apr 2025) and when a monthly is re-dated at short notice (June 2023); the report lists every disagreement. |
| dte | calendar days from trade_date to expiry |
| underlying_source | `file` / `spot_join` / `missing` (helper) |
| source_format | `old` / `udiff` / `mkt_report` (helper; `mkt_report` rows have settle = NaN and only traded contracts) |

Read it with `pd.read_parquet('data/processed/nifty_fo')` (pandas reads the `year=` partitions)
or `pipeline.build.load_fo()`.

## Things to know before backtesting

- NSE re-dates contracts. When it moved the expiry weekday (Thursday -> Tuesday in 2025) the
  long-dated contracts were re-listed under new dates; the old dates linger in the history with
  zero volume and are listed in the report. When a holiday was declared at short notice the
  June 2023 monthly traded as expiry 2023-06-29 until 27 June and as 2023-06-28 on its last day.
- Weekly expiries have no same-expiry future. Only monthly expiries do. For a weekly, the
  forward has to come from the next monthly future, the spot plus carry, or put-call parity.
- On expiry day `settle` is NOT the option's value (index settlement price from Feb 2020, 0 before). Use `value`.
- Old-format rows for strikes with no open interest carry `settle = 0` and a stale `close`.
  Treat `settle = 0` before expiry as "no price".
- `open_interest` is not comparable across years without dividing by the lot size.
- Long-dated (half-yearly) NIFTY options appear in every file with zero volume; they are
  flagged `is_monthly_expiry = TRUE` because they are the only expiry in their month.
- NSE held trading sessions on some weekends (budget days, Muhurat, special sessions); the
  downloader requests every calendar day, so those are included and listed in the report.
- The validation report flags; it never silently fixes. Read section 0 first.
