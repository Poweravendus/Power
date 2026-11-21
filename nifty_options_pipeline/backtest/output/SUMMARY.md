# NIFTY defined-risk monthly option selling: backtest summary

Data: NSE bhavcopy 2019-01-01 to 2026-11-20, prices = `value` (settle before expiry, intrinsic at expiry). Rules: one new position on the first trading day of each week in the nearest monthly expiry with 28-45 dte, short strike nearest 0.16 delta (Black-76 on the same-expiry future), wing 300 pts further OTM, take profit at 50% of credit, stop at 1.5x credit, time exit at 7 dte. Costs: Rs 20/order/leg, STT, NSE/SEBI/stamp charges, GST, 1 pt slippage per leg per trade (x2 when VIX > 25). All rupee figures per lot of 65 units.

## Headline results (net of all costs)

| Run | Period | Trades | Win rate | Expectancy Rs/trade | Total Rs/lot | Annual Rs/lot | Max DD Rs/lot | DD % capital | Capital at risk Rs/lot |
|---|---|---|---|---|---|---|---|---|---|
| PCS VIX ON | 2019-2026 | 270 | 78.9% | -158 | -42,639 | -5,406 | -61,228 | 84.3% | 72,605 |
| PCS VIX ON | 2021-2026 | 199 | 77.9% | -193 | -38,436 | -6,530 | -58,454 | 80.8% | 72,384 |
| PCS VIX OFF | 2019-2026 | 279 | 78.5% | -164 | -45,861 | -5,814 | -64,450 | 71.0% | 90,756 |
| PCS VIX OFF | 2021-2026 | 208 | 77.4% | -200 | -41,658 | -7,077 | -61,676 | 68.2% | 90,480 |
| IC VIX ON | 2019-2026 | 269 | 71.7% | -842 | -226,484 | -28,713 | -244,692 | 347.9% | 70,330 |
| IC VIX ON | 2021-2026 | 199 | 72.4% | -834 | -165,991 | -28,199 | -196,033 | 278.7% | 70,330 |
| IC VIX OFF | 2019-2026 | 278 | 71.9% | -809 | -224,898 | -28,512 | -243,106 | 345.7% | 70,330 |
| IC VIX OFF | 2021-2026 | 208 | 72.6% | -790 | -164,405 | -27,930 | -194,447 | 276.5% | 70,330 |

## Holdout (Jan 2025 to latest, base case run once, not re-tuned)

| Run | Trades | Win rate | Expectancy Rs/trade | Total Rs/lot | Annual Rs/lot | Max DD Rs/lot |
|---|---|---|---|---|---|---|
| PCS VIX ON | 60 | 76.7% | -292 | -17,510 | -9,282 | -30,470 |
| PCS VIX OFF | 65 | 76.9% | -283 | -18,395 | -9,751 | -30,563 |
| IC VIX ON | 60 | 75.0% | -811 | -48,680 | -25,806 | -66,142 |
| IC VIX OFF | 65 | 75.4% | -752 | -48,893 | -25,919 | -66,142 |

## Does it beat doing nothing (a Nifty index fund), after tax?

F&O profits taxed at 30% as business income; index-fund gains at 12.5% LTCG (no exemption, no dividends, which understates the fund by roughly 1-1.5% a year). The fund is assumed to hold the same capital the strategy needs (max defined loss x max concurrent positions). Strategy capital is assumed idle; parking it in a liquid fund would add about 6% a year pre-tax to the strategy side.

| Run | Period | Strategy after tax Rs/lot | Nifty fund after tax Rs/lot | Strategy CAGR | Nifty CAGR | Verdict |
|---|---|---|---|---|---|---|
| PCS VIX ON | 2019-2026 | -42,639 | 86,707 | -10.6% | 10.5% | loses to the index fund |
| PCS VIX ON | 2021-2026 | -38,436 | 53,232 | -12.1% | 9.8% | loses to the index fund |
| PCS VIX OFF | 2019-2026 | -45,861 | 108,384 | -8.5% | 10.5% | loses to the index fund |
| PCS VIX OFF | 2021-2026 | -41,658 | 66,540 | -10.0% | 9.8% | loses to the index fund |
| IC VIX ON | 2019-2026 | -226,484 | 83,990 | n/a | 10.5% | loses to the index fund |
| IC VIX ON | 2021-2026 | -165,991 | 51,721 | n/a | 9.8% | loses to the index fund |
| IC VIX OFF | 2019-2026 | -224,898 | 83,990 | n/a | 10.5% | loses to the index fund |
| IC VIX OFF | 2021-2026 | -164,405 | 51,721 | n/a | 9.8% | loses to the index fund |

**Plain verdict: no.** In none of the headline runs does the strategy beat a Nifty index fund after tax, over the full period or from 2021. The exit rules (50% take profit against a 1.5x stop) need a win rate above 75% just to break even before costs, and the realised win rate does not clear that bar once costs and slippage are charged.

## What drives the result

- Breakeven win rate implied by the exit rules is 75.0%; realised avg win / avg loss implies 81.9% (put spread, VIX OFF, full period). Realised win rate 78.5%.
- Costs and slippage: average credit 31.7 pts; 1 pt slippage per leg per trade is 13% of the credit on a 2-leg spread round trip, more on a condor. See the slippage table: the sign of the result can depend on it.
- In-sample grid (36 rule combos x 2 variants x 2 filters): best total Rs 116,114 (PCS VIX ON, delta 0.20, width 500, SL 2.0x, TP 65%); worst Rs -301,547. Share of grid points with positive total: 17%. The base case was fixed before looking at this grid.
- Feb-Apr 2020 (COVID crash), PCS_OFF: equity change inside the window Rs -17,336 on 10 trades touching it.
- 3-7 June 2024 (election result), PCS_OFF: equity change inside the window Rs 2,872 on 2 trades touching it.
- Feb-Apr 2020 (COVID crash), IC_OFF: equity change inside the window Rs -16,619 on 10 trades touching it.
- 3-7 June 2024 (election result), IC_OFF: equity change inside the window Rs 5,686 on 3 trades touching it.

## Data-quality handling that matters

About 6% of pre-expiry option rows (5-9% of near-the-money rows, mostly 50-step strikes with no volume) carry an NSE settlement price that violates strike monotonicity, by a median of ~45 points. They are flagged `value_suspect` in the dataset. The backtest never enters on such a strike and, when an open leg lands on one, prices that leg by interpolating between the clean neighbouring strikes and counts it (Summary sheet). The `_RAW` runs below use raw `value` everywhere, as literally specified:

- PCS VIX OFF, raw value: 277 trades, total Rs -40,168, max DD Rs -62,240 (vs Rs -45,861 with suspect handling).
- IC VIX OFF, raw value: 275 trades, total Rs -182,367, max DD Rs -197,618 (vs Rs -224,898 with suspect handling).

## Caveats you should not ignore

- 2019-2020 prices for untraded strikes are NSE theoretical settlement prices, not trades. The 2021+ rows are the ones to trust more; both are reported.
- No bid/ask in bhavcopy: slippage is an assumption. Exits on untraded legs are priced at the settlement value and counted (Summary sheet, by year).
- Stops are checked once a day at the close. An intraday gap through the stop (June 2024, March 2020) is only caught at the close, so real losses on those days can be larger than modelled.
- Capital at risk here is the full defined loss; broker margin is different and changes daily. The CAGR comparison depends entirely on this capital base.
- One position per week with up to several open at once; no position sizing, no compounding, no lot-size history (everything at 65 units).

## Sources for cost rates

- [Zerodha bulletin, STT revision from 1 Apr 2026](https://zerodha.com/marketintel/bulletin/445377/revision-in-stt-securities-transaction-tax-from-1st-april-2026)
- [Business Standard, Budget 2026 STT hike](https://www.business-standard.com/markets/news/markets-fm-hikes-stt-on-fo-trades-surprise-move-126020100888_1.html)
- [Zerodha bulletin, transaction charges from 1 Oct 2024](https://zerodha.com/marketintel/bulletin/391488/revision-in-transactions-charges-from-1st-october-2024)
- [HDFC Securities, exchange charges from 1 Oct 2024](https://www.hdfcsec.com/blog/details/revised-exchange-transaction-charges-w-e-f-1st-october-2024)
- [Zerodha support, how STT is calculated](https://support.zerodha.com/category/account-opening/resident-individual/ri-charges/articles/how-is-the-securities-transaction-tax-stt-calculated)
