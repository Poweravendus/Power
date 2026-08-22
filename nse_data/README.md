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

# Backtest: four-rule entry

`scripts/backtest.py` tests a stacked entry:

1. **Open == Low** — never traded below the open all session
2. **Close +3–5%** vs the previous close
3. **Open > previous close** — gapped up
4. **Volume ≥ 1.5×** the prior 30-session average *(swept as a sensitivity parameter)*

Entry at that day's close, stop 3% below the open=low, target +15%.

## Result: positive, but not measurable

**14 trades. +1.35% per trade, 95% CI −3.42% to +7.28%.** A random sample of 14
ordinary days beats it 37% of the time. Remove the single best trade and the
average falls to +0.30%; remove the best two and it is negative.

The funnel: 11,796 rows → 526 (Open=Low) → 107 (+3–5%) → 72 (gap up) → 66 (has
30 sessions of volume history) → **14**.

## Which rules earn their place

Each rule alone, and the full set with each rule removed, on the identical stop
and target. `p` = share of random same-size samples of all days that beat the
subset.

| Filter | Trades | Avg % | 95% CI | p |
|---|---|---|---|---|
| **volume ≥1.5× alone** | 1,692 | **+1.86** | +1.38 … +2.34 | **<0.001** |
| **close +3–5% alone** | 818 | **+1.23** | +0.47 … +1.98 | **0.030** |
| gap up alone | 6,807 | +0.59 | +0.37 … +0.80 | 0.694 |
| Open = Low alone | 526 | +0.52 | −0.27 … +1.32 | 0.617 |
| **without Open = Low** | 191 | **+1.60** | +0.15 … +3.06 | **0.069** |
| without close band | 68 | +1.77 | −0.71 … +4.26 | 0.151 |
| without volume | 72 | +1.41 | −0.87 … +3.78 | 0.227 |
| without gap up | 19 | +1.66 | −2.88 … +6.41 | 0.304 |
| ALL FOUR | 14 | +1.35 | −3.42 … +7.28 | 0.375 |
| every day (baseline) | 11,796 | +0.64 | +0.48 … +0.80 | — |

- **Volume is the only rule that clearly works** — the one interval that never
  touches the baseline.
- **The 3–5% band is a real but smaller effect.** It is also what turned the
  strategy around: the earlier "under 3%" version returned −0.39% per trade.
- **Open = Low and gap-up contribute nothing.** Open = Low returns *below* the
  baseline; gap-up matches 6,807 of 11,796 rows, so it barely filters at all.
- **Dropping Open = Low gives the best-supported combination in the study:**
  191 trades at +1.60%, p = 0.069 — 13× the sample for a higher return.

## Volume threshold sweep (rules 1–3 fixed)

| Threshold | Trades | Avg % | 95% CI |
|---|---|---|---|
| none | 72 | +1.41 | −0.88 … +3.74 |
| ≥1.0× | 35 | +0.98 | −2.19 … +4.59 |
| ≥1.25× | 23 | +0.16 | −3.62 … +4.06 |
| ≥1.5× | 14 | +1.35 | −3.39 … +7.33 |
| ≥2.0× | 5 | −1.90 | −6.70 … +6.70 |
| ≥3.0× | 3 | +0.63 | −7.37 … +15.00 |

Non-monotonic, and every interval crosses zero. Tightening the threshold shrinks
the sample without improving the result.

## The regime problem

Splitting the window at 19 Feb 2026 — the universe fell 7.0% in the first half
and rose 51.1% in the second:

| Filter | H1 avg | H2 avg |
|---|---|---|
| volume ≥1.5× alone | −2.76 | +4.67 |
| close +3–5% alone | −2.44 | +3.53 |
| Open = Low alone | −2.06 | +2.59 |
| gap up alone | −1.64 | +2.59 |
| ALL FOUR | −0.95 | +2.26 |
| every day (baseline) | −1.68 | +2.79 |

**Every filter is negative in the falling half and positive in the rising half,
including the do-nothing baseline.** In the falling half the volume filter did
*worse* than doing nothing. These filters amplify market direction rather than
predict it — beta, not alpha. Over a window that rose 43%, beta looks like skill.

## Engine

- Volume benchmark is the 30 sessions *before* the signal, so a high-volume day
  cannot inflate its own benchmark. A full 30-session history is required
  (6 otherwise-qualifying days dropped, all recent listings).
- Entry at the signal day's close; exits checked from the next session.
- Stop = signal-day low × 0.97, target = entry × 1.15. Because a 3–5% up day
  closes well above its open, real risk averages 6.08% from entry, not 3%.
- Gaps exit at the open, not the level. A bar touching both levels scores as a
  stop (never occurred here).
- Confidence intervals bootstrapped and p-values permuted, 20,000 resamples each.
- One position per symbol gives 13 trades at +1.92% — same conclusion.
- Costs excluded; Indian round-trip delivery costs run 0.3–0.6%.

```bash
python3 scripts/backtest.py                                   # defaults above
python3 scripts/backtest.py --vol-mult 2.5 --up-min 2 --up-max 6
python3 scripts/backtest.py --sl 8 --target 25
```

Outputs `backtest/Backtest_Results.xlsx` (volume sweep, rule attribution, period
split, sensitivity grid, fixed-hold reference, risk-matched benchmark, trade
logs) and `backtest/report.html`.

**Limits.** One year, 51 hand-picked names, a market that rose 43%. Enough to
rank the four rules against each other. Not enough to certify any of them for
live trading.
