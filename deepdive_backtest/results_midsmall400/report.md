# Deep Dive (Cause -> Consolidation -> Effect) Backtest Results

Universe: 259 NSE mid/small/micro caps · 2692 raw entries · Feb 2015 – Jul 2026


## 1. Headline: all raw entries vs full-template entries

| stop   | cohort         |    n |   win_rate |   avg_r |   med_r |   profit_factor |
|:-------|:---------------|-----:|-----------:|--------:|--------:|----------------:|
| 2%     | all entries    | 2692 |       20.3 |  -0.39  |  -1     |            0.51 |
| 2%     | core template  |   84 |       45.2 |   0.402 |  -1     |            1.73 |
| 2%     | strict (all 9) |   14 |       57.1 |   0.776 |   0.611 |            2.81 |
| 3%     | all entries    | 2692 |       28.4 |  -0.152 |  -1     |            0.79 |
| 3%     | core template  |   84 |       46.4 |   0.351 |  -1     |            1.64 |
| 3%     | strict (all 9) |   14 |       50   |   0.373 |  -0.167 |            1.75 |
| 5%     | all entries    | 2692 |       34   |   0.042 |  -1     |            1.06 |
| 5%     | core template  |   84 |       40.5 |   0.142 |  -1     |            1.23 |
| 5%     | strict (all 9) |   14 |       28.6 |  -0.281 |  -1     |            0.61 |
| 8%     | all entries    | 2692 |       39.3 |   0.176 |  -1     |            1.3  |
| 8%     | core template  |   84 |       42.9 |   0.227 |  -1     |            1.4  |
| 8%     | strict (all 9) |   14 |       35.7 |  -0.198 |  -1     |            0.7  |


core template = consolidation <=20% + narrow prior day + clean CQ + undercut rule respected + relative volume >=1.2x on entry day + cause <=100%.


core template split by environment (5% stop):

| env                               |   n |   win_rate |   avg_r |   med_r |   profit_factor |
|:----------------------------------|----:|-----------:|--------:|--------:|----------------:|
| strong (breadth>50%, index>20DMA) |  50 |       44   |   0.33  |      -1 |            1.57 |
| weak (breadth<=35%, index<20DMA)  |  11 |       36.4 |  -0.234 |      -1 |            0.63 |


## 2. When it works vs when it does not (univariate, 5% stop)

| condition        |   n_true |   win_true |   avgR_true |   pf_true |   n_false |   win_false |   avgR_false |   pf_false |
|:-----------------|---------:|-----------:|------------:|----------:|----------:|------------:|-------------:|-----------:|
| shallow          |     2585 |       33.8 |       0.038 |      1.06 |       107 |        38.3 |        0.128 |       1.2  |
| prior_narrow     |     1458 |       35   |       0.072 |      1.11 |      1234 |        32.9 |        0.006 |       1.01 |
| clean_cq         |     1928 |       33.4 |       0.035 |      1.05 |       764 |        35.7 |        0.059 |       1.09 |
| undercut_rule_ok |     1849 |       35.5 |       0.072 |      1.11 |       843 |        30.7 |       -0.024 |       0.97 |
| liquid_25cr      |     2692 |       34   |       0.042 |      1.06 |         0 |       nan   |      nan     |     nan    |
| fast_adr         |     2148 |       33.1 |       0.016 |      1.02 |       544 |        37.5 |        0.144 |       1.23 |
| lf_expanded      |     2130 |       34   |       0.044 |      1.07 |       562 |        34.2 |        0.034 |       1.05 |
| early_base       |     1070 |       32   |      -0.006 |      0.99 |      1622 |        35.4 |        0.073 |       1.11 |
| relvol_confirm   |      416 |       43.3 |       0.323 |      1.56 |      2276 |        32.3 |       -0.01  |       0.99 |


## 3. Market environment at entry (5% stop, all entries)

| breadth   | index_above_20dma   |   n |   win_rate |   avg_r |   med_r |   profit_factor |
|:----------|:--------------------|----:|-----------:|--------:|--------:|----------------:|
| <20%      | False               | 174 |       32.8 |  -0.005 |      -1 |            0.99 |
| 20-35%    | False               | 360 |       36.1 |   0.089 |      -1 |            1.14 |
| 20-35%    | True                |  50 |       34   |  -0.04  |      -1 |            0.94 |
| 35-50%    | False               | 275 |       29.8 |  -0.108 |      -1 |            0.85 |
| 35-50%    | True                | 342 |       27.5 |  -0.182 |      -1 |            0.75 |
| 50-65%    | False               |  87 |       34.5 |  -0.026 |      -1 |            0.96 |
| 50-65%    | True                | 531 |       33.5 |   0.009 |      -1 |            1.01 |
| >65%      | False               |   4 |        0   |  -1.026 |      -1 |            0    |
| >65%      | True                | 869 |       37.7 |   0.203 |      -1 |            1.32 |


## 4. Consolidation depth (5% stop)

| consolidation_depth   |   n |   win_rate |   avg_r |   med_r |   profit_factor |   mfe_med |
|:----------------------|----:|-----------:|--------:|--------:|----------------:|----------:|
| 0-10%                 | 997 |       33.6 |   0.039 |      -1 |            1.06 |      10.7 |
| 10-15%                | 901 |       36.7 |   0.114 |      -1 |            1.18 |      13.5 |
| 15-20%                | 485 |       30.7 |  -0.052 |      -1 |            0.93 |      12.2 |
| 20-25%                | 202 |       29.7 |  -0.091 |      -1 |            0.87 |      12.3 |
| 25-40%                | 107 |       38.3 |   0.128 |      -1 |            1.2  |      12.3 |


## 5. Cause size (5% stop)

| cause   |   n |   win_rate |   avg_r |   med_r |   profit_factor |
|:--------|----:|-----------:|--------:|--------:|----------------:|
| 25-40%  | 998 |       35.8 |   0.09  |      -1 |            1.14 |
| 40-60%  | 795 |       35.8 |   0.071 |      -1 |            1.11 |
| 60-100% | 636 |       30.8 |  -0.031 |      -1 |            0.96 |
| >100%   | 263 |       29.7 |  -0.054 |      -1 |            0.92 |


## 6. Base count (5% stop)

| base   |    n |   win_rate |   avg_r |   med_r |   profit_factor |
|:-------|-----:|-----------:|--------:|--------:|----------------:|
| 1      |  535 |       32.3 |   0.001 |      -1 |            1    |
| 2      |  535 |       31.6 |  -0.013 |      -1 |            0.98 |
| 3      |  538 |       37.2 |   0.146 |      -1 |            1.23 |
| 4+     | 1084 |       34.5 |   0.037 |      -1 |            1.06 |


## 7. Shakeout study (exit-scheme-free, 40-bar window)

| dip_threshold   |   pct_of_20pct_winners_dipping_first |   pct_of_10pct_winners_dipping_first |
|:----------------|-------------------------------------:|-------------------------------------:|
| -2%             |                                 82.1 |                                 81.6 |
| -3%             |                                 65.2 |                                 64.9 |
| -5%             |                                 42.4 |                                 42.4 |
| -8%             |                                 22.7 |                                 21.5 |

- Trades reaching +10% within 40 bars: 57.0% · reaching +20%: 30.6%

- Of trades that reached +10%, fell back to entry before reaching +20%: 40.5% (the 'losing open gains' noise the training warns about)

- Median worst dip (MAE) among eventual +20% winners: -4.9%


## 8. Stop width trade-off (all entries)

| stop   |    n |   win_rate |   avg_r |   med_r |   profit_factor |   winners_lost_to_stop_pct |
|:-------|-----:|-----------:|--------:|--------:|----------------:|---------------------------:|
| 2%     | 2692 |       20.3 |  -0.39  |      -1 |            0.51 |                       74.2 |
| 3%     | 2692 |       28.4 |  -0.152 |      -1 |            0.79 |                       58.4 |
| 5%     | 2692 |       34   |   0.042 |      -1 |            1.06 |                       38.8 |
| 8%     | 2692 |       39.3 |   0.176 |      -1 |            1.3  |                       22.1 |


## 9. Year by year (5% stop, full template)

|   year |   n |   win_rate |   avg_r |   med_r |   profit_factor |
|-------:|----:|-----------:|--------:|--------:|----------------:|
|   2015 |   1 |        0   |  -1     |  -1     |            0    |
|   2016 |   1 |        0   |  -1     |  -1     |            0    |
|   2017 |   3 |       33.3 |  -0.444 |  -1     |            0.33 |
|   2018 |   5 |       20   |  -0.667 |  -1     |            0.17 |
|   2019 |   6 |       66.7 |   1.101 |   1.532 |            4.3  |
|   2020 |   4 |        0   |  -1     |  -1     |            0    |
|   2021 |   8 |       25   |  -0.434 |  -1     |            0.44 |
|   2022 |   8 |       25   |  -0.25  |  -1     |            0.67 |
|   2023 |  12 |       50   |   0.788 |  -0.167 |            2.58 |
|   2024 |  20 |       60   |   0.775 |   0.667 |            2.93 |
|   2025 |   8 |       25   |  -0.704 |  -1     |            0.19 |
|   2026 |   8 |       50   |   0.269 |  -0.067 |            1.54 |