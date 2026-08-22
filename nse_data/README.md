# NSE Equity OHLCV Database

Daily open / high / low / close / volume data for 51 NSE-listed stocks over the
last one year, collated into a single Excel workbook and a SQLite database.

**Coverage:** 247 trading days, 2025-08-21 → 2026-08-21 · 11,748 rows · 51 symbols

## Source

NSE India's official end-of-day **Security-wise Price Volume & Deliverable
Position** report — the dataset behind
<https://www.nseindia.com/report-detail/eq_security>.

The report page itself is an interactive form that returns one symbol at a time.
The same numbers are published as a daily full-market file, which is what this
project pulls:

```
https://archives.nseindia.com/products/content/sec_bhavdata_full_DDMMYYYY.csv
```

One file per trading day, every listed security in it. Filtering 247 of those
files down to the 51 symbols of interest gives the full year in one pass and
avoids hammering the per-symbol endpoint.

## Outputs (`output/`)

| File | What it is |
|---|---|
| `NSE_OHLCV_Database.xlsx` | The consolidated workbook — 54 sheets |
| `nse_ohlcv.db` | SQLite database — `ohlcv`, `symbol_summary`, view `v_latest` |
| `nse_ohlcv_master.csv` | Flat CSV of the master table |

### Workbook sheets

- **README** — provenance, date range, column definitions, caveats.
- **Master_Data** — every symbol × every trading day, one row each. Frozen
  header, autofilter on.
- **Summary** — per symbol: 52-week high/low with the dates they occurred,
  period return, distance from high/low, average and median volume, average
  and total turnover, average delivery %, annualised volatility.
- **51 per-symbol sheets** — each symbol's own daily series, oldest to newest.

### Columns

`Symbol`, `NSE_Ticker`, `Traded_As`, `Series`, `Date`, `Prev_Close`, `Open`,
`High`, `Low`, `Last`, `Close`, `VWAP`, `Volume`, `Turnover_Lacs`,
`No_of_Trades`, `Delivery_Qty`, `Delivery_Pct`

- `Close` is NSE's official close (weighted average of the last 30 minutes);
  `Last` is the final traded price. They differ on most days.
- `VWAP` is NSE's `AVG_PRICE`.
- `Turnover_Lacs` is in INR lakhs — divide by 100 for INR crore.
- `Delivery_Qty` / `Delivery_Pct` are blank on the 78 rows where NSE did not
  publish the figure.
- `Series`: `EQ` rolling settlement, `BE`/`BZ` trade-for-trade, `SM`/`ST` SME.

## Querying the database

```sql
-- latest session for every symbol
SELECT * FROM v_latest ORDER BY Symbol;

-- one symbol's year
SELECT Date, Open, High, Low, Close, Volume
FROM ohlcv WHERE Symbol = 'HFCL' ORDER BY Date;

-- highest average delivery percentage
SELECT Symbol, ROUND(Avg_Delivery_Pct, 1) FROM symbol_summary
ORDER BY Avg_Delivery_Pct DESC LIMIT 10;
```

`ohlcv` is indexed on `(Symbol, Series, Date)` (unique), `Date`, and `Symbol`.

## Regenerating

```bash
pip install pandas openpyxl XlsxWriter requests
python3 scripts/download_bhavcopy.py --days 366   # ~3 min, writes raw_bhavcopy/
python3 scripts/build_database.py                 # writes output/
```

`raw_bhavcopy/` (85 MB) is gitignored — the download step recreates it. Re-runs
are incremental: already-downloaded days are skipped.

## Notes and caveats

**Prices are not adjusted for corporate actions.** Bhavcopy carries prices as
traded on the day. NSE does adjust `Prev_Close` across an ex-date, so a split or
bonus shows up as a jump between one row's `Close` and the next row's
`Prev_Close`. Check for corporate actions before computing long-run returns.

**Two archive quirks are handled in the downloader**, both discovered while
building this:

1. `archives.nseindia.com` answers `403` both for "no file exists" (weekend,
   holiday) *and* for rate-limiting. They are indistinguishable from a single
   response, so every 403 is retried with backoff and a date is only declared
   unavailable after the retry budget is spent. Without this, 10 ordinary
   trading days in Aug–Sep 2025 silently went missing.
2. On 13 of the 15 trading holidays in this window, the archive served the
   *previous* session's file under the holiday's filename. Each download is
   validated against the date inside the file and discarded on mismatch.

**Short histories** — 8 symbols have fewer than 247 rows because they listed
mid-window, not because data is missing:

| Symbol | Rows | Listed |
|---|---|---|
| VOGL | 49 | 2026-06-15 |
| VEDPOWER | 49 | 2026-06-15 |
| CLEANMAX | 117 | 2026-03-02 |
| AEQUS | 172 | 2025-12-10 |
| MEESHO | 172 | 2025-12-10 |
| SHILCTECH | 184 | 2025-11-24 |
| PINELABS | 190 | 2025-11-14 |
| LENSKART | 194 | 2025-11-10 |

**Ticker renames** are folded in via `scripts/aliases.txt`, so a rename does not
truncate the series. Currently one applies: MIRC Electronics (`MIRCELECTR`)
became Onida (`ONIDA`) on 2026-06-19 — verified by price continuity
(`MIRCELECTR` closed 38.22 on 18-Jun, `ONIDA` opened with `Prev_Close` 38.22 on
19-Jun). The `Traded_As` column records the ticker each row actually traded
under.

## Validation

Checks run on the built dataset, all passing:

- 0 rows where `High < max(Open, Close, Low)` or `Low > min(Open, Close, High)`
- 0 duplicate `(Symbol, Series, Date)` keys
- 0 null or non-positive OHLC / volume values
- Spot-checked against the raw bhavcopy (HFCL 21-Aug-2026: O 225.00, H 228.80,
  L 223.03, C 228.01, Vol 12,598,055, Deliv 38.16% — exact match)
