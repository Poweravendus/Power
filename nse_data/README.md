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

---

# Backtest: "Open = Low" entry

`scripts/backtest.py` tests the entry rule: buy at the close on days where the
stock's **Open equals its Low** and the day's up-move is under 3%; stop 3% below
that open=low; target +15%.

## Result: no edge

| | Rule 2 = vs prev close | Rule 2 = vs open |
|---|---|---|
| Trades | 338 | 331 |
| Target hit / stopped | 67 / 251 | 72 / 240 |
| Win rate | 23.1% | 24.8% |
| **Expectancy per trade** | **−0.39%** | **+0.10%** |
| Profit factor | 0.89 | 1.03 |

"Below 3% up that day" is ambiguous, so both readings are run. Neither produces
an edge, so the ambiguity does not change the conclusion. Excluding overlapping
positions gives −0.17% and +0.37% respectively — same answer.

The arithmetic is the whole story: average win +13.7%, average loss −4.6%, so
the strategy needs a **25.2%** win rate to break even and delivers **23.1%**.

## Three independent checks

1. **The filter picks below-average days.** Running the identical stop and
   target on all 11,458 non-signal days returns **+0.55%** per trade at profit
   factor 1.16, versus **−0.19%** and 0.94 on signal days. Both sets use the
   same stop distance from entry (4.63%) — without that correction non-signal
   days get a wider stop by construction and the comparison is meaningless.
2. **The stop, not the entry, is the problem.** The same 338 signals held for a
   fixed period with no stop and no target return +1.56% at 10 days, +2.93% at
   20 and +6.27% at 40, winning 55% of the time at 40 days.
3. **A 3% stop is inside the noise.** Real risk averages 4.63% from entry
   (the close sits above the open), against a median 14-day ATR of 3.90% —
   1.19× one average day's range. 21% of trades that eventually reached +15%
   first traded more than 3% below entry.

Context: equal-weight buy-and-hold of the same 51 names returned **+43.0%** over
the window. Costs are excluded; Indian round-trip delivery costs of 0.3–0.6%
would make a marginal result clearly negative.

## Sensitivity

Average return per trade, Rule 2 vs previous close:

| stop ↓ / target → | +8% | +10% | +15% | +20% | +25% |
|---|---|---|---|---|---|
| −2% | −0.70 | −0.65 | −0.37 | −0.21 | +0.37 |
| **−3%** | −0.74 | −0.75 | **−0.39** | −0.07 | +0.66 |
| −5% | −0.65 | −0.77 | −0.16 | +0.25 | +1.16 |
| −8% | −0.16 | −0.06 | +0.64 | +1.42 | +2.46 |

The gradient runs one way: wider stop, larger target. The best cell (−8% / +25%)
returns +2.46% per trade, but it is one unvalidated peak in a 20-cell grid fitted
on a single year — a direction to investigate, not a setting to trade.

## Engine

- Entry at the signal day's close; exits checked from the next session.
- Stop = signal-day low × 0.97. Target = entry × 1.15.
- Gaps exit at the open, not the level — no look-ahead in either direction.
- A bar touching both levels is scored as a stop (conservative). It never
  occurred: no single bar spanned both a 4.6% loss and a 15% gain.
- Trades still live at the end of the window are marked to the last close.

```bash
python3 scripts/backtest.py                      # defaults: SL 3%, target 15%
python3 scripts/backtest.py --sl 8 --target 25   # any variant
```

Outputs `backtest/Backtest_Results.xlsx` (headline, sensitivity grid,
fixed-hold reference, risk-matched benchmark, portfolio, monthly, per-symbol,
full trade logs), per-variant trade CSVs, and `backtest/report.html`.

**Limits.** One year, 51 hand-picked names, one strongly bullish regime. Enough
to say these rules have no edge here; not enough to say the idea is dead in
every regime, or that the wide-stop corner of the grid is real.
