# NIFTY options data validation report

Generated 2026-11-21 14:34 UTC. Rows: 562,205; trade dates: 183 (2019-01-01 .. 2024-07-09); spot-check seed 42.

## 0. Flags

- **FLAG** 1177 weekday(s) have no F&O bhavcopy and are not in the holiday list (section 1a)
- **FLAG** 14 index-file days have no F&O file (section 1d)
- **FLAG** months without any expiry: ['2020-01', '2020-02', '2020-04', '2020-05', '2020-07', '2020-08', '2020-09', '2020-10', '2020-11', '2021-01', '2021-02', '2021-03', '2021-04', '2021-05', '2021-07', '2021-08', '2021-09', '2021-10', '2021-11', '2022-01', '2022-02', '2022-03', '2022-04', '2022-05', '2022-07', '2022-08', '2022-09', '2022-10', '2022-11', '2023-01', '2023-02', '2023-03', '2023-04', '2023-05', '2023-07', '2023-08', '2023-09', '2023-10', '2023-11', '2024-01', '2024-02', '2024-03', '2024-04', '2024-05']
- **FLAG** 1 gaps > 5 calendar days in the spot/VIX series (section 6b)
- **FLAG** 4351 option rows with open interest/volume but settle = 0 before expiry (section 8)
- **FLAG** 26,154 pre-expiry option rows have settle = 0 (untraded, zero OI; mostly old format). Treat settle=0 as 'no price', not a price (section 8)

## 1. Trading-day calendar

Date range with F&O files: **2019-01-01 .. 2024-07-09**. Holiday list sources: {'bundled': 102, 'nse_api': 20} (the NSE holiday API is attempted every run; when it is unreachable only the bundled, hand-entered list is used).

| year | fo_trading_days | index_days | weekdays_without_fo_file | of_which_listed_holidays | of_which_NOT_listed | weekend_sessions_with_data |
|---|---|---|---|---|---|---|
| 2019 | 178 | 192 | 83 | 17 | 66 | 0 |
| 2020 | 0 | 0 | 262 | 12 | 250 | 0 |
| 2021 | 0 | 0 | 261 | 14 | 247 | 0 |
| 2022 | 0 | 0 | 260 | 13 | 247 | 0 |
| 2023 | 0 | 0 | 260 | 15 | 245 | 0 |
| 2024 | 5 | 5 | 132 | 10 | 122 | 0 |


### 1a. Weekdays with no F&O file that are NOT in the holiday list

**FLAG** these need a look: either the bundled holiday list is incomplete, or NSE has a gap.


| date | weekday | fo_old | fo_udiff | index_file | note |
|---|---|---|---|---|---|
| 2019-09-23 | Mon | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-09-24 | Tue | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-09-25 | Wed | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-09-26 | Thu | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-09-27 | Fri | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-09-30 | Mon | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-10-01 | Tue | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-10-03 | Thu | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-10-04 | Fri | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-10-07 | Mon | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-10-09 | Wed | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-10-10 | Thu | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-10-11 | Fri | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-10-14 | Mon | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-10-15 | Tue | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-10-16 | Wed | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-10-17 | Thu | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-10-18 | Fri | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-10-22 | Tue | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-10-23 | Wed | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-10-24 | Thu | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-10-25 | Fri | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-10-29 | Tue | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-10-30 | Wed | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-10-31 | Thu | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-11-01 | Fri | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-11-04 | Mon | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-11-05 | Tue | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-11-06 | Wed | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-11-07 | Thu | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-11-08 | Fri | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-11-11 | Mon | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-11-13 | Wed | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-11-14 | Thu | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-11-15 | Fri | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-11-18 | Mon | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-11-19 | Tue | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-11-20 | Wed | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-11-21 | Thu | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-11-22 | Fri | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-11-25 | Mon | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-11-26 | Tue | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-11-27 | Wed | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-11-28 | Thu | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-11-29 | Fri | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-12-02 | Mon | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-12-03 | Tue | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-12-04 | Wed | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-12-05 | Thu | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-12-06 | Fri | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-12-09 | Mon | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-12-10 | Tue | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-12-11 | Wed | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-12-12 | Thu | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-12-13 | Fri | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-12-16 | Mon | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-12-17 | Tue | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-12-18 | Wed | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-12-19 | Thu | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-12-20 | Fri | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-12-23 | Mon | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-12-24 | Tue | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-12-26 | Thu | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-12-27 | Fri | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-12-30 | Mon | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2019-12-31 | Tue | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2020-01-01 | Wed | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2020-01-02 | Thu | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2020-01-03 | Fri | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2020-01-06 | Mon | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2020-01-07 | Tue | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2020-01-08 | Wed | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2020-01-09 | Thu | ok | - | ok | index file exists -> market was open, F&O file missing! |
| 2020-01-10 | Fri | - | - | ok | index file exists -> market was open, F&O file missing! |
| 2020-01-13 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-01-14 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-01-15 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-01-16 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-01-17 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-01-20 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-01-21 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-01-22 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-01-23 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-01-24 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-01-27 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-01-28 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-01-29 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-01-30 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-01-31 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-02-03 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-02-04 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-02-05 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-02-06 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-02-07 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-02-10 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-02-11 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-02-12 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-02-13 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-02-14 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-02-17 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-02-18 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-02-19 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-02-20 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-02-24 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-02-25 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-02-26 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-02-27 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-02-28 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-03-02 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-03-03 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-03-04 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-03-05 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-03-06 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-03-09 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-03-11 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-03-12 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-03-13 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-03-16 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-03-17 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-03-18 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-03-19 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-03-20 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-03-23 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-03-24 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-03-25 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-03-26 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-03-27 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-03-30 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-03-31 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-04-01 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-04-03 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-04-07 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-04-08 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-04-09 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-04-13 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-04-15 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-04-16 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-04-17 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-04-20 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-04-21 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-04-22 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-04-23 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-04-24 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-04-27 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-04-28 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-04-29 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-04-30 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-05-04 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-05-05 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-05-06 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-05-07 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-05-08 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-05-11 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-05-12 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-05-13 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-05-14 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-05-15 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-05-18 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-05-19 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-05-20 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-05-21 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-05-22 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-05-26 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-05-27 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-05-28 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-05-29 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-06-01 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-06-02 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-06-03 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-06-04 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-06-05 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-06-08 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-06-09 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-06-10 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-06-11 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-06-12 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-06-15 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-06-16 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-06-17 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-06-18 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-06-19 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-06-22 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-06-23 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-06-24 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-06-25 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-06-26 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-06-29 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-06-30 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-07-01 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-07-02 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-07-03 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-07-06 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-07-07 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-07-08 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-07-09 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-07-10 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-07-13 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-07-14 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-07-15 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-07-16 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-07-17 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-07-20 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-07-21 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-07-22 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-07-23 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-07-24 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-07-27 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-07-28 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-07-29 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-07-30 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-07-31 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-08-03 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-08-04 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-08-05 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-08-06 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-08-07 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-08-10 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-08-11 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-08-12 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-08-13 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-08-14 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-08-17 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-08-18 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-08-19 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-08-20 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-08-21 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-08-24 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-08-25 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-08-26 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-08-27 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-08-28 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-08-31 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-09-01 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-09-02 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-09-03 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-09-04 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-09-07 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-09-08 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-09-09 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-09-10 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-09-11 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-09-14 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-09-15 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-09-16 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-09-17 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-09-18 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-09-21 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-09-22 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-09-23 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-09-24 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-09-25 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-09-28 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-09-29 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-09-30 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-10-01 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-10-05 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-10-06 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-10-07 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-10-08 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-10-09 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-10-12 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-10-13 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-10-14 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-10-15 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-10-16 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-10-19 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-10-20 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-10-21 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-10-22 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-10-23 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-10-26 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-10-27 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-10-28 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-10-29 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-10-30 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-11-02 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-11-03 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-11-04 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-11-05 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-11-06 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-11-09 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-11-10 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-11-11 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-11-12 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-11-13 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-11-17 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-11-18 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-11-19 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-11-20 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-11-23 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-11-24 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-11-25 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-11-26 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-11-27 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-12-01 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-12-02 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-12-03 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-12-04 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-12-07 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-12-08 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-12-09 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-12-10 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-12-11 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-12-14 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-12-15 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-12-16 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-12-17 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-12-18 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-12-21 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-12-22 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-12-23 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-12-24 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-12-28 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-12-29 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-12-30 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2020-12-31 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-01-01 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-01-04 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-01-05 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-01-06 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-01-07 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-01-08 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-01-11 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-01-12 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-01-13 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-01-14 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-01-15 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-01-18 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-01-19 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-01-20 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-01-21 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-01-22 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-01-25 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-01-27 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-01-28 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-01-29 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-02-01 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-02-02 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-02-03 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-02-04 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-02-05 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-02-08 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-02-09 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-02-10 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-02-11 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-02-12 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-02-15 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-02-16 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-02-17 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-02-18 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-02-19 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-02-22 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-02-23 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-02-24 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-02-25 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-02-26 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-03-01 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-03-02 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-03-03 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-03-04 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-03-05 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-03-08 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-03-09 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-03-10 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-03-12 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-03-15 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-03-16 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-03-17 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-03-18 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-03-19 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-03-22 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-03-23 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-03-24 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-03-25 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-03-26 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-03-30 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-03-31 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-04-01 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-04-05 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-04-06 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-04-07 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-04-08 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-04-09 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-04-12 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-04-13 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-04-15 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-04-16 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-04-19 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-04-20 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-04-22 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-04-23 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-04-26 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-04-27 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-04-28 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-04-29 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-04-30 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-05-03 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-05-04 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-05-05 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-05-06 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-05-07 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-05-10 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-05-11 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-05-12 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-05-14 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-05-17 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-05-18 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-05-19 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-05-20 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-05-21 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-05-24 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-05-25 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-05-26 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-05-27 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-05-28 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-05-31 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-06-01 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-06-02 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-06-03 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-06-04 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-06-07 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-06-08 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-06-09 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-06-10 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-06-11 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-06-14 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-06-15 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-06-16 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-06-17 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-06-18 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-06-21 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-06-22 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-06-23 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-06-24 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-06-25 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-06-28 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-06-29 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-06-30 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-07-01 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-07-02 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-07-05 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-07-06 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-07-07 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-07-08 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-07-09 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-07-12 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-07-13 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-07-14 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-07-15 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-07-16 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-07-19 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-07-20 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-07-22 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-07-23 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-07-26 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-07-27 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-07-28 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-07-29 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-07-30 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-08-02 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-08-03 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-08-04 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-08-05 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-08-06 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-08-09 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-08-10 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-08-11 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-08-12 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-08-13 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-08-16 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-08-17 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-08-18 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-08-20 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-08-23 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-08-24 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-08-25 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-08-26 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-08-27 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-08-30 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-08-31 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-09-01 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-09-02 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-09-03 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-09-06 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-09-07 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-09-08 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-09-09 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-09-13 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-09-14 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-09-15 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-09-16 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-09-17 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-09-20 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-09-21 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-09-22 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-09-23 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-09-24 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-09-27 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-09-28 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-09-29 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-09-30 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-10-01 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-10-04 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-10-05 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-10-06 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-10-07 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-10-08 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-10-11 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-10-12 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-10-13 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-10-14 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-10-18 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-10-19 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-10-20 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-10-21 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-10-22 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-10-25 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-10-26 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-10-27 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-10-28 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-10-29 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-11-01 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-11-02 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-11-03 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-11-08 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-11-09 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-11-10 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-11-11 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-11-12 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-11-15 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-11-16 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-11-17 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-11-18 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-11-22 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-11-23 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-11-24 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-11-25 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-11-26 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-11-29 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-11-30 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-12-01 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-12-02 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-12-03 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-12-06 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-12-07 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-12-08 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-12-09 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-12-10 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-12-13 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-12-14 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-12-15 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-12-16 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-12-17 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-12-20 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-12-21 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-12-22 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-12-23 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-12-24 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-12-27 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-12-28 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-12-29 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-12-30 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2021-12-31 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-01-03 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-01-04 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-01-05 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-01-06 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-01-07 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-01-10 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-01-11 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-01-12 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-01-13 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-01-14 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-01-17 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-01-18 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-01-19 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-01-20 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-01-21 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-01-24 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-01-25 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-01-27 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-01-28 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-01-31 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-02-01 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-02-02 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-02-03 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-02-04 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-02-07 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-02-08 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-02-09 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-02-10 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-02-11 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-02-14 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-02-15 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-02-16 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-02-17 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-02-18 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-02-21 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-02-22 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-02-23 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-02-24 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-02-25 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-02-28 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-03-02 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-03-03 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-03-04 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-03-07 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-03-08 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-03-09 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-03-10 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-03-11 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-03-14 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-03-15 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-03-16 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-03-17 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-03-21 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-03-22 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-03-23 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-03-24 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-03-25 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-03-28 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-03-29 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-03-30 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-03-31 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-04-01 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-04-04 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-04-05 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-04-06 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-04-07 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-04-08 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-04-11 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-04-12 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-04-13 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-04-18 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-04-19 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-04-20 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-04-21 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-04-22 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-04-25 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-04-26 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-04-27 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-04-28 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-04-29 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-05-02 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-05-04 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-05-05 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-05-06 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-05-09 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-05-10 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-05-11 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-05-12 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-05-13 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-05-16 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-05-17 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-05-18 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-05-19 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-05-20 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-05-23 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-05-24 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-05-25 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-05-26 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-05-27 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-05-30 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-05-31 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-06-01 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-06-02 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-06-03 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-06-06 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-06-07 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-06-08 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-06-09 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-06-10 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-06-13 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-06-14 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-06-15 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-06-16 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-06-17 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-06-20 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-06-21 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-06-22 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-06-23 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-06-24 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-06-27 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-06-28 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-06-29 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-06-30 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-07-01 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-07-04 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-07-05 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-07-06 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-07-07 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-07-08 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-07-11 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-07-12 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-07-13 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-07-14 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-07-15 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-07-18 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-07-19 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-07-20 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-07-21 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-07-22 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-07-25 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-07-26 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-07-27 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-07-28 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-07-29 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-08-01 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-08-02 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-08-03 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-08-04 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-08-05 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-08-08 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-08-10 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-08-11 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-08-12 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-08-16 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-08-17 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-08-18 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-08-19 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-08-22 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-08-23 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-08-24 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-08-25 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-08-26 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-08-29 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-08-30 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-09-01 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-09-02 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-09-05 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-09-06 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-09-07 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-09-08 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-09-09 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-09-12 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-09-13 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-09-14 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-09-15 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-09-16 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-09-19 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-09-20 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-09-21 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-09-22 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-09-23 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-09-26 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-09-27 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-09-28 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-09-29 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-09-30 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-10-03 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-10-04 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-10-06 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-10-07 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-10-10 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-10-11 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-10-12 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-10-13 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-10-14 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-10-17 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-10-18 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-10-19 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-10-20 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-10-21 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-10-25 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-10-27 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-10-28 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-10-31 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-11-01 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-11-02 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-11-03 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-11-04 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-11-07 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-11-09 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-11-10 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-11-11 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-11-14 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-11-15 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-11-16 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-11-17 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-11-18 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-11-21 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-11-22 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-11-23 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-11-24 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-11-25 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-11-28 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-11-29 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-11-30 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-12-01 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-12-02 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-12-05 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-12-06 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-12-07 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-12-08 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-12-09 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-12-12 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-12-13 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-12-14 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-12-15 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-12-16 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-12-19 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-12-20 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-12-21 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-12-22 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-12-23 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-12-26 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-12-27 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-12-28 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-12-29 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2022-12-30 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-01-02 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-01-03 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-01-04 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-01-05 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-01-06 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-01-09 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-01-10 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-01-11 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-01-12 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-01-13 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-01-16 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-01-17 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-01-18 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-01-19 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-01-20 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-01-23 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-01-24 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-01-25 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-01-27 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-01-30 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-01-31 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-02-01 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-02-02 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-02-03 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-02-06 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-02-07 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-02-08 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-02-09 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-02-10 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-02-13 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-02-14 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-02-15 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-02-16 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-02-17 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-02-20 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-02-21 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-02-22 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-02-23 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-02-24 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-02-27 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-02-28 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-03-01 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-03-02 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-03-03 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-03-06 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-03-08 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-03-09 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-03-10 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-03-13 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-03-14 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-03-15 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-03-16 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-03-17 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-03-20 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-03-21 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-03-22 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-03-23 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-03-24 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-03-27 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-03-28 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-03-29 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-03-31 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-04-03 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-04-05 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-04-06 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-04-10 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-04-11 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-04-12 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-04-13 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-04-17 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-04-18 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-04-19 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-04-20 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-04-21 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-04-24 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-04-25 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-04-26 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-04-27 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-04-28 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-05-02 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-05-03 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-05-04 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-05-05 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-05-08 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-05-09 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-05-10 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-05-11 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-05-12 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-05-15 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-05-16 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-05-17 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-05-18 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-05-19 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-05-22 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-05-23 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-05-24 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-05-25 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-05-26 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-05-29 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-05-30 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-05-31 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-06-01 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-06-02 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-06-05 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-06-06 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-06-07 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-06-08 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-06-09 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-06-12 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-06-13 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-06-14 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-06-15 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-06-16 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-06-19 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-06-20 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-06-21 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-06-22 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-06-23 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-06-26 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-06-27 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-06-28 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-06-30 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-07-03 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-07-04 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-07-05 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-07-06 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-07-07 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-07-10 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-07-11 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-07-12 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-07-13 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-07-14 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-07-17 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-07-18 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-07-19 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-07-20 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-07-21 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-07-24 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-07-25 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-07-26 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-07-27 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-07-28 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-07-31 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-08-01 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-08-02 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-08-03 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-08-04 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-08-07 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-08-08 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-08-09 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-08-10 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-08-11 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-08-14 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-08-16 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-08-17 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-08-18 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-08-21 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-08-22 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-08-23 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-08-24 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-08-25 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-08-28 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-08-29 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-08-30 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-08-31 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-09-01 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-09-04 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-09-05 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-09-06 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-09-07 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-09-08 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-09-11 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-09-12 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-09-13 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-09-14 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-09-15 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-09-18 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-09-20 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-09-21 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-09-22 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-09-25 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-09-26 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-09-27 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-09-28 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-09-29 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-10-03 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-10-04 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-10-05 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-10-06 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-10-09 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-10-10 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-10-11 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-10-12 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-10-13 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-10-16 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-10-17 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-10-18 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-10-19 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-10-20 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-10-23 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-10-25 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-10-26 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-10-27 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-10-30 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-10-31 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-11-01 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-11-02 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-11-03 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-11-06 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-11-07 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-11-08 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-11-09 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-11-10 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-11-13 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-11-15 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-11-16 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-11-17 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-11-20 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-11-21 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-11-22 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-11-23 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-11-24 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-11-28 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-11-29 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-11-30 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-12-01 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-12-04 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-12-05 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-12-06 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-12-07 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-12-08 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-12-11 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-12-12 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-12-13 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-12-14 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-12-15 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-12-18 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-12-19 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-12-20 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-12-21 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-12-22 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-12-26 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-12-27 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-12-28 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2023-12-29 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-01-01 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-01-02 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-01-03 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-01-04 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-01-05 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-01-08 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-01-09 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-01-10 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-01-11 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-01-12 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-01-15 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-01-16 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-01-17 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-01-18 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-01-19 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-01-23 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-01-24 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-01-25 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-01-29 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-01-30 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-01-31 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-02-01 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-02-02 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-02-05 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-02-06 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-02-07 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-02-08 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-02-09 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-02-12 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-02-13 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-02-14 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-02-15 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-02-16 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-02-19 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-02-20 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-02-21 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-02-22 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-02-23 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-02-26 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-02-27 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-02-28 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-02-29 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-03-01 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-03-04 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-03-05 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-03-06 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-03-07 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-03-11 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-03-12 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-03-13 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-03-14 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-03-15 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-03-18 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-03-19 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-03-20 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-03-21 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-03-22 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-03-26 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-03-27 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-03-28 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-04-01 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-04-02 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-04-03 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-04-04 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-04-05 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-04-08 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-04-09 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-04-10 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-04-12 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-04-15 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-04-16 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-04-18 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-04-19 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-04-22 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-04-23 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-04-24 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-04-25 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-04-26 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-04-29 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-04-30 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-05-02 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-05-03 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-05-06 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-05-07 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-05-08 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-05-09 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-05-10 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-05-13 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-05-14 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-05-15 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-05-16 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-05-17 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-05-21 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-05-22 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-05-23 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-05-24 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-05-27 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-05-28 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-05-29 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-05-30 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-05-31 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-06-03 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-06-04 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-06-05 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-06-06 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-06-07 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-06-10 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-06-11 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-06-12 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-06-13 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-06-14 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-06-18 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-06-19 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-06-20 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-06-21 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-06-24 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-06-25 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-06-26 | Wed | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-06-27 | Thu | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-06-28 | Fri | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-07-01 | Mon | - | - | - | no index file either -> probably a holiday missing from the list |
| 2024-07-02 | Tue | - | - | - | no index file either -> probably a holiday missing from the list |


### 1b. Listed holidays that DO have an F&O file (special sessions, or a wrong holiday entry)

_(none)_


### 1c. Weekend dates with an F&O file (special / Muhurat / budget sessions)

_(none)_


### 1d. Days present in only one of the two sources

- F&O file but no index file: 0 []

- Index file but no F&O file: 14 ['2019-09-23', '2019-09-24', '2019-09-25', '2019-09-26', '2019-09-27', '2019-09-30', '2019-10-01', '2019-10-03', '2019-10-04', '2019-10-07', '2019-10-09', '2019-10-10', '2019-10-11', '2019-10-14']

## 2. Row counts per year, per source format

- Last date with an old-format file: **2024-07-05**

- First date with a UDiFF file: **2024-07-03** (NSE back-filled UDiFF for 2024)

- First weekday where only UDiFF exists (observed cutover): **2024-07-08**

- Configured cutover: old format up to 2024-07-05, UDiFF from 2024-07-08


| year | old_FUT | old_OPT | udiff_FUT | udiff_OPT | trading_days | opt_rows_per_day |
|---|---|---|---|---|---|---|
| 2,019 | 534 | 553,334 | 0 | 0 | 178 | 3,109 |
| 2,024 | 9 | 5,054 | 6 | 3,268 | 5 | 1,664 |

## 3. Expiry calendar

Monthly expiry = last expiry date observed in each calendar month (from option listings).


### 3a. Monthly expiry dates by year

- **2019** (12): 2019-01-31 (Thu), 2019-02-28 (Thu), 2019-03-28 (Thu), 2019-04-25 (Thu), 2019-05-30 (Thu), 2019-06-27 (Thu), 2019-07-25 (Thu), 2019-08-29 (Thu), 2019-09-26 (Thu), 2019-10-31 (Thu), 2019-11-28 (Thu), 2019-12-26 (Thu)

- **2020** (3): 2020-03-26 (Thu), 2020-06-25 (Thu), 2020-12-31 (Thu)

- **2021** (2): 2021-06-24 (Thu), 2021-12-30 (Thu)

- **2022** (2): 2022-06-30 (Thu), 2022-12-29 (Thu)

- **2023** (2): 2023-06-29 (Thu), 2023-12-28 (Thu)

- **2024** (5): 2024-06-27 (Thu), 2024-07-25 (Thu), 2024-08-29 (Thu), 2024-09-26 (Thu), 2024-12-26 (Thu)

- **2025** (3): 2025-03-27 (Thu), 2025-06-26 (Thu), 2025-12-24 (Wed)

- **2026** (2): 2026-06-25 (Thu), 2026-12-31 (Thu)

- **2027** (2): 2027-06-24 (Thu), 2027-12-30 (Thu)

- **2028** (2): 2028-06-29 (Thu), 2028-12-28 (Thu)

- **2029** (1): 2029-06-28 (Thu)


### 3b. Expiry weekday by year (shows NSE moving the expiry day)

| year | is_monthly | Thursday | Wednesday |
|---|---|---|---|
| 2019 | False | 30 | 2 |
| 2019 | True | 12 | 0 |
| 2020 | True | 3 | 0 |
| 2021 | True | 2 | 0 |
| 2022 | True | 2 | 0 |
| 2023 | True | 2 | 0 |
| 2024 | False | 1 | 0 |
| 2024 | True | 1 | 0 |


### 3c. Consistency checks

- Futures expiries not flagged as monthly: 0 []

- Months in range without any option expiry: ['2020-01', '2020-02', '2020-04', '2020-05', '2020-07', '2020-08', '2020-09', '2020-10', '2020-11', '2021-01', '2021-02', '2021-03', '2021-04', '2021-05', '2021-07', '2021-08', '2021-09', '2021-10', '2021-11', '2022-01', '2022-02', '2022-03', '2022-04', '2022-05', '2022-07', '2022-08', '2022-09', '2022-10', '2022-11', '2023-01', '2023-02', '2023-03', '2023-04', '2023-05', '2023-07', '2023-08', '2023-09', '2023-10', '2023-11', '2024-01', '2024-02', '2024-03', '2024-04', '2024-05']

- Long-dated (quarterly/half-yearly) expiries beyond the data end, flagged monthly by construction: ['2024-12-26', '2025-03-27', '2025-06-26', '2025-12-24', '2026-06-25', '2026-12-31', '2027-06-24', '2027-12-30', '2028-06-29', '2028-12-28', '2029-06-28']

- Rows with expiry before trade date (dte < 0): 0

## 4. Illiquid strikes: share of option rows with zero contracts traded

All years, all expiries, distance = strike / underlying - 1:

| strike vs underlying | rows | zero-volume share % |
|---|---|---|
| < -20% | 113586 | 97.6 |
| -20..-10% | 91550 | 91.9 |
| -10..-5% | 59636 | 85.8 |
| -5..-2.5% | 29598 | 79.3 |
| -2.5..-1% | 17844 | 74.0 |
| -1..+1% (ATM) | 24056 | 69.8 |
| +1..2.5% | 17958 | 73.0 |
| +2.5..5% | 29692 | 78.7 |
| +5..10% | 58852 | 86.9 |
| +10..20% | 85180 | 94.4 |
| > +20% | 33704 | 97.6 |


By year, zero-volume share % (all strikes / within ±2.5% of spot / dte <= 7):

| year | all_strikes | within_2.5pct | dte_le_7 | dte_gt_60 |
|---|---|---|---|---|
| 2,019.0 | 89.7 | 73.5 | 50.7 | 96.7 |
| 2,024.0 | 47.8 | 23.9 | 14.2 | 73.8 |


Note: on zero-volume rows `close` is NSE's last traded price (possibly days old) while `settle` is the exchange settlement price; they differ on 499,868 of 500,502 zero-volume rows (99.9%). Use `settle` for illiquid strikes.

## 5. Spot checks: ATM call/put vs underlying and put-call parity vs the same-expiry future

Parity used: C - P = (F - K) * exp(-r*T) with r = 6.5%; `implied_fwd` = K + (C - P) * exp(r*T). Residual is reported in index points and as % of spot. Only monthly expiries have a same-expiry future; for the nearest weekly expiry the implied forward is compared with spot instead.


### 5a. Nearest monthly expiry (future exists)
| trade_date | spot | expiry | dte | atm_strike | call_close | put_close | future_close | implied_fwd | parity_resid_pts | resid_pct_spot | atm_call_pct_spot |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2019-01-09 | 10,855.15 | 2019-01-31 | 22 | 10,850.00 | 163.45 | 136.90 | 10,877.70 | 10,876.65 | -1.04 | -0.01 | 1.51 |
| 2019-02-08 | 10,943.60 | 2019-02-28 | 20 | 10,950.00 | 136.80 | 133.80 | 10,957.25 | 10,953.01 | -4.22 | -0.04 | 1.25 |
| 2019-04-01 | 11,669.15 | 2019-04-25 | 24 | 11,650.00 | 222.90 | 136.35 | 11,748.40 | 11,736.92 | -11.43 | -0.10 | 1.91 |
| 2019-04-11 | 11,596.70 | 2019-04-25 | 14 | 11,600.00 | 151.40 | 83.45 | 11,668.90 | 11,668.12 | -0.78 | -0.01 | 1.31 |
| 2019-08-29 | 10,948.30 | 2019-09-26 | 28 | 10,950.00 | 215.55 | 162.20 | 11,002.35 | 11,003.62 | 1.26 | 0.01 | 1.97 |


### 5b. Nearest weekly expiry (no same-expiry future; implied forward vs spot)
| trade_date | spot | weekly_expiry | dte | atm_strike | call_close | put_close | implied_fwd | fwd_minus_spot_pct | next_monthly_future |
|---|---|---|---|---|---|---|---|---|---|
| 2019-04-01 | 11,669.15 | 2019-04-04 | 3 | 11,650.00 | 84.60 | 45.40 | 11,689.22 | 0.17 | 11,748.40 |
| 2019-04-11 | 11,596.70 | 2019-04-18 | 7 | 11,600.00 | 90.40 | 53.70 | 11,636.75 | 0.35 | 11,668.90 |
| 2019-08-29 | 10,948.30 | 2019-09-05 | 7 | 10,950.00 | 111.35 | 80.25 | 10,981.14 | 0.30 | 11,002.35 |


What 'roughly holds' means here: a residual within about 0.1-0.3% of spot is normal (bid-ask, stale closes, dividend/rate assumptions). Weekly implied forwards sit slightly above spot by the carry; a weekly implied forward far from spot or from the monthly future would be a flag.

## 6. NIFTY 50 spot and India VIX series

- Index-file days: 197; days with missing/zero Nifty 50 close: 0; missing/zero India VIX close: 0

- F&O days with no underlying at all: 0 []

- F&O days with no VIX close: 0 []


### 6a. Large day-over-day moves (|spot| > 7% or |VIX| > 40%) - check these are real events

| trade_date | spot_close | spot_ret_pct | vix_close | vix_chg_pct |
|---|---|---|---|---|
| 2024-07-03 | 24,286.50 | 114.14 | 13.21 | -24.21 |


### 6b. Gaps of more than 5 calendar days between consecutive index-file days

| trade_date | gap_days |
|---|---|
| 2024-07-03 | 1724 |


### 6c. UDiFF `UndrlygPric` vs Nifty 50 close from the index file
- days compared: 2; days differing by > 0.5 pts: 0

- days where UDiFF rows carry more than one underlying value for NIFTY: 0

## 7. Old-format vs UDiFF reconciliation on overlap dates (Jan-Jul 2024)

Dates with both files: 3 (2024-07-03 .. 2024-07-05)

Total contract-days with any difference: **0**


| rows_old | rows_udiff | only_in_old | only_in_udiff | diff_open | diff_high | diff_low | diff_close | diff_settle | diff_contracts_traded | diff_open_interest |
|---|---|---|---|---|---|---|---|---|---|---|
| 5063 | 5063 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## 8. Row-level integrity

- Duplicate contract-days: 0

- Option rows with option_type not CE/PE: 0; futures rows with a non-blank option_type: 0

- Rows with a negative price: 0

- Traded rows where close is outside [low, high] or high < low: 0

- Rows with close <= 0 but open interest > 0: 0

- Option rows with settle <= 0: 35,897 = expiry-day rows expiring worthless 5,392 (expected) + untraded zero-OI strikes before expiry 26,154 (old format leaves settle at 0 for strikes nobody holds; `close` there is a stale last-traded price) + rows WITH OI or volume but settle 0 before expiry 4,351

| year | rows |
|---|---|
| 2019 | 4305 |
| 2024 | 46 |

- NaN counts: none

- Futures rows per day: min 3, max 3 (NSE lists 3 monthly futures)

- Minimum strike step on near expiries by year: {2019: 50.0, 2024: 50.0}

- Units: `contracts_traded` is in contracts (lots); `open_interest` is in units of underlying (lots x lot size) in BOTH formats, consistent with each other on the overlap dates. Lot size changed over time (75 -> 50 -> 25 -> 75), so OI is not comparable across years without dividing by lot size.
