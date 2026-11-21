# NIFTY options data validation report

Generated 2026-11-21 17:41 UTC. Rows: 4,120,590; trade dates: 1,957 (2019-01-01 .. 2026-11-20); spot-check seed 42.

## 0. Flags

- **FLAG** 1 trading day(s) have no bhavcopy in NSE's archive and were filled from the F&O market-activity report, which has no settlement price and lists traded contracts only: ['2021-03-30'] (section 2)
- **FLAG** 13 expiry dates were listed and later removed/re-dated by NSE (176,574 rows, almost all zero-volume long-dated contracts) (section 3)
- **FLAG** 4 expiries where the futures-based monthly flag disagrees with the literal last-expiry-in-month rule (section 3c) - this is why the literal rule was not used
- **FLAG** 1 month(s) carry two monthly expiry dates because NSE re-dated the contract mid-life; a position held across the change sees its expiry date change (section 3c)
- **FLAG** 3 index files had the date written MM-DD-YYYY; accepted because the swapped date equals the file date (section 6)
- **FLAG** 18500 option rows with open interest/volume but settle = 0 before expiry (76% of them untraded that day, so `close` is a stale print there) (section 8)
- **FLAG** 42,264 pre-expiry option rows have settle = 0 (untraded, zero OI; mostly old format). Treat settle=0 as 'no price', not a price (section 8)
- **FLAG** 228,120 option rows (5.7%) carry a settlement price that violates strike monotonicity; 5-9% of near-the-money rows. Flagged in `value_suspect`, interpolation in `value_interp` (section 10)

## 1. Trading-day calendar

Date range with F&O files: **2019-01-01 .. 2026-11-20**. Holiday list sources: {'bundled': 102, 'nse_api': 20} (the NSE holiday API is attempted every run; when it is unreachable only the bundled, hand-entered list is used).

| year | fo_trading_days | index_days | weekdays_without_fo_file | of_which_listed_holidays | of_which_NOT_listed | weekend_sessions_with_data |
|---|---|---|---|---|---|---|
| 2019 | 245 | 245 | 17 | 17 | 0 | 1 |
| 2020 | 252 | 252 | 12 | 12 | 0 | 2 |
| 2021 | 248 | 248 | 13 | 13 | 0 | 0 |
| 2022 | 248 | 248 | 12 | 12 | 0 | 0 |
| 2023 | 246 | 246 | 15 | 15 | 0 | 1 |
| 2024 | 249 | 249 | 16 | 16 | 0 | 3 |
| 2025 | 249 | 249 | 13 | 13 | 0 | 1 |
| 2026 | 220 | 220 | 14 | 14 | 0 | 2 |


Weekdays with no bhavcopy that were filled from the market-activity report: ['2021-03-30']


### 1a. Weekdays with no F&O file that are NOT in the holiday list

None. Every weekday without a file is a listed holiday.


### 1b. Listed holidays that DO have an F&O file (special sessions, or a wrong holiday entry)

| date | weekday | holiday_list_entry | note |
|---|---|---|---|
| 2021-11-04 | Thu | Diwali Laxmi Pujan | Muhurat session held - bhavcopy expected |
| 2022-10-24 | Mon | Diwali Laxmi Pujan | Muhurat session held - bhavcopy expected |
| 2024-11-01 | Fri | Diwali Laxmi Pujan | Muhurat session held - bhavcopy expected |
| 2025-10-21 | Tue | Diwali Laxmi Pujan | Muhurat session held - bhavcopy expected |
| 2026-11-08 | Sun | Diwali Laxmi Pujan* |  |


### 1c. Weekend dates with an F&O file (special / Muhurat / budget sessions)

| date | weekday | option_rows |
|---|---|---|
| 2019-10-27 | Sun | 3277 |
| 2020-02-01 | Sat | 3165 |
| 2020-11-14 | Sat | 2198 |
| 2023-11-12 | Sun | 1357 |
| 2024-01-20 | Sat | 1604 |
| 2024-03-02 | Sat | 1496 |
| 2024-05-18 | Sat | 1498 |
| 2025-02-01 | Sat | 1586 |
| 2026-02-01 | Sun | 1601 |
| 2026-11-08 | Sun | 2221 |


### 1d. Days present in only one of the two sources

- F&O file but no index file: 0 []

- Index file but no F&O file: 0 []

## 2. Row counts per year, per source format

- Last date with an old-format file: **2024-07-05**

- First date with a UDiFF file: **2024-01-01** (NSE back-filled UDiFF for 2024)

- First weekday where only UDiFF exists (observed cutover): **2024-07-08**

- Configured cutover: old format up to 2024-07-05, UDiFF from 2024-07-08

- **FLAG** days filled from the market-activity report (source_format = mkt_report, settle = NaN): ['2021-03-30']


| year | old_FUT | old_OPT | mkt_report_FUT | mkt_report_OPT | udiff_FUT | udiff_OPT | trading_days | opt_rows_per_day |
|---|---|---|---|---|---|---|---|---|
| 2019 | 735 | 773,364 | 0 | 0 | 0 | 0 | 245 | 3,157 |
| 2020 | 756 | 736,996 | 0 | 0 | 0 | 0 | 252 | 2,925 |
| 2021 | 741 | 510,565 | 3 | 573 | 0 | 0 | 248 | 2,061 |
| 2022 | 744 | 562,041 | 0 | 0 | 0 | 0 | 248 | 2,266 |
| 2023 | 738 | 340,423 | 0 | 0 | 0 | 0 | 246 | 1,384 |
| 2024 | 384 | 197,852 | 0 | 0 | 363 | 200,887 | 249 | 1,601 |
| 2025 | 0 | 0 | 0 | 0 | 747 | 395,866 | 249 | 1,590 |
| 2026 | 0 | 0 | 0 | 0 | 660 | 396,152 | 220 | 1,801 |

## 3. Expiry calendar

`is_monthly_expiry` = an option expiry on which a NIFTY future also expires (futures are listed only for monthlies); beyond the futures horizon (long-dated options) it falls back to the last expiry seen in the calendar month. The literal last-in-month rule is kept in `is_last_expiry_in_month`; section 3c lists where the two disagree.


### 3-pre. Expiries listed at some point but removed before expiry (re-dated by NSE). Their rows are kept; they are flagged monthly only if a future carried the same date.

| expiry | weekday | first_seen | last_seen | rows |
|---|---|---|---|---|
| 2023-03-30 | Thursday | 2022-04-01 | 2022-12-21 | 4654 |
| 2025-09-25 | Thursday | 2024-09-27 | 2025-07-31 | 9296 |
| 2025-12-24 | Wednesday | 2021-01-01 | 2025-07-31 | 33768 |
| 2026-03-26 | Thursday | 2025-03-28 | 2025-07-31 | 2202 |
| 2026-03-31 | Tuesday | 2025-08-01 | 2025-12-26 | 2588 |
| 2026-06-25 | Thursday | 2021-06-25 | 2025-07-31 | 28996 |
| 2026-12-31 | Thursday | 2021-12-31 | 2025-07-31 | 25349 |
| 2027-06-24 | Thursday | 2022-07-01 | 2025-07-31 | 19538 |
| 2027-12-30 | Thursday | 2022-12-30 | 2025-07-31 | 16588 |
| 2028-06-29 | Thursday | 2023-06-30 | 2025-07-31 | 12942 |
| 2028-12-28 | Thursday | 2023-12-29 | 2025-07-31 | 9981 |
| 2029-06-28 | Thursday | 2024-06-28 | 2025-07-31 | 6904 |
| 2029-12-27 | Thursday | 2024-12-27 | 2025-07-31 | 3768 |


### 3a. Monthly expiry dates by year

- **2019** (12): 2019-01-31 (Thu), 2019-02-28 (Thu), 2019-03-28 (Thu), 2019-04-25 (Thu), 2019-05-30 (Thu), 2019-06-27 (Thu), 2019-07-25 (Thu), 2019-08-29 (Thu), 2019-09-26 (Thu), 2019-10-31 (Thu), 2019-11-28 (Thu), 2019-12-26 (Thu)

- **2020** (12): 2020-01-30 (Thu), 2020-02-27 (Thu), 2020-03-26 (Thu), 2020-04-30 (Thu), 2020-05-28 (Thu), 2020-06-25 (Thu), 2020-07-30 (Thu), 2020-08-27 (Thu), 2020-09-24 (Thu), 2020-10-29 (Thu), 2020-11-26 (Thu), 2020-12-31 (Thu)

- **2021** (12): 2021-01-28 (Thu), 2021-02-25 (Thu), 2021-03-25 (Thu), 2021-04-29 (Thu), 2021-05-27 (Thu), 2021-06-24 (Thu), 2021-07-29 (Thu), 2021-08-26 (Thu), 2021-09-30 (Thu), 2021-10-28 (Thu), 2021-11-25 (Thu), 2021-12-30 (Thu)

- **2022** (12): 2022-01-27 (Thu), 2022-02-24 (Thu), 2022-03-31 (Thu), 2022-04-28 (Thu), 2022-05-26 (Thu), 2022-06-30 (Thu), 2022-07-28 (Thu), 2022-08-25 (Thu), 2022-09-29 (Thu), 2022-10-27 (Thu), 2022-11-24 (Thu), 2022-12-29 (Thu)

- **2023** (13): 2023-01-25 (Wed), 2023-02-23 (Thu), 2023-03-29 (Wed), 2023-04-27 (Thu), 2023-05-25 (Thu), 2023-06-28 (Wed), 2023-06-29 (Thu), 2023-07-27 (Thu), 2023-08-31 (Thu), 2023-09-28 (Thu), 2023-10-26 (Thu), 2023-11-30 (Thu), 2023-12-28 (Thu)

- **2024** (12): 2024-01-25 (Thu), 2024-02-29 (Thu), 2024-03-28 (Thu), 2024-04-25 (Thu), 2024-05-30 (Thu), 2024-06-27 (Thu), 2024-07-25 (Thu), 2024-08-29 (Thu), 2024-09-26 (Thu), 2024-10-31 (Thu), 2024-11-28 (Thu), 2024-12-26 (Thu)

- **2025** (12): 2025-01-30 (Thu), 2025-02-27 (Thu), 2025-03-27 (Thu), 2025-04-24 (Thu), 2025-05-29 (Thu), 2025-06-26 (Thu), 2025-07-31 (Thu), 2025-08-28 (Thu), 2025-09-30 (Tue), 2025-10-28 (Tue), 2025-11-25 (Tue), 2025-12-30 (Tue)

- **2026** (12): 2026-01-27 (Tue), 2026-02-24 (Tue), 2026-03-30 (Mon), 2026-04-28 (Tue), 2026-05-26 (Tue), 2026-06-30 (Tue), 2026-07-28 (Tue), 2026-08-25 (Tue), 2026-09-29 (Tue), 2026-10-27 (Tue), 2026-11-23 (Mon), 2026-12-29 (Tue)

- **2027** (5): 2027-01-25 (Mon), 2027-03-30 (Tue), 2027-06-29 (Tue), 2027-09-28 (Tue), 2027-12-28 (Tue)

- **2028** (2): 2028-06-27 (Tue), 2028-12-26 (Tue)

- **2029** (2): 2029-06-26 (Tue), 2029-12-24 (Mon)

- **2030** (2): 2030-06-25 (Tue), 2030-12-31 (Tue)

- **2031** (1): 2031-06-24 (Tue)


### 3b. Expiry weekday by year (shows NSE moving the expiry day)

| year | is_monthly | Monday | Thursday | Tuesday | Wednesday |
|---|---|---|---|---|---|
| 2019 | False | 0 | 33 | 0 | 2 |
| 2019 | True | 0 | 12 | 0 | 0 |
| 2020 | False | 0 | 40 | 0 | 1 |
| 2020 | True | 0 | 12 | 0 | 0 |
| 2021 | False | 0 | 36 | 0 | 4 |
| 2021 | True | 0 | 12 | 0 | 0 |
| 2022 | False | 0 | 39 | 0 | 1 |
| 2022 | True | 0 | 12 | 0 | 0 |
| 2023 | False | 0 | 40 | 0 | 0 |
| 2023 | True | 0 | 10 | 0 | 3 |
| 2024 | False | 0 | 38 | 0 | 2 |
| 2024 | True | 0 | 12 | 0 | 0 |
| 2025 | False | 1 | 25 | 13 | 2 |
| 2025 | True | 0 | 8 | 4 | 0 |
| 2026 | False | 4 | 0 | 32 | 0 |
| 2026 | True | 1 | 0 | 9 | 0 |


### 3c. Consistency checks

- Futures expiries removed/re-dated before expiry (ignored below): ['2025-09-25']

- Futures expiries not flagged as monthly: 0 []

- Expiries where `is_monthly_expiry` != `is_last_expiry_in_month` (within the futures horizon): 4

| expiry | weekday | is_monthly_expiry | is_last_expiry_in_month | why |
|---|---|---|---|---|
| 2023-06-28 | Wednesday | True | False | a future expired on this date, but a later option expiry exists in the same month (monthly re-dated: sudden holiday or expiry-weekday change) |
| 2025-04-24 | Thursday | True | False | a future expired on this date, but a later option expiry exists in the same month (monthly re-dated: sudden holiday or expiry-weekday change) |
| 2025-04-30 | Wednesday | False | True | last expiry of the month but no future: a next-month weekly pulled back by a holiday, or a removed date |
| 2025-09-25 | Thursday | True | False | a future expired on this date, but a later option expiry exists in the same month (monthly re-dated: sudden holiday or expiry-weekday change) |

- Months with more than one monthly expiry date: 1

| month | expiry_dates |
|---|---|
| 2023-06 | 2023-06-28, 2023-06-29 |

- Months in range without any option expiry: none

- Long-dated (quarterly/half-yearly) expiries beyond the data end, flagged monthly by construction: ['2027-03-30', '2027-06-29', '2027-09-28', '2027-12-28', '2028-06-27', '2028-12-26', '2029-06-26', '2029-12-24', '2030-06-25', '2030-12-31', '2031-06-24']

- Rows with expiry before trade date (dte < 0): 0

## 4. Illiquid strikes: share of option rows with zero contracts traded

All years, all expiries, distance = strike / underlying - 1:

| strike vs underlying | rows | zero-volume share % |
|---|---|---|
| < -20% | 428172 | 91.3 |
| -20..-10% | 557066 | 78.1 |
| -10..-5% | 607830 | 62.9 |
| -5..-2.5% | 333564 | 50.9 |
| -2.5..-1% | 200654 | 42.0 |
| -1..+1% (ATM) | 267117 | 35.1 |
| +1..2.5% | 201654 | 41.5 |
| +2.5..5% | 333381 | 51.1 |
| +5..10% | 573006 | 64.4 |
| +10..20% | 405680 | 78.9 |
| > +20% | 206595 | 89.7 |


By year, zero-volume share % (all strikes / within ±2.5% of spot / dte <= 7):

| year | all_strikes | within_2.5pct | dte_le_7 | dte_gt_60 |
|---|---|---|---|---|
| 2019 | 89.5 | 73.2 | 49.3 | 96.7 |
| 2020 | 83.6 | 68.5 | 39.0 | 94.0 |
| 2021 | 69.1 | 52.5 | 19.8 | 85.2 |
| 2022 | 62.8 | 43.4 | 19.4 | 77.7 |
| 2023 | 47.7 | 20.4 | 15.9 | 72.1 |
| 2024 | 45.8 | 21.9 | 12.7 | 72.0 |
| 2025 | 41.2 | 18.6 | 13.1 | 67.1 |
| 2026 | 40.7 | 14.9 | 16.0 | 61.7 |


Note: on zero-volume rows `close` is NSE's last traded price (possibly days old) while `settle` is the exchange settlement price; they differ on 2,682,776 of 2,684,274 zero-volume rows (99.9%). Use `settle` for illiquid strikes.

## 5. Spot checks: ATM call/put vs underlying and put-call parity vs the same-expiry future

Parity used: C - P = (F - K) * exp(-r*T) with r = 6.5%; `implied_fwd` = K + (C - P) * exp(r*T). Residual is reported in index points and as % of spot. Only monthly expiries have a same-expiry future; for the nearest weekly expiry the implied forward is compared with spot instead.


### 5a. Nearest monthly expiry (future exists)
| trade_date | spot | expiry | dte | atm_strike | call_close | put_close | future_close | implied_fwd | parity_resid_pts | resid_pct_spot | atm_call_pct_spot |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2019-03-14 | 11,343.25 | 2019-03-28 | 14 | 11,350.00 | 125.65 | 95.40 | 11,381.75 | 11,380.33 | -1.42 | -0.01 | 1.11 |
| 2019-12-06 | 11,921.50 | 2019-12-26 | 20 | 11,900.00 | 169.15 | 114.95 | 11,955.70 | 11,954.39 | -1.30 | -0.01 | 1.42 |
| 2021-04-09 | 14,834.85 | 2021-04-29 | 20 | 14,850.00 | 283.65 | 245.90 | 14,889.40 | 14,887.88 | -1.51 | -0.01 | 1.91 |
| 2024-04-12 | 22,519.40 | 2024-04-25 | 13 | 22,500.00 | 249.25 | 144.95 | 22,601.45 | 22,604.54 | 3.08 | 0.01 | 1.11 |
| 2025-02-11 | 23,071.80 | 2025-02-27 | 16 | 23,050.00 | 327.75 | 225.05 | 23,153.15 | 23,152.99 | -0.16 | -0.00 | 1.42 |


### 5b. Nearest weekly expiry (no same-expiry future; implied forward vs spot)
| trade_date | spot | weekly_expiry | dte | atm_strike | call_close | put_close | implied_fwd | fwd_minus_spot_pct | next_monthly_future |
|---|---|---|---|---|---|---|---|---|---|
| 2019-03-14 | 11,343.25 | 2019-03-20 | 6 | 11,350.00 | 73.60 | 63.55 | 11,360.06 | 0.15 | 11,381.75 |
| 2019-12-06 | 11,921.50 | 2019-12-12 | 6 | 11,900.00 | 83.90 | 50.25 | 11,933.69 | 0.10 | 11,955.70 |
| 2021-04-09 | 14,834.85 | 2021-04-15 | 6 | 14,850.00 | 127.10 | 133.95 | 14,843.14 | 0.06 | 14,889.40 |
| 2024-04-12 | 22,519.40 | 2024-04-18 | 6 | 22,500.00 | 157.75 | 89.50 | 22,568.32 | 0.22 | 22,601.45 |
| 2025-02-11 | 23,071.80 | 2025-02-13 | 2 | 23,050.00 | 143.30 | 90.40 | 23,102.92 | 0.13 | 23,153.15 |


What 'roughly holds' means here: a residual within about 0.1-0.3% of spot is normal (bid-ask, stale closes, dividend/rate assumptions). Weekly implied forwards sit slightly above spot by the carry; a weekly implied forward far from spot or from the monthly future would be a flag.

## 6. NIFTY 50 spot and India VIX series

- Index-file days: 1957; days with missing/zero Nifty 50 close: 0; missing/zero India VIX close: 0

- Days where the VIX row has a close but '-' for open/high/low: 2 ['2021-02-12', '2021-03-30']

- **FLAG** index files with MM-DD-YYYY dates (accepted, see note): ['2023-04-06', '2023-04-10', '2023-04-11']

- F&O days with no underlying at all: 0 []

- F&O days with no VIX close: 0 []


### 6a. Large day-over-day moves (|spot| > 7% or |VIX| > 40%) - check these are real events

| trade_date | spot_close | spot_ret_pct | vix_close | vix_chg_pct |
|---|---|---|---|---|
| 2020-03-12 | 9,590.15 | -8.30 | 41.16 | 30.42 |
| 2020-03-16 | 9,197.40 | -7.61 | 58.88 | 14.40 |
| 2020-03-23 | 7,610.25 | -12.98 | 71.99 | 7.29 |
| 2020-04-07 | 8,792.20 | 8.76 | 51.80 | -6.33 |
| 2024-08-05 | 24,055.60 | -2.68 | 20.37 | 42.25 |
| 2025-04-07 | 22,161.60 | -3.24 | 22.79 | 65.62 |


### 6b. Gaps of more than 5 calendar days between consecutive index-file days

_(none)_


### 6c. UDiFF `UndrlygPric` vs Nifty 50 close from the index file
- days compared: 590; days differing by > 0.5 pts: 0

- days where UDiFF rows carry more than one underlying value for NIFTY: 0

## 7. Old-format vs UDiFF reconciliation on overlap dates (Jan-Jul 2024)

Dates with both files: 128 (2024-01-01 .. 2024-07-05)

Total contract-days with any difference: **0**


| rows_old | rows_udiff | only_in_old | only_in_udiff | diff_open | diff_high | diff_low | diff_close | diff_settle | diff_contracts_traded | diff_open_interest |
|---|---|---|---|---|---|---|---|---|---|---|
| 198236 | 198236 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## 8. Row-level integrity

- Duplicate contract-days: 0

- Option rows with option_type not CE/PE: 0; futures rows with a non-blank option_type: 0

- Rows with a negative price: 0

- Traded rows where close is outside [low, high] or high < low: 0

- Rows with close <= 0 but open interest > 0: 0

- Expiry-day option rows (dte == 0): 79,540. `settle` there is NOT an option value: 8,582 rows have settle = 0 (all expiries up to 2020-01-30), 70,958 rows have settle = index final settlement price = underlying (from 2020-02-06), 0 rows have something else. Use `value` (intrinsic vs underlying) on expiry day, never `settle`.

- Pre-expiry option rows with settle <= 0: 60,764 = untraded zero-OI strikes 42,264 (old format leaves settle at 0 for strikes nobody holds; `close` there is a stale last-traded price) + rows WITH OI or volume but settle 0 18,500

| year | rows |
|---|---|
| 2019 | 7239 |
| 2020 | 803 |
| 2021 | 3103 |
| 2022 | 4067 |
| 2023 | 1432 |
| 2024 | 571 |
| 2025 | 549 |
| 2026 | 736 |

- NaN counts: {'settle': 576}

- Futures rows per day: min 3, max 3 (NSE lists 3 monthly futures)

- Minimum strike step on near expiries by year: {2019: 50.0, 2020: 50.0, 2021: 50.0, 2022: 50.0, 2023: 50.0, 2024: 50.0, 2025: 50.0, 2026: 50.0}

- Units: `contracts_traded` is in contracts (lots); `open_interest` is in units of underlying (lots x lot size) in BOTH formats, consistent with each other on the overlap dates. Lot size changed over time (75 -> 50 -> 25 -> 75 -> 65 from Jan 2026), so OI is not comparable across years without dividing by lot size.

## 9. Expiry-day `value` = intrinsic check

`value` = `settle` for dte > 0; on dte == 0 it is intrinsic against `underlying` (CE: max(0, underlying - strike), PE: max(0, strike - underlying)). Whole-dataset check first, then four sample expiries with the strikes around the money.

- Expiry-day option rows: 79,540; max |value - intrinsic| = 0.0000; rows with |diff| > 0.005: 0; rows with value NaN: 0

- Pre-expiry option rows: 4,035,179; rows where value != settle: 0

- `traded` = contracts_traded > 0: 1,430,445 of 4,114,719 option rows (34.8%)


### 9.2019: expiry 2019-07-18, underlying (Nifty close) 11,596.90, max |diff| over all 156 strikes that day = 0.0000

| strike | option_type | close | settle | underlying | value | intrinsic | diff | contracts_traded |
|---|---|---|---|---|---|---|---|---|
| 11,450.00 | CE | 141.35 | 0.00 | 11,596.90 | 146.90 | 146.90 | 0.00 | 542.00 |
| 11,450.00 | PE | 0.05 | 0.00 | 11,596.90 | 0.00 | 0.00 | 0.00 | 8,385.00 |
| 11,500.00 | CE | 99.45 | 0.00 | 11,596.90 | 96.90 | 96.90 | 0.00 | 23,105.00 |
| 11,500.00 | PE | 0.05 | 0.00 | 11,596.90 | 0.00 | 0.00 | 0.00 | 63,401.00 |
| 11,550.00 | CE | 49.05 | 0.00 | 11,596.90 | 46.90 | 46.90 | 0.00 | 37,841.00 |
| 11,550.00 | PE | 0.05 | 0.00 | 11,596.90 | 0.00 | 0.00 | 0.00 | 152,374.00 |
| 11,600.00 | CE | 4.30 | 0.00 | 11,596.90 | 0.00 | 0.00 | 0.00 | 402,187.00 |
| 11,600.00 | PE | 1.35 | 0.00 | 11,596.90 | 3.10 | 3.10 | 0.00 | 886,229.00 |
| 11,650.00 | CE | 0.15 | 0.00 | 11,596.90 | 0.00 | 0.00 | 0.00 | 858,479.00 |
| 11,650.00 | PE | 33.85 | 0.00 | 11,596.90 | 53.10 | 53.10 | 0.00 | 688,364.00 |
| 11,700.00 | CE | 0.05 | 0.00 | 11,596.90 | 0.00 | 0.00 | 0.00 | 908,072.00 |
| 11,700.00 | PE | 84.15 | 0.00 | 11,596.90 | 103.10 | 103.10 | 0.00 | 265,469.00 |


### 9.2021: expiry 2021-07-08, underlying (Nifty close) 15,727.90, max |diff| over all 170 strikes that day = 0.0000

| strike | option_type | close | settle | underlying | value | intrinsic | diff | contracts_traded |
|---|---|---|---|---|---|---|---|---|
| 15,600.00 | CE | 123.50 | 15,727.90 | 15,727.90 | 127.90 | 127.90 | 0.00 | 114,304.00 |
| 15,600.00 | PE | 0.20 | 15,727.90 | 15,727.90 | 0.00 | 0.00 | 0.00 | 725,631.00 |
| 15,650.00 | CE | 72.85 | 15,727.90 | 15,727.90 | 77.90 | 77.90 | 0.00 | 198,358.00 |
| 15,650.00 | PE | 0.30 | 15,727.90 | 15,727.90 | 0.00 | 0.00 | 0.00 | 1,100,966.00 |
| 15,700.00 | CE | 23.65 | 15,727.90 | 15,727.90 | 27.90 | 27.90 | 0.00 | 1,522,726.00 |
| 15,700.00 | PE | 1.15 | 15,727.90 | 15,727.90 | 0.00 | 0.00 | 0.00 | 3,397,572.00 |
| 15,750.00 | CE | 0.50 | 15,727.90 | 15,727.90 | 0.00 | 0.00 | 0.00 | 2,161,904.00 |
| 15,750.00 | PE | 26.05 | 15,727.90 | 15,727.90 | 22.10 | 22.10 | 0.00 | 2,322,912.00 |
| 15,800.00 | CE | 0.20 | 15,727.90 | 15,727.90 | 0.00 | 0.00 | 0.00 | 2,919,293.00 |
| 15,800.00 | PE | 76.40 | 15,727.90 | 15,727.90 | 72.10 | 72.10 | 0.00 | 2,511,373.00 |
| 15,850.00 | CE | 0.15 | 15,727.90 | 15,727.90 | 0.00 | 0.00 | 0.00 | 2,250,094.00 |
| 15,850.00 | PE | 126.10 | 15,727.90 | 15,727.90 | 122.10 | 122.10 | 0.00 | 1,130,695.00 |


### 9.2024: expiry 2024-07-04, underlying (Nifty close) 24,302.15, max |diff| over all 238 strikes that day = 0.0000

| strike | option_type | close | settle | underlying | value | intrinsic | diff | contracts_traded |
|---|---|---|---|---|---|---|---|---|
| 24,200.00 | CE | 99.20 | 24,302.15 | 24,302.15 | 102.15 | 102.15 | 0.00 | 3,472,360.00 |
| 24,200.00 | PE | 0.20 | 24,302.15 | 24,302.15 | 0.00 | 0.00 | 0.00 | 20,104,678.00 |
| 24,250.00 | CE | 49.05 | 24,302.15 | 24,302.15 | 52.15 | 52.15 | 0.00 | 8,163,687.00 |
| 24,250.00 | PE | 0.35 | 24,302.15 | 24,302.15 | 0.00 | 0.00 | 0.00 | 29,073,071.00 |
| 24,300.00 | CE | 2.20 | 24,302.15 | 24,302.15 | 2.15 | 2.15 | 0.00 | 61,324,620.00 |
| 24,300.00 | PE | 3.15 | 24,302.15 | 24,302.15 | 0.00 | 0.00 | 0.00 | 83,425,758.00 |
| 24,350.00 | CE | 0.20 | 24,302.15 | 24,302.15 | 0.00 | 0.00 | 0.00 | 59,786,066.00 |
| 24,350.00 | PE | 50.90 | 24,302.15 | 24,302.15 | 47.85 | 47.85 | 0.00 | 36,630,166.00 |
| 24,400.00 | CE | 0.15 | 24,302.15 | 24,302.15 | 0.00 | 0.00 | 0.00 | 36,724,387.00 |
| 24,400.00 | PE | 100.85 | 24,302.15 | 24,302.15 | 97.85 | 97.85 | 0.00 | 15,630,030.00 |
| 24,450.00 | CE | 0.10 | 24,302.15 | 24,302.15 | 0.00 | 0.00 | 0.00 | 19,428,635.00 |
| 24,450.00 | PE | 150.60 | 24,302.15 | 24,302.15 | 147.85 | 147.85 | 0.00 | 3,258,225.00 |


### 9.2026: expiry 2026-06-16, underlying (Nifty close) 23,989.15, max |diff| over all 206 strikes that day = 0.0000

| strike | option_type | close | settle | underlying | value | intrinsic | diff | contracts_traded |
|---|---|---|---|---|---|---|---|---|
| 23,850.00 | CE | 136.75 | 23,989.15 | 23,989.15 | 139.15 | 139.15 | 0.00 | 4,996,714.00 |
| 23,850.00 | PE | 0.15 | 23,989.15 | 23,989.15 | 0.00 | 0.00 | 0.00 | 15,757,900.00 |
| 23,900.00 | CE | 86.85 | 23,989.15 | 23,989.15 | 89.15 | 89.15 | 0.00 | 18,072,805.00 |
| 23,900.00 | PE | 0.15 | 23,989.15 | 23,989.15 | 0.00 | 0.00 | 0.00 | 34,054,760.00 |
| 23,950.00 | CE | 37.05 | 23,989.15 | 23,989.15 | 39.15 | 39.15 | 0.00 | 30,969,363.00 |
| 23,950.00 | PE | 0.60 | 23,989.15 | 23,989.15 | 0.00 | 0.00 | 0.00 | 34,689,213.00 |
| 24,000.00 | CE | 1.95 | 23,989.15 | 23,989.15 | 0.00 | 0.00 | 0.00 | 50,290,193.00 |
| 24,000.00 | PE | 14.65 | 23,989.15 | 23,989.15 | 10.85 | 10.85 | 0.00 | 23,587,709.00 |
| 24,050.00 | CE | 0.25 | 23,989.15 | 23,989.15 | 0.00 | 0.00 | 0.00 | 21,167,355.00 |
| 24,050.00 | PE | 63.25 | 23,989.15 | 23,989.15 | 60.85 | 60.85 | 0.00 | 4,161,485.00 |
| 24,100.00 | CE | 0.15 | 23,989.15 | 23,989.15 | 0.00 | 0.00 | 0.00 | 12,823,531.00 |
| 24,100.00 | PE | 113.40 | 23,989.15 | 23,989.15 | 110.85 | 110.85 | 0.00 | 1,989,414.00 |

## 10. Suspect settlement prices (`value_suspect`)

A pre-expiry option row is flagged when its `value` violates strike monotonicity against a neighbour (a put worth more than the next higher-strike put, or a call worth more than the next lower-strike call, by more than 1 point) and it is the thinner-traded side of the violating pair. These are NSE theoretical settlement prices on illiquid strikes and are not usable as prices. `value` is left untouched; `value_interp` carries a linear interpolation between the nearest clean strikes for those rows.

| year | rows | suspect_% | suspect_% strikes x100 | suspect_% strikes x50 | suspect_% within 8% of spot | suspect_% traded rows | suspect_% near & dte<=45 | interp_unavailable |
|---|---|---|---|---|---|---|---|---|
| 2019 | 765,496.00 | 3.13 | 1.03 | 11.07 | 5.22 | 1.56 | 5.18 | 40.00 |
| 2020 | 726,121.00 | 4.67 | 1.64 | 12.25 | 6.24 | 3.33 | 6.49 | 200.00 |
| 2021 | 500,885.00 | 5.99 | 1.05 | 13.91 | 6.94 | 4.06 | 6.14 | 265.00 |
| 2022 | 551,031.00 | 6.44 | 0.96 | 14.23 | 7.87 | 4.91 | 6.69 | 257.00 |
| 2023 | 331,594.00 | 7.16 | 1.11 | 16.80 | 8.44 | 4.32 | 6.02 | 195.00 |
| 2024 | 388,370.00 | 7.42 | 0.90 | 17.36 | 8.57 | 4.60 | 6.49 | 185.00 |
| 2025 | 385,460.00 | 7.00 | 0.91 | 16.37 | 8.14 | 4.55 | 6.31 | 215.00 |
| 2026 | 385,649.00 | 6.55 | 1.34 | 14.45 | 7.35 | 5.07 | 5.57 | 145.00 |


- Suspect rows: 228,120 (5.65% of pre-expiry option rows); median contracts traded on them: 0; median |value - interpolation|: 46.5 pts; 90th percentile: 168.0 pts
